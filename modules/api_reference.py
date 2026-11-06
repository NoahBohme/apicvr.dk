"""Copy for the server-rendered API reference (/api-dokumentation/, /en/api-reference/).

/docs (Swagger UI) is a JavaScript shell with no crawlable text, so this page
is the indexable reference. Paths, parameters and response fields are read
from the live OpenAPI schema in main.py; only the prose lives here.
"""

PATHS = {"da": "/api-dokumentation/", "en": "/en/api-reference/"}

# Order shown on the page. Keys are OpenAPI paths.
ENDPOINTS = [
    {
        "path": "/api/v1/{cvrNumber}",
        "anchor": "virksomhed",
        "example": "/api/v1/41013583",
        "da": {
            "name": "Hent virksomhed på CVR-nummer",
            "text": (
                "Den fulde virksomhedsprofil: navn, adresse, kontaktoplysninger, branchekode, "
                "virksomhedsform, status, antal ansatte, reklamebeskyttelse, alle P-enheder samt "
                "nuværende direktion, fuldt ansvarlige deltagere og legale ejere."
            ),
        },
        "en": {
            "name": "Get a company by CVR number",
            "text": (
                "The full company profile: name, address, contact details, industry code, company "
                "type, status, headcount, marketing protection, every production unit, plus current "
                "management, fully liable participants and legal owners."
            ),
        },
    },
    {
        "path": "/api/v1/{cvrNumber}/direktion-og-ansvarlig",
        "anchor": "direktion-og-ejere",
        "example": "/api/v1/41013583/direktion-og-ansvarlig",
        "da": {
            "name": "Direktion, fuldt ansvarlige og ejere",
            "text": (
                "Et slankt svar med kun de personer og selskaber, der aktuelt leder eller ejer "
                "virksomheden. Ejere har ejerandel og stemmeret både som tal og som CVR's "
                "intervaller (fx <code>25-33,32%</code>)."
            ),
        },
        "en": {
            "name": "Management, fully liable participants and owners",
            "text": (
                "A slim response with only the people and companies currently running or owning the "
                "company. Owners include ownership share and voting rights both as numbers and as "
                "CVR's display ranges (e.g. <code>25-33,32%</code>)."
            ),
        },
    },
    {
        "path": "/api/v1/search",
        "anchor": "soegning",
        "example": "/api/v1/search?name=novo&limit=5",
        "da": {
            "name": "Kombineret søgning på navn og/eller CVR",
            "text": "Søg på navn (præfiks), CVR-nummer eller begge. Mindst én af parametrene er påkrævet.",
        },
        "en": {
            "name": "Combined search by name and/or CVR",
            "text": "Search by name (prefix), CVR number, or both. At least one parameter is required.",
        },
    },
    {
        "path": "/api/v1/search/company/{companyName}",
        "anchor": "navnesoegning",
        "example": "/api/v1/search/company/Novo%20Nordisk?limit=5",
        "da": {
            "name": "Søg på virksomhedsnavn",
            "text": "Præfiks-match på virksomhedens nuværende navn. Returnerer fulde virksomhedsprofiler.",
        },
        "en": {
            "name": "Search by company name",
            "text": "Prefix match on the company's current name. Returns full company profiles.",
        },
    },
    {
        "path": "/api/v1/search/fuzzy/{companyName}",
        "anchor": "fuzzy",
        "example": "/api/v1/search/fuzzy/novo%20nordsk?limit=5",
        "da": {
            "name": "Fejltolerant navnesøgning (autocomplete)",
            "text": (
                "Finder virksomheden selv med stavefejl og returnerer et slankt svar med navn, "
                "CVR-nummer og branche. Lavet til autocomplete-felter."
            ),
        },
        "en": {
            "name": "Typo-tolerant name search (autocomplete)",
            "text": (
                "Finds the company even when the name is misspelled, and returns a slim response with "
                "name, CVR number and industry. Built for autocomplete fields."
            ),
        },
    },
    {
        "path": "/api/v1/search/address",
        "anchor": "adresse",
        "example": "/api/v1/search/address?address=Novo%20All%C3%A9%201&postal_code=2880",
        "da": {
            "name": "Søg på adresse",
            "text": (
                "Find alle virksomheder registreret på en adresse. Søgningen prøver først et eksakt "
                "match, derefter vejnavn og husnummer og til sidst et fejltolerant match. Angiv "
                "<code>postal_code</code> for at afgrænse til ét postnummer."
            ),
        },
        "en": {
            "name": "Search by address",
            "text": (
                "Find every company registered at an address. The search tries an exact match first, "
                "then street name and number, then a typo-tolerant match. Pass <code>postal_code</code> "
                "to narrow it to one postal district."
            ),
        },
    },
    {
        "path": "/api/v1/search/email/{email}",
        "anchor": "email",
        "example": "/api/v1/search/email/info@example.dk",
        "da": {
            "name": "Søg på email",
            "text": "Find virksomheder, der har den angivne email registreret offentligt i CVR.",
        },
        "en": {
            "name": "Search by email",
            "text": "Find companies with the given email on their public CVR record.",
        },
    },
    {
        "path": "/api/v1/search/email-domain/{domain}",
        "anchor": "email-domaene",
        "example": "/api/v1/search/email-domain/novonordisk.com",
        "da": {
            "name": "Søg på emaildomæne",
            "text": (
                "Find virksomheder, hvis registrerede email ligger på domænet. Godt til at koble en "
                "B2B-lead eller en ny bruger til den rigtige virksomhed."
            ),
        },
        "en": {
            "name": "Search by email domain",
            "text": (
                "Find companies whose registered email is on the domain. Handy for matching a B2B lead "
                "or a new user to the right company."
            ),
        },
    },
    {
        "path": "/api/v1/search/phone/{phone}",
        "anchor": "telefon",
        "example": "/api/v1/search/phone/44448888",
        "da": {
            "name": "Søg på telefonnummer",
            "text": "Find virksomheder med telefonnummeret registreret offentligt i CVR.",
        },
        "en": {
            "name": "Search by phone number",
            "text": "Find companies with the phone number on their public CVR record.",
        },
    },
]

# Parameter descriptions (OpenAPI has none for these).
PARAMS = {
    "cvrNumber": {"da": "CVR-nummer på 8 cifre.", "en": "8-digit CVR number."},
    "companyName": {"da": "Virksomhedsnavn eller en del af det.", "en": "Company name or part of it."},
    "name": {"da": "Virksomhedsnavn (præfiks).", "en": "Company name (prefix)."},
    "cvr": {"da": "CVR-nummer på 8 cifre.", "en": "8-digit CVR number."},
    "address": {"da": "Vejnavn og husnummer, fx <code>Novo Allé 1</code>.", "en": "Street and number, e.g. <code>Novo Allé 1</code>."},
    "postal_code": {"da": "Postnummer på 4 cifre.", "en": "4-digit postal code."},
    "email": {"da": "Fuld emailadresse.", "en": "Full email address."},
    "domain": {"da": "Domæne uden @, fx <code>firma.dk</code>.", "en": "Domain without @, e.g. <code>firma.dk</code>."},
    "phone": {"da": "Telefonnummer, 8 cifre uden landekode.", "en": "Phone number, 8 digits without country code."},
    "limit": {"da": "Maks. antal resultater (standard 100).", "en": "Max number of results (default 100)."},
}

# Response field descriptions for the Company model, in display order.
COMPANY_FIELDS = [
    ("vat", "CVR-nummeret (8 cifre).", "The CVR number (8 digits)."),
    ("name", "Nuværende navn.", "Current name."),
    ("address", "Vejnavn, husnummer, etage og dør.", "Street, number, floor and door."),
    ("zipcode", "Postnummer.", "Postal code."),
    ("city", "By (postdistrikt).", "City (postal district)."),
    ("cityname", "Bynavn, hvis det adskiller sig fra postdistriktet.", "Town name, when it differs from the postal district."),
    ("addressco", "c/o-adresse.", "c/o address."),
    ("protected", "<code>true</code> hvis virksomheden har reklamebeskyttelse.", "<code>true</code> if the company has opted out of marketing."),
    ("phone", "Offentligt registreret telefonnummer.", "Publicly registered phone number."),
    ("email", "Offentligt registreret email.", "Publicly registered email."),
    ("website", "Hjemmeside, hvis registreret.", "Website, if registered."),
    ("startdate", "Stiftelsesdato (ÅÅÅÅ-MM-DD).", "Founding date (YYYY-MM-DD)."),
    ("enddate", "Ophørsdato, ellers <code>null</code>.", "Closing date, otherwise <code>null</code>."),
    ("employees", "Antal ansatte (seneste indberetning).", "Headcount (latest filing)."),
    ("industrycode", "Branchekode (DB07, 6 cifre).", "Industry code (DB07, 6 digits)."),
    ("industrydesc", "Branchebeskrivelse.", "Industry description."),
    ("companycode", "Kode for virksomhedsform.", "Company type code."),
    ("companydesc", "Virksomhedsform, fx Aktieselskab.", "Company type, e.g. Aktieselskab."),
    ("companytypeshort", "Kort virksomhedsform, fx A/S eller ApS.", "Short company type, e.g. A/S or ApS."),
    ("status", "Fx <code>NORMAL</code>, <code>OPHØRT</code> eller <code>UNDERKONKURS</code>.", "E.g. <code>NORMAL</code>, <code>OPHØRT</code> or <code>UNDERKONKURS</code>."),
    ("bankrupt", "<code>true</code> hvis virksomheden er under konkurs.", "<code>true</code> if the company is bankrupt."),
    ("p_units", "Liste over produktionsenheder (P-enheder) med adresse, branche og ansatte.", "List of production units (P-units) with address, industry and headcount."),
    ("direktion", "Nuværende direktører.", "Current directors."),
    ("fuldt_ansvarlige", "Deltagere med personlig, ubegrænset hæftelse.", "Participants with unlimited personal liability."),
    ("ejere", "Legale ejere med ejerandel og stemmeret.", "Legal owners with ownership share and voting rights."),
]

ERRORS = [
    ("400", "MISSING_QUERY", "<code>/api/v1/search</code> blev kaldt uden <code>name</code> eller <code>cvr</code>.", "<code>/api/v1/search</code> was called without <code>name</code> or <code>cvr</code>."),
    ("404", "NOT_FOUND", "Ingen virksomhed med det CVR-nummer.", "No company with that CVR number."),
    ("422", "–", "En parameter har forkert type, fx et CVR-nummer med bogstaver.", "A parameter has the wrong type, e.g. a CVR number containing letters."),
    ("502", "HTTP_ERROR", "Erhvervsstyrelsens CVR-distribution svarede med en fejl. Prøv igen.", "The Danish Business Authority's CVR distribution returned an error. Retry."),
    ("502", "TRANSPORT_ERROR", "CVR-distributionen kunne ikke nås. Prøv igen om lidt.", "The CVR distribution could not be reached. Retry shortly."),
]

TEXT = {
    "da": {
        "title": "CVR API dokumentation – endpoints, felter og eksempler | APICVR.dk",
        "description": (
            "Fuld dokumentation til det gratis CVR API: alle endpoints, parametre, svarfelter, "
            "fejlkoder og curl-eksempler. Ingen API-nøgle – kald direkte og få JSON tilbage."
        ),
        "h1": "CVR API dokumentation",
        "lead": (
            "Alle endpoints er GET-kald uden API-nøgle og returnerer JSON. Basis-URL'en er "
            "https://apicvr.dk. Her finder du hvert endpoint med parametre, eksempel og felter."
        ),
        "crumb": "Dokumentation",
        "toc": "Indhold",
        "basics": "Grundlæggende",
        "basics_items": [
            "Basis-URL: <code>https://apicvr.dk</code>",
            "Autentificering: ingen – ingen konto, ingen API-nøgle",
            "Format: JSON (UTF-8). CORS er slået til, så du kan kalde API'et direkte fra browseren",
            "Data: live opslag i Erhvervsstyrelsens CVR-distribution (distribution.virk.dk)",
            "Rate limits: fair use. Skal du bruge vedvarende høj trafik, så skriv til noah@noahbohme.com",
        ],
        "params": "Parametre",
        "param": "Parameter",
        "where": "Placering",
        "where_path": "sti",
        "where_query": "query",
        "required": "påkrævet",
        "optional": "valgfri",
        "desc": "Beskrivelse",
        "example": "Eksempel",
        "try": "Åbn i browseren",
        "fields": "Svarfelter",
        "field": "Felt",
        "type": "Type",
        "fields_sub": (
            "Gælder <code>/api/v1/{cvrNumber}</code> og søge-endpoints (søgninger udelader P-enheder "
            "og relationer). Felter uden værdi er <code>null</code>."
        ),
        "errors": "Fejlkoder",
        "errors_sub": "Fejl returneres som <code>{\"detail\": {\"error\": \"KODE\", \"message\": \"…\"}}</code>.",
        "status": "HTTP",
        "code": "Kode",
        "swagger": "Interaktiv Swagger-dokumentation",
        "swagger_text": "Vil du prøve kald med egne parametre, så brug",
        "openapi": "OpenAPI-specifikation",
    },
    "en": {
        "title": "CVR API Reference – Endpoints, Fields and Examples | APICVR.dk",
        "description": (
            "Full reference for the free CVR API: every endpoint, parameter, response field, error "
            "code and curl example. No API key – call it directly and get JSON back."
        ),
        "h1": "CVR API reference",
        "lead": (
            "Every endpoint is a GET request with no API key and returns JSON. The base URL is "
            "https://apicvr.dk. Below you'll find each endpoint with parameters, an example and fields."
        ),
        "crumb": "API reference",
        "toc": "Contents",
        "basics": "Basics",
        "basics_items": [
            "Base URL: <code>https://apicvr.dk</code>",
            "Authentication: none – no account, no API key",
            "Format: JSON (UTF-8). CORS is enabled, so you can call the API straight from the browser",
            "Data: live lookups against the Danish Business Authority's CVR distribution (distribution.virk.dk)",
            "Rate limits: fair use. If you need sustained heavy traffic, email noah@noahbohme.com",
        ],
        "params": "Parameters",
        "param": "Parameter",
        "where": "In",
        "where_path": "path",
        "where_query": "query",
        "required": "required",
        "optional": "optional",
        "desc": "Description",
        "example": "Example",
        "try": "Open in browser",
        "fields": "Response fields",
        "field": "Field",
        "type": "Type",
        "fields_sub": (
            "Applies to <code>/api/v1/{cvrNumber}</code> and the search endpoints (searches omit "
            "production units and relations). Fields without a value are <code>null</code>."
        ),
        "errors": "Error codes",
        "errors_sub": "Errors come back as <code>{\"detail\": {\"error\": \"CODE\", \"message\": \"…\"}}</code>.",
        "status": "HTTP",
        "code": "Code",
        "swagger": "Interactive Swagger docs",
        "swagger_text": "To try calls with your own parameters, use the",
        "openapi": "OpenAPI specification",
    },
}
