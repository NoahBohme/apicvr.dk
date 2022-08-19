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


@app.get("/api/{cvrNumber}")
def read_root(cvrNumber: int):

    return searchcvrAPI(cvrNumber)
