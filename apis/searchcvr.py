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


# Making a POST Request to system-til-system-adgang
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

    # Formatting the response to json
    jsonResponse = response.json()

    # If the response is empty, return not found
    if (jsonResponse['hits']['total'] == 0):

        return {"error": "NOT_FOUND"}

    # If the response is not empty, return the response
    else:

        # Find company name
        companyName = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']

        # Find company start date
        startDate = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[2] + "/" + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[
            1] + " - " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['stiftelsesDato'].split('-')[0]

        # Check if company has a end date

        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'] != None):
            endDate = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[2] + "/" + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[
                1] + " - " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['livsforloeb'][0]['periode']['gyldigTil'].split('-')[0]
        else:
            endDate = None

        # Company status
        companyStatus = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed']['virksomhedMetadata']['sammensatStatus']

        # Find the company type

        companyFormationTypeShort = jsonResponse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['kortBeskrivelse']

        companyFormationTypeLong = jsonResponse['hits']['hits'][0]['_source'][
            'Vrvirksomhed']['virksomhedMetadata']['nyesteVirksomhedsform']['langBeskrivelse']

        # Find company field of work
        businessType = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchetekst']

        # Find the ID of field of work
        businessTypeID = int(jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteHovedbranche']['branchekode'])

        # Address of company
        addressStreet = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteBeliggenhedsadresse']['vejnavn']

        # Address street number from
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra'] == None):
            addressStreetNumberFrom = ""
        else:
            addressStreetNumberFrom = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra']

        # Address street number to
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil'] == None):
            addressStreetNumberTo = ""
        else:
            addressStreetNumberTo = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerTil']

        # Address Street Letter From
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra'] == None):
            addressStreetLetterFrom = ""
        else:
            addressStreetLetterFrom = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavFra']

        # Address Street Letter To
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil'] == None):
            addressStreetLetterTo = ""
        else:
            addressStreetLetterTo = jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['bogstavTil']

        # Create Combined Address
        combinedAddress = addressStreet + " " + \
            str(addressStreetNumberFrom)

        # Street Number to and street lettes
        if (addressStreetNumberTo != ""):
            combinedAddress = combinedAddress + \
                "-" + str(addressStreetNumberTo)

        if (addressStreetLetterFrom != ""):
            combinedAddress = combinedAddress + addressStreetLetterFrom

        if (addressStreetLetterTo != ""):
            combinedAddress = combinedAddress + "-" + addressStreetLetterTo

            # Level of address
        if (jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['etage'] != None):
            combinedAddress = combinedAddress + ", " + jsonResponse['hits']['hits'][0]['_source']['Vrvirksomhed'][
                'virksomhedMetadata']['nyesteBeliggenhedsadresse']['etage']
        else:
            combinedAddress = combinedAddress

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

        # Contact info

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

        # Return data to API
        return {
            "vat": cvrNumber,
            "name": companyName,
            "address": combinedAddress,
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
            "version": 1,

        }
