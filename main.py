import os
import secrets
import time
from apis.searchcvr import *
from typing import Optional, Union
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import NoMatchFound
from app.modules.kapitalsog import show_capital_result
from app.modules.stats import init_db, log_request, get_stats

init_db()

_security = HTTPBasic()

def _verify_stats_auth(credentials: HTTPBasicCredentials = Depends(_security)):
    stats_password = os.getenv("STATS_PASSWORD", "")
    if not stats_password:
        raise HTTPException(status_code=503, detail="STATS_PASSWORD not configured")
    ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        stats_password.encode("utf-8"),
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )


class _RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        forwarded_for = request.headers.get("x-forwarded-for")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)
        raw_referer = request.headers.get("referer") or request.headers.get("referrer")
        referer = raw_referer[:500] if raw_referer else None
        log_request(request.method, request.url.path, response.status_code, elapsed_ms, ip=ip, referer=referer)
        return response


app = FastAPI(
    title="APICVR.dk",
    description="APICVR er et gratis og open source API til at søge på CVR",
    version="1.0",
    contact={
        "name": "Noah Böhme Rasmussen",
        "url": "https://noahbohme.com",
        "email": "apicvr@noahbohme.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://raw.githubusercontent.com/NoahBohme/apicvr.dk/master/LICENSE",
    },
)

templates = Jinja2Templates(directory="frontend/templates")

app.add_middleware(_RequestLogMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _base_context(request: Request) -> dict:
    base_url = str(request.base_url).rstrip("/")
    try:
        docs_url = request.url_for("swagger_ui_html")
    except NoMatchFound:
        docs_url = f"{base_url}/docs"
    return {"request": request, "base_url": base_url, "docs_url": docs_url}


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("/homepage.html", _base_context(request))


@app.get("/en/")
async def home_en(request: Request):
    return templates.TemplateResponse("/homepage_en.html", _base_context(request))


@app.get("/da/mcp")
async def mcp_da(request: Request):
    return templates.TemplateResponse("/mcp_da.html", _base_context(request))


@app.get("/en/mcp")
async def mcp_en(request: Request):
    return templates.TemplateResponse("/mcp_en.html", _base_context(request))


@app.get("/mcp")
async def mcp_redirect():
    return RedirectResponse("/da/mcp", status_code=301)

@app.get("/da/search/")
async def search_da(request: Request):
    return templates.TemplateResponse("/sogning.html", {"request": request})


@app.get("/en/company/{cvrNumber}")
async def company_en(request: Request, cvrNumber: str):
    try:
        cvr_int = int(cvrNumber)
    except ValueError:
        info = {"error": "INVALID_CVR", "status": 400, "message": "CVR number must consist of 8 digits."}
    else:
        info = search_cvr_api(cvr_int)
    return templates.TemplateResponse(
        "/virksomhed_en.html",
        {"request": request, "cvrNumber": cvrNumber, "info": info},
    )


@app.get("/da/virksomhed/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):
    try:
        cvr_int = int(cvrNumber)
    except ValueError:
        info = {"error": "INVALID_CVR", "status": 400, "message": "CVR-nummer skal bestå af 8 cifre."}
    else:
        info = search_cvr_api(cvr_int)

    return templates.TemplateResponse(
        "/virksomhed.html",
        {"request": request, "cvrNumber": cvrNumber, "info": info},
    )


@app.get("/api/v1/{cvrNumber}")
def read_root(cvrNumber: int):
    return search_cvr_api(cvrNumber)

@app.get("/api/v1/search/company/{companyName}")
def search_company(companyName: str, limit: int = 100):
    return search_cvr_by_name(companyName, limit=limit)

@app.get("/api/v1/fuzzy_search/company/{companyName}")
def search_company_fuzzy(companyName: str, limit: int = 100):
    return search_cvr_by_fuzzy_name(companyName, limit=limit)

@app.get("/api/v1/email/{email}")
def search_email(email: str, limit: int = 100):
    return search_cvr_by_email(email, limit=limit)

@app.get("/api/v1/email_domain/{domain}")
def search_email_domain(domain: str, limit: int = 100):
    return search_cvr_by_email_domain(domain, limit=limit)

@app.get("/api/v1/phone/{phone}")
def search_phone(phone: str, limit: int = 100):
    return search_cvr_by_phone(phone, limit=limit)


@app.get("/api/v1/search/address")
def search_address(address: str, postal_code: str = None, limit: int = 100):
    return search_cvr_by_address(address, postal_code, limit=limit)


@app.get("/api/v1/search")
def search(name: Optional[str] = None, cvr: Optional[int] = None, limit: int = 100):
    if not name and cvr is None:
        raise HTTPException(status_code=400, detail="At least one of 'name' or 'cvr' must be provided.")
    return search_cvr_combined(name=name, cvr=cvr, limit=limit)



# Search in registeringshistorik after capital raise

@app.get("/da/kapitalsog/")
async def search_da(request: Request):
    return templates.TemplateResponse("/kapitalsog.html", {"request": request})


@app.get("/da/kapitalindsigt/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):
    return templates.TemplateResponse("/kapitalresultat.html", {"request": request, "data": show_capital_result(cvrNumber)})


@app.get("/stats")
async def stats_dashboard(request: Request, _: bool = Depends(_verify_stats_auth)):
    return templates.TemplateResponse("/stats.html", {"request": request, "stats": get_stats()})


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /stats\n"
        "Disallow: /da/search/\n"
        "\n"
        "Sitemap: https://apicvr.dk/sitemap.xml\n"
    )


@app.get("/sitemap.xml")
async def sitemap():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://apicvr.dk/</loc>
    <xhtml:link rel="alternate" hreflang="da" href="https://apicvr.dk/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://apicvr.dk/en/"/>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://apicvr.dk/en/</loc>
    <xhtml:link rel="alternate" hreflang="da" href="https://apicvr.dk/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://apicvr.dk/en/"/>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://apicvr.dk/da/mcp</loc>
    <xhtml:link rel="alternate" hreflang="da" href="https://apicvr.dk/da/mcp"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://apicvr.dk/en/mcp"/>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://apicvr.dk/en/mcp</loc>
    <xhtml:link rel="alternate" hreflang="da" href="https://apicvr.dk/da/mcp"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://apicvr.dk/en/mcp"/>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://apicvr.dk/da/kapitalsog/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""
    return Response(content=content, media_type="application/xml")
