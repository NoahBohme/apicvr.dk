import os
import requests
import json
import re
from dotenv import load_dotenv
from . import model
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
class AccessorService :

    def __init__(self,db:Session):
        self.db = db
        return
    
    def get_all(self):
        return self.db.query(model.Accessor).all()
    
    def get_counts(self):
        return self.db.query(model.Accessor).count()
    
    def create_accessor(self,request:Request):
        client_ip = request.client.host
        origin = request.headers.get("origin")
        user_agent = request.headers.get("user-agent")
        method = request.method
        url = str(request.url)

        try:
           geo_resp = requests.get(f"https://ipapi.co/{client_ip}/country_name/", timeout=2)
           country = geo_resp.text.strip()
           pass
        except Exception:
           country = None
           pass

        accessor = model.Accessor(
        ip=client_ip,
        origin=origin,
        browser=user_agent,
        method=method,
        url=url,
        country=country )

        self.db.add(accessor)
        self.db.commit()
        self.db.refresh(accessor)
        return accessor
        
