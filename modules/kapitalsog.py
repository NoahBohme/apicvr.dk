import requests
import json
import re
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


project_folder = os.path.expanduser('/code/app')
load_dotenv(os.path.join(project_folder, '.env'))
APITOKEN = os.getenv("API_TOKEN")


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure Jinja2 Environment to use Bootstrap CDN
loader = FileSystemLoader("templates")
jinja_env = Environment(loader=loader)
jinja_env.globals['bootstrap'] = {
    'cdn_css': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css',
    'cdn_js': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js'
}


def show_capital_result(cvr_number: str):
    url = "http://distribution.virk.dk/registreringstekster/registreringstekst/_search"
    headers = {
        "Authorization": "Basic " + APITOKEN,
        "Content-Type": "application/json"
    }

    # Construct the request payload
    payload = {
        "size": 3000,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "cvrNummer": cvr_number
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = json.loads(response.text)

    aendring_kapital_entries = []
    hits = data.get("hits", {}).get("hits", [])
    for hit in hits:
        source = hit.get("_source", {})
        status_list = source.get("virksomhedsregistreringstatusser", [])
        if "AENDRING_KAPITAL" in status_list:
            aendring_kapital_entries.append(source)

    # Prepare the result data
    result_data = []
    for entry in aendring_kapital_entries:
        # Extract the "tekst" field
        tekst = entry.get("tekst", "")

        # Parse the HTML and format the text nicely
        soup = BeautifulSoup(tekst, "html.parser")
        formatted_text = soup.get_text()

        # Create a new entry with the formatted text
        formatted_entry = {
            "offentliggoerelseId": entry.get("offentliggoerelseId", ""),
            "registreringTidsstempel": entry.get("registreringTidsstempel", ""),
            "offentliggoerelseTidsstempel": entry.get("offentliggoerelseTidsstempel", ""),
            "cvrNummer": entry.get("cvrNummer", ""),
            "hovednavn": entry.get("hovednavn", ""),
            "formatted_tekst": formatted_text,
        }
        result_data.append(formatted_entry)

    return result_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
