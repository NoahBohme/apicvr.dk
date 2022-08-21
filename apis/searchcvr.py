import os
import requests
import json
import re
from dotenv import load_dotenv

# Load .env file

project_folder = os.path.expanduser('/code/app')
load_dotenv(os.path.join(project_folder, '.env'))
APITOKEN = os.getenv("API_TOKEN")

# START POST

url = "http://distribution.virk.dk/cvr-permanent/virksomhed/_search"


def searchcvrAPI(cvrNumber):

    payload = json.dumps({
        "_source": [
            "Vrvirksomhed.virksomhedMetadata"
        ],
        "query": {
            "term": {
                "Vrvirksomhed.cvrNummer": cvrNumber
            }
        }
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # POST END

    jsonResonse = response.json()

    if (jsonResonse['hits']['total'] == 0):

        return {"error": "NOT_FOUND"}

    else:
        companyName = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']

        formationDate = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato']

        companyStatus = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['sammensatStatus']

        # Dansk = Virksomhedstype
        companyFormationTypeLong = jsonResonse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['langBeskrivelse']

        companyFormationTypeShort = jsonResonse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['kortBeskrivelse']

        businessType = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchetekst']

        businessTypeID = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchekode']

        addressStreet = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteBeliggenhedsadresse']['vejnavn']

        # Address Street Numer From
        if (jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra'] == None):
            addressStreetNumberFrom = ""
        else:
            addressStreetNumberFrom = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra']

        # Address Street Number To
        if (jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil'] == None):
            adressStreetNumberTo = ""
        else:
            adressStreetNumberTo = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil']

        # Address Street Letter From
        if (jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra'] == None):
            adressStreetLetterFrom = ""
        else:
            adressStreetLetterFrom = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra']

        # Adress Street Letter To
        if (jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil'] == None):
            adressStreetLetterTo = ""
        else:
            adressStreetLetterTo = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil']

        # Combined Address

        combinedAdress = addressStreet + " " + str(addressStreetNumberFrom)

        # Street Number to and street lettes
        if (adressStreetNumberTo != ""):
            combinedAdress = combinedAdress + "-" + str(adressStreetNumberTo)

        if (adressStreetLetterFrom != ""):
            combinedAdress = combinedAdress + adressStreetLetterFrom

        if (adressStreetLetterTo != ""):
            combinedAdress = combinedAdress + "-" + adressStreetLetterTo

        # Overall contact info

        contactinfo = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteKontaktoplysninger']

        # Phone number
        phone = str(re.findall(r'\b\d{8}\b', str(contactinfo))).replace(
            "[", "").replace("]", "").replace("'", "")
        if (phone == ""):
            phone = None

        # Email info
        email = str(re.findall(r'\b[\w.-]+@[\w.-]+\b',
                    str(contactinfo))).replace("['", "").replace("']", "")

        # Website info of the company
        website = str(re.findall(r'\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b', str(
            contactinfo))).replace("[", "").replace("]", "").replace("'", "")

        if (website == ""):
            website = None

        # Data about Employees
        try:
            employees = jsonResonse['hits']['hits'][0]['_source'][
                'Vrvirksomhed']['virksomhedMetadata']['nyesteErstMaanedsbeskaeftigelse']['antalAnsatte']
        except:
            employees = None

        # Data about a company about a bankruptcy
        try:
            if (jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteStatus']['kreditoplysningtekst'] == "Konkurs"):
                bankrupt = True
            else:
                bankrupt = False
        except:
            bankrupt = False

        # Data about a company if it's merged

        try:
            endData = jsonResonse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteNavn']['periode']['gyldigTil']
        except:
            endData = None

        return {"cvr": cvrNumber, "name": companyName, "formationdate": formationDate, "status": companyStatus, "companytype": companyFormationTypeLong, "companytypeshort": companyFormationTypeShort, "industry": businessType, "industryid": businessTypeID, "address": combinedAdress, "phone": phone, "email": email, "website": website, "employees": employees, "bankrupt": bankrupt, "enddate": endData}
