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


# Visma Credit Rating API

def vismaRatingAPI(cvrNumber):
    url = "https://api.vismarating.com/credit/" + str(cvrNumber)

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if (response.status_code == 200):
        return (response.json()['credit_score'], response.json()['credit_days'])
    else:
        return (None, None)


def searchcvrAPI(cvrNumber):

    payload = json.dumps({
        "_source": [
            "Vrvirksomhed"
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

    jsonResponse = response.json()

    if (jsonResponse['hits']['total'] == 0):

        return {"error": "NOT_FOUND"}

    else:
        companyName = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']

        # Formation date

        startDate = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[2] + "/" + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[
            1] + " - " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[0]

        companyStatus = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['sammensatStatus']

        # End date

        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'] != None):
            endDate = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[2] + "/" + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[
                1] + " - " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[0]
        else:
            endDate = None

        # Dansk = Virksomhedstype
        companyFormationTypeLong = jsonResponse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['langBeskrivelse']

        companyFormationTypeShort = jsonResponse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['kortBeskrivelse']

        businessType = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchetekst']

        businessTypeID = int(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchekode'])

        addressStreet = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteBeliggenhedsadresse']['vejnavn']

        # Address Street Numer From
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra'] == None):
            addressStreetNumberFrom = ""
        else:
            addressStreetNumberFrom = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra']

        # Address Street Number To
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil'] == None):
            adressStreetNumberTo = ""
        else:
            adressStreetNumberTo = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil']

        # Address Street Letter From
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra'] == None):
            adressStreetLetterFrom = ""
        else:
            adressStreetLetterFrom = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra']

        # Adress Street Letter To
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil'] == None):
            adressStreetLetterTo = ""
        else:
            adressStreetLetterTo = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil']

        # Combined Address

        combinedAdress = addressStreet + " " + \
            str(addressStreetNumberFrom)

        # Street Number to and street lettes
        if (adressStreetNumberTo != ""):
            combinedAdress = combinedAdress + "-" + str(adressStreetNumberTo)

        if (adressStreetLetterFrom != ""):
            combinedAdress = combinedAdress + adressStreetLetterFrom

        if (adressStreetLetterTo != ""):
            combinedAdress = combinedAdress + "-" + adressStreetLetterTo

            # Level of address
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['etage'] != None):
            combinedAdress = combinedAdress + ", " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['etage']
        else:
            combinedAdress = combinedAdress

        # Zipcode

        addressZipcode = str(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteBeliggenhedsadresse']['postnummer'])

        # City

        addressCity = str(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteBeliggenhedsadresse']['postdistrikt'])

        # City name
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bynavn'] != None):
            addressCityName = str(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bynavn'])
        else:
            addressCityName = None

        # addressCo

        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['conavn'] != None):
            addressCo = str(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['conavn'])
        else:
            addressCo = None

        # Advertisement protection

        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['reklamebeskyttet'] != None):
            advertisementProtection = jsonResponse['hits']['hits'][0]['_source'][
                'Vrvirksomhed']['reklamebeskyttet']
        else:
            advertisementProtection = None

        # Overall contact info

        contactinfo = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteKontaktoplysninger']

        # Phone number
        phone = str(re.findall(r'\b\d{8}\b', str(contactinfo))).replace(
            "[", "").replace("]", "").replace("'", "")
        if (phone == ""):
            phone = None

        # Fax

        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['telefaxNummer'] == ""):
            fax = str(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['telefaxNummer']).replace(
                "[", "").replace("]", "").replace("'", "")
        else:
            fax = None

        # Email info
        if (str(re.findall(r'\b[\w.-]+@[\w.-]+\b',
                           str(contactinfo))).replace("['", "").replace("']", "") == "[]"):
            email = None
        else:
            email = str(re.findall(r'\b[\w.-]+@[\w.-]+\b',
                                   str(contactinfo))).replace("['", "").replace("']", "")

        # Website info of the company
        website = str(re.findall(r'\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b', str(
            contactinfo))).replace("[", "").replace("]", "").replace("'", "")

        if (website == ""):
            website = None

        # Data about Employees
        try:
            employees = jsonResponse['hits']['hits'][0]['_source'][
                'Vrvirksomhed']['virksomhedMetadata']['nyesteErstMaanedsbeskaeftigelse']['antalAnsatte']
        except:
            employees = None

        # Formcode
        formcode = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteVirksomhedsform']['virksomhedsformkode']

        # Data about a company about a bankruptcy
        try:
            if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteStatus']['kreditoplysningtekst'] == "Konkurs"):
                bankrupt = True
            else:
                bankrupt = False
        except:
            bankrupt = False

        try:
            endData = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteNavn']['periode']['gyldigTil']
        except:
            endData = None

        return {
            "vat": cvrNumber,
            "name": companyName,
            "address": combinedAdress,
            "zipcode": addressZipcode,
            "city": addressCity,
            "cityname": addressCityName,
            "protected": advertisementProtection,
            "phone": phone,
            "email": email,
            "fax": fax,
            "startdate": startDate,
            "enddate": endDate,
            "employees": employees,
            "addressco": addressCo,
            "industrycode": businessTypeID,
            "industrydesc": businessType,
            "companycode": formcode,
            "companydesc": companyFormationTypeLong,
            "bankrupt": bankrupt,
            "status": companyStatus,
            "companytypeshort": companyFormationTypeShort,
            "website": website,
            "creditrating": vismaRatingAPI(cvrNumber)[0],
            "creditratingdays": vismaRatingAPI(cvrNumber)[1],
            "version": 1,

        }
