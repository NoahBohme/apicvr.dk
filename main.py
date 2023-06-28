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


# Search in registeringshistorik after capital raise

@app.get("/da/kapitalsog/{cvrNumber}")
async def search_da(request: Request, cvrNumber: str):
    return templates.TemplateResponse("/kapitalsog.html", {"request": request})


@app.get("/da/kapitalindsigt/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):
    return templates.TemplateResponse("/kapitalresultat.html", {"request": request, "data": show_capital_result(cvrNumber)})
