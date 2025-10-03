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
    if response.status_code != 200:
        return {
            "error": "HTTP_ERROR",
            "status": response.status_code,
            "message": response.text,
        }

    try:
        json_response = response.json()
    except ValueError:
        return {
            "error": "INVALID_RESPONSE",
            "status": response.status_code,
            "message": response.text,
        }

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

    components = _parse_address_components(cleaned_address)

    filters = []

    if postal_code:
        trimmed_postal = postal_code.strip()
        if trimmed_postal:
            numeric_postal_code = int(trimmed_postal) if trimmed_postal.isdigit() else trimmed_postal
            filters.append({
                "term": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.postnummer": numeric_postal_code
                }
            })

    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    queries = []

    exact_query = _build_exact_address_query(cleaned_address, filters)
    if exact_query:
        queries.append(exact_query)

    structured_query = _build_structured_address_query(components, filters)
    if structured_query:
        queries.append(structured_query)

    queries.append(_build_fuzzy_address_query(cleaned_address, filters))

    for query in queries:
        payload = json.dumps(query)
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Error querying Elasticsearch: {response.status_code}, {response.text}")

        json_response = response.json()
        companies = _extract_companies_from_hits(json_response)

        if companies:
            return companies

    return []


def _extract_companies_from_hits(json_response: dict) -> list:
    companies = []
    for hit in json_response.get('hits', {}).get('hits', []):
        company = hit['_source'].get('Vrvirksomhed', {})
        cvr_number = company.get('cvrNummer')
        if not cvr_number:
            continue
        formatted_company = format_company_data(company, cvr_number)
        companies.append(formatted_company)
    return companies


def _build_exact_address_query(cleaned_address: str, filters: list) -> Optional[dict]:
    if not cleaned_address:
        return None

    bool_query = {
        "must": [
            {
                "match_phrase": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.adressebetegnelse": cleaned_address
                }
            }
        ]
    }

    if filters:
        bool_query["filter"] = filters

    return {
        "_source": ["Vrvirksomhed"],
        "query": {"bool": bool_query},
        "size": 100
    }


def _build_structured_address_query(components: dict, filters: list) -> Optional[dict]:
    street = components.get("street")
    number = components.get("number")
    letter = components.get("letter")

    if not street or number is None:
        return None

    must_clauses = [
        {
            "match_phrase": {
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.vejnavn": street
            }
        },
        {
            "term": {
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.husnummerFra": number
            }
        }
    ]

    if letter:
        must_clauses.append({
            "term": {
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.bogstavFra": letter
            }
        })

    bool_query = {"must": must_clauses}

    if filters:
        bool_query["filter"] = filters

    return {
        "_source": ["Vrvirksomhed"],
        "query": {"bool": bool_query},
        "size": 100
    }


def _build_fuzzy_address_query(cleaned_address: str, filters: list) -> dict:
    bool_query = {
        "must": [
            {
                "multi_match": {
                    "query": cleaned_address,
                    "fields": [
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.adressebetegnelse^3",
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.fritekst^2",
                        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.vejnavn"
                    ],
                    "fuzziness": "AUTO",
                    "type": "best_fields",
                    "operator": "or"
                }
            }
        ]
    }

    if filters:
        bool_query["filter"] = filters

    return {
        "_source": ["Vrvirksomhed"],
        "query": {"bool": bool_query},
        "size": 100
    }


def _parse_address_components(address: str) -> dict:
    components = {
        "street": None,
        "number": None,
        "letter": None,
    }

    main_part, _, _ = address.partition(',')
    main_part = main_part.strip()

    if not main_part:
        return components

    match = re.match(r"^(?P<street>[^0-9]+?)\s+(?P<number>\d+)(?:\s*(?P<letter>[A-Za-z]))?$", main_part)

    if not match:
        return components

    street = match.group('street').strip()
    number = match.group('number')
    raw_letter = match.group('letter')
    letter = raw_letter.upper() if raw_letter else None

    components["street"] = street if street else None
    components["number"] = int(number) if number else None
    components["letter"] = letter

    return components


# Format company data
def format_company_data(company: dict, cvr_number: str) -> dict:
    """Convert raw company data to the API response schema."""
    metadata = company.get('virksomhedMetadata') or {}
    hovedbranche = metadata.get('nyesteHovedbranche') or {}
    virksomhedsform = metadata.get('nyesteVirksomhedsform') or {}

    livsforloeb = company.get('livsforloeb') or []
    first_period = {}
    if livsforloeb and isinstance(livsforloeb[0], dict):
        first_period = livsforloeb[0].get('periode') or {}

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
        "startdate": get_formatted_date(metadata.get('stiftelsesDato')),
        "enddate": get_formatted_date(first_period.get('gyldigTil')),
        "employees": get_employees(company),
        "addressco": get_address_field(company, 'conavn'),
        "industrycode": hovedbranche.get('branchekode'),
        "industrydesc": hovedbranche.get('branchetekst'),
        "companycode": virksomhedsform.get('virksomhedsformkode'),
        "companydesc": virksomhedsform.get('langBeskrivelse'),
        "bankrupt": is_bankrupt(company),
        "status": metadata.get('sammensatStatus'),
        "companytypeshort": virksomhedsform.get('kortBeskrivelse'),
        "website": get_website(company),
        "version": 1
    }
    return company_data

# Get company name
def get_company_name(company):
    metadata = company.get('virksomhedMetadata') or {}
    navn = metadata.get('nyesteNavn') or {}
    return navn.get('navn')

# Get combined address
def get_combined_address(company):
    metadata = company.get('virksomhedMetadata') or {}
    address = metadata.get('nyesteBeliggenhedsadresse') or {}

    vejnavn = address.get('vejnavn', '')
    if not vejnavn:
        return None

    combined_address = f"{vejnavn} {address.get('husnummerFra', '')}".rstrip()

    if address.get('husnummerTil'):
        combined_address += f"-{address['husnummerTil']}"

    combined_address += address.get('bogstavFra', '') or ''

    if address.get('bogstavTil'):
        combined_address += f"-{address['bogstavTil']}"

    combined_address += f", {address['etage']}" if address.get('etage') else ''

    return combined_address


# Get specific field from address
def get_address_field(company, field):
    metadata = company.get('virksomhedMetadata') or {}
    address = metadata.get('nyesteBeliggenhedsadresse') or {}
    return address.get(field)

# Get formatted date
def get_formatted_date(date):
    if date is None:
        return None
    parts = date.split('-')
    return f"{parts[2]}/{parts[1]} - {parts[0]}"

# Get phone number
def get_phone_number(company):
    metadata = company.get('virksomhedMetadata') or {}
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
    phone = re.findall(r'\b\d{8}\b', str(contact_info))
    return phone[0] if phone else None

# Get email
def get_email(company):
    metadata = company.get('virksomhedMetadata') or {}
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
    email = re.findall(r'\b[\w.-]+@[\w.-]+\b', str(contact_info))
    return email[0] if email else None

# Get website
def get_website(company):
    metadata = company.get('virksomhedMetadata') or {}
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
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
