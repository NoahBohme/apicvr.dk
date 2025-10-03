import os
import requests
import json
import re
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
# Falls back to the current working directory if `.env` is not found
load_dotenv()
APITOKEN = os.getenv("API_TOKEN", "")


# API endpoint
url = "http://distribution.virk.dk/cvr-permanent/virksomhed/_search"

# Make a POST request to system-til-system-adgang
def search_cvr_api(cvr_number: int) -> dict:
    """Look up company information based on CVR number."""
    payload = json.dumps({
        "_source": ["Vrvirksomhed"],
        "query": {
            "term": {
                "Vrvirksomhed.cvrNummer": cvr_number
            }
        }
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    json_response = response.json()

    if json_response['hits']['total'] == 0:
        return {"error": "NOT_FOUND"}
    else:
        company = json_response['hits']['hits'][0]['_source']['Vrvirksomhed']
        return format_company_data(company, cvr_number)

def search_cvr_by_name(company_name: str) -> list:
    """Search for companies matching the provided name."""
    payload = json.dumps({
        "_source": ["Vrvirksomhed"],
        "query": {
            "match_phrase_prefix": {
                "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": company_name
            }
        },
        "size": 100  # Adjust the size as needed
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    json_response = response.json()

    
    companies = []
    for hit in json_response['hits']['hits']:
        company = hit['_source']['Vrvirksomhed']
        cvr_number = company['cvrNummer']
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


def search_cvr_by_fuzzy_name(company_name: str) -> list:
    """Return companies matching the name using fuzzy search."""
    # Define the payload for the multi_match query
    payload = json.dumps({
        "_source": ["Vrvirksomhed"],
        "query": {
            "multi_match": {
                "query": company_name,
                "fields": ["Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn^2"],
                "fuzziness": "AUTO"
            }
        },
        "size": 100
    })

    # Set up headers with authorization and content type
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    # Send the POST request to Elasticsearch
    response = requests.post(url, headers=headers, data=payload, timeout=10)

    # Handle potential errors
    if response.status_code != 200:
        raise Exception(f"Error querying Elasticsearch: {response.status_code}, {response.text}")

    # Parse the JSON response
    json_response = response.json()

    # Extract companies from the response
    companies = []
    for hit in json_response.get('hits', {}).get('hits', []):
        company = hit['_source'].get('Vrvirksomhed', {})
        cvr_number = company.get('cvrNummer', None)

        # Safely extract nested fields
        metadata = company.get('virksomhedMetadata', {})
        nyeste_navn = metadata.get('nyesteNavn', {})
        hovedbranche = metadata.get('nyesteHovedbranche', {})

        # Ensure hovedbranche is a dictionary before accessing it
        if hovedbranche is None:
            hovedbranche = {}

        formatted_company = {
            "name": nyeste_navn.get('navn', "Unknown"),  # Safely get nested 'navn'
            "cvr_number": cvr_number,
            "industrycode": hovedbranche.get('branchekode', "Unknown"),
            "industrytext": hovedbranche.get('branchetekst', "Unknown"),
        }

        companies.append(formatted_company)

    return companies



def search_cvr_by_email(email: str) -> list:
    """Find companies registered with the given email address."""
    payload = json.dumps({
        "_source": ["*"],
        "query": {
            "match": {
                "Vrvirksomhed.elektroniskPost.kontaktoplysning": email
            }
        },
        "size": 100  # Adjust the size as needed
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    json_response = response.json()

    companies = []
    for hit in json_response['hits']['hits']:
        company = hit['_source']['Vrvirksomhed']
        cvr_number = company['cvrNummer']
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


def search_cvr_by_email_domain(email_domain: str) -> list:
    """Search for companies by matching email domain."""
    email = "@" + email_domain
    payload = json.dumps({
        "_source": ["*"],
        "query": {
            "match": {
                "Vrvirksomhed.elektroniskPost.kontaktoplysning": email
            }
        },
        "size": 100  # Adjust the size as needed
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    json_response = response.json()

    companies = []
    for hit in json_response['hits']['hits']:
        company = hit['_source']['Vrvirksomhed']
        cvr_number = company['cvrNummer']
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


def search_cvr_by_phone(phone_number: str) -> list:
    """Locate companies by phone number."""
    payload = json.dumps({
        "_source": ["*"],
        "query": {
            "match": {
                "Vrvirksomhed.telefonNummer.kontaktoplysning": phone_number
            }
        },
        "size": 100  # Adjust the size as needed
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    json_response = response.json()

    companies = []
    for hit in json_response['hits']['hits']:
        company = hit['_source']['Vrvirksomhed']
        cvr_number = company['cvrNummer']
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


def search_cvr_by_address(address: str, postal_code: Optional[str] = None) -> list:
    """Return companies registered on the provided street address."""
    cleaned_address = address.strip()
    if not cleaned_address:
        return []

    bool_query = {
        "must": [
            {
                "multi_match": {
                    "query": cleaned_address,
                    "type": "phrase",
                    "fields": [
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.fritekst^3",
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.adressebetegnelse^2",
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.vejnavn"
                    ]
                }
            }
        ],
    }

    filters = []

    numeric_postal_code = None
    if postal_code:
        trimmed_postal = postal_code.strip()
        if trimmed_postal:
            numeric_postal_code = int(trimmed_postal) if trimmed_postal.isdigit() else trimmed_postal
            filters.append({
                "term": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.postnummer": numeric_postal_code
                }
            })

    if filters:
        bool_query["filter"] = filters

    payload = json.dumps({
        "_source": ["Vrvirksomhed"],
        "query": {
            "bool": bool_query
        },
        "size": 100
    })

    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Error querying Elasticsearch: {response.status_code}, {response.text}")

    json_response = response.json()

    companies = []
    for hit in json_response.get('hits', {}).get('hits', []):
        company = hit['_source'].get('Vrvirksomhed', {})
        cvr_number = company.get('cvrNummer')
        if not cvr_number:
            continue
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


# Format company data
def format_company_data(company: dict, cvr_number: str) -> dict:
    """Convert raw company data to the API response schema."""
    company_data = {
        "vat": cvr_number,
        "name": get_company_name(company),
        "address": get_combined_address(company),
        "zipcode": get_address_field(company, 'postnummer'),
        "city": get_address_field(company, 'postdistrikt'),
        "cityname": get_address_field(company, 'bynavn'),
        "protected": company.get('reklamebeskyttet'),
        "phone": get_phone_number(company),
        "email": get_email(company),
        "fax": company.get('telefaxNummer'),
        "startdate": get_formatted_date(company['virksomhedMetadata']['stiftelsesDato']),
        "enddate": get_formatted_date(company['livsforloeb'][0]['periode']['gyldigTil']) if 'gyldigTil' in company['livsforloeb'][0]['periode'] else None,
        "employees": get_employees(company),
        "addressco": get_address_field(company, 'conavn'),
        "industrycode": company['virksomhedMetadata']['nyesteHovedbranche']['branchekode'],
        "industrydesc": company['virksomhedMetadata']['nyesteHovedbranche']['branchetekst'],
        "companycode": company['virksomhedMetadata']['nyesteVirksomhedsform']['virksomhedsformkode'],
        "companydesc": company['virksomhedMetadata']['nyesteVirksomhedsform']['langBeskrivelse'],
        "bankrupt": is_bankrupt(company),
        "status": company['virksomhedMetadata']['sammensatStatus'],
        "companytypeshort": company['virksomhedMetadata']['nyesteVirksomhedsform']['kortBeskrivelse'],
        "website": get_website(company),
        "version": 1
    }
    return company_data

# Get company name
def get_company_name(company):
    return company['virksomhedMetadata']['nyesteNavn']['navn']

# Get combined address
def get_combined_address(company):
    address = company['virksomhedMetadata']['nyesteBeliggenhedsadresse']
    combined_address = f"{address['vejnavn']} {address.get('husnummerFra', '')}"

    if address.get('husnummerTil'):
        combined_address += f"-{address['husnummerTil']}"

    combined_address += address.get('bogstavFra', '') or ''

    if address.get('bogstavTil'):
        combined_address += f"-{address['bogstavTil']}"

    combined_address += f", {address['etage']}" if address.get('etage') else ''

    return combined_address


# Get specific field from address
def get_address_field(company, field):
    address = company['virksomhedMetadata']['nyesteBeliggenhedsadresse']
    return address.get(field)

# Get formatted date
def get_formatted_date(date):
    if date is None:
        return None
    parts = date.split('-')
    return f"{parts[2]}/{parts[1]} - {parts[0]}"

# Get phone number
def get_phone_number(company):
    contact_info = company['virksomhedMetadata']['nyesteKontaktoplysninger']
    phone = re.findall(r'\b\d{8}\b', str(contact_info))
    return phone[0] if phone else None

# Get email
def get_email(company):
    contact_info = company['virksomhedMetadata']['nyesteKontaktoplysninger']
    email = re.findall(r'\b[\w.-]+@[\w.-]+\b', str(contact_info))
    return email[0] if email else None

# Get website
def get_website(company):
    contact_info = company['virksomhedMetadata']['nyesteKontaktoplysninger']
    website = re.findall(r'\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b', str(contact_info))
    return website[0] if website else None

# Get number of employees
def get_employees(company):
    metadata = company.get('virksomhedMetadata', {})
    erst_maaned_beskaeftigelse = metadata.get('nyesteErstMaanedsbeskaeftigelse')
    if erst_maaned_beskaeftigelse:
        return erst_maaned_beskaeftigelse.get('antalAnsatte')
    return None
# Check if the company is bankrupt
def is_bankrupt(company):
    metadata = company.get('virksomhedMetadata')
    if metadata:
        nyeste_status = metadata.get('nyesteStatus')
        if nyeste_status:
            return nyeste_status.get('kreditoplysningtekst') == "Konkurs"
    return False
