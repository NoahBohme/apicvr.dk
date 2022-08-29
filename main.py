from apis.searchcvr import *
from typing import Union
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, Request

app = FastAPI()

templates = Jinja2Templates(directory="frontend/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("/homepage.html", {"request": request})


@app.get("/da/search/")
async def search_da(request: Request):
    return templates.TemplateResponse("/sogning.html", {"request": request})


@app.get("/da/virksomhed/{cvrNumber}")
async def company_frontned(request: Request, cvrNumber: str):

    return templates.TemplateResponse("/virksomhed.html", {"request": request, "cvrNumber": cvrNumber, "info": searchcvrAPI(cvrNumber)})


@app.get("/api/v1/{cvrNumber}")
def read_root(cvrNumber: int):

    return searchcvrAPI(cvrNumber)
