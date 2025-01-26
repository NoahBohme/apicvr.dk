from apis.searchcvr import *
from typing import Union
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from app.modules.kapitalsog import show_capital_result

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("/homepage.html", {"request": request})

@app.get("/da/search/")
async def search_da(request: Request):
    return templates.TemplateResponse("/sogning.html", {"request": request})


@app.get("/da/virksomhed/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):
    return templates.TemplateResponse("/virksomhed.html", {"request": request, "cvrNumber": cvrNumber, "info": search_cvr_api(cvrNumber)})


@app.get("/api/v1/{cvrNumber}")
def read_root(cvrNumber: int):
    return search_cvr_api(cvrNumber)

@app.get("/api/v1/search/company/{companyName}")
def search_company(companyName: str):
    return search_cvr_by_name(companyName)

@app.get("/api/v1/fuzzy_search/company/{companyName}")
def search_company_fuzzy(companyName: str):
    return search_cvr_by_fuzzy_name(companyName)

@app.get("/api/v1/email/{email}")
def search_email(email: str):
    return search_cvr_by_email(email)

@app.get("/api/v1/email_domain/{domain}")
def search_email_domain(domain: str):
    return search_cvr_by_email(domain)

@app.get("/api/v1/phone/{phone}")
def search_phone(phone: str):
    return search_cvr_by_phone(phone)



# Search in registeringshistorik after capital raise

@app.get("/da/kapitalsog/")
async def search_da(request: Request):
    return templates.TemplateResponse("/kapitalsog.html", {"request": request})


@app.get("/da/kapitalindsigt/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):
    return templates.TemplateResponse("/kapitalresultat.html", {"request": request, "data": show_capital_result(cvrNumber)})
