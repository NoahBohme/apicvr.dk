import os
import requests
import json
import re
from dotenv import load_dotenv

# Load .env file
project_folder = os.path.expanduser('/code/app')
load_dotenv(os.path.join(project_folder, '.env'))
APITOKEN = os.getenv("API_TOKEN")
APITOKEN = "TkJSX1NvbHV0aW9uc19DVlJfSV9TS1lFTjozN2U5Mzc5Yi02YjVhLTQwNTYtOTE5Yi0zZGUwMmZmMzEzMjc"


# API endpoint
url = "http://distribution.virk.dk/cvr-permanent/virksomhed/_search"

# Make a POST request to system-til-system-adgang
def search_cvr_api(cvr_number):
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

    response = requests.request("POST", url, headers=headers, data=payload)
    json_response = response.json()

    if json_response['hits']['total'] == 0:
        return {"error": "NOT_FOUND"}
    else:
        company = json_response['hits']['hits'][0]['_source']['Vrvirksomhed']
        return format_company_data(company, cvr_number)

# Format company data
def format_company_data(company, cvr_number):
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