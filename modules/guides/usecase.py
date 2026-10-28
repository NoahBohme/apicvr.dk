"""Use-case guides: one page per kind of lookup or search the API supports."""

_PHONE_JSON = """[
  {
    "vat": 32657222,
    "name": "NOVO NORDISK PHARMA OPERATIONS A/S",
    "address": "Novo Alle 1",
    "zipcode": 2880,
    "city": "Bagsværd",
    "phone": "44448888",
    "status": "NORMAL",
    "protected": false,
    "industrydesc": "...",
    ...
  },
  ...
]"""

_EMAIL_JSON = """[
  {
    "vat": 10403782,
    "name": "VESTAS WIND SYSTEMS A/S",
    "address": "Hedeager 42",
    "zipcode": 8200,
    "city": "Aarhus N",
    "phone": "97300000",
    "email": "vestas@vestas.dk",
    "status": "NORMAL",
    "protected": false,
    ...
  },
  ...
]"""

_ADDRESS_JSON = """[
  {
    "vat": 28118244,
    "name": "VESTAS AMERICAS A/S",
    "address": "Hedeager 42",
    "zipcode": 8200,
    "city": "Aarhus N",
    "status": "NORMAL",
    "protected": false,
    ...
  },
  {
    "vat": 27988210,
    "name": "VESTAS MANUFACTURING A/S",
    "address": "Hedeager 42",
    ...
  }
]"""

_OWNERS_JSON = """{
  "vat": 24256790,
  "direktion": [
    {
      "name": "Karsten Munk Knudsen",
      "role": "DIREKTØR",
      "type": "PERSON",
      "cvr": null,
      "startdate": "2018-02-15",
      ...
    }
  ],
  "fuldt_ansvarlige": [],
  "ejere": [
    {
      "name": "Novo Holdings A/S",
      "type": "VIRKSOMHED",
      "cvr": 24257630,
      "country": "DK",
      "ownership_percent": 0.25,
      "ownership_range": "25-33,32%",
      "voting_rights_percent": 0.6667,
      "voting_rights_range": "66,67-89,99%",
      "startdate": "2000-11-13"
    }
  ]
}"""

_PUNITS_JSON = """{
  "vat": 24256790,
  "name": "NOVO NORDISK A/S",
  ...
  "p_units": [
    {
      "p_number": 1007712304,
      "name": "Novo Nordisk A/S",
      "address": "Brogårdsvej 66",
      "zipcode": 2820,
      "city": "Gentofte",
      "startdate": "1999-10-18",
      "enddate": "2001-12-31",
      "industrycode": 244200,
      "industrydesc": "Fremstilling af aluminium",
      "employees": null,
      "protected": false
    },
    ...
  ]
}"""

_VALIDATE_JSON = """{
  "vat": 10403782,
  "name": "VESTAS WIND SYSTEMS A/S",
  "status": "NORMAL",
  "startdate": "...",
  "enddate": null,
  "bankrupt": false,
  "companydesc": "Aktieselskab",
  ...
}"""

_NOT_FOUND_JSON = """{"detail": {"error": "NOT_FOUND", "status": 404, "message": null}}"""

_MOD11_PY = """WEIGHTS = (2, 7, 6, 5, 4, 3, 2, 1)

def is_valid_cvr(cvr: str) -> bool:
    cvr = cvr.replace(" ", "")
    if len(cvr) != 8 or not cvr.isdigit() or cvr[0] == "0":
        return False
    return sum(int(d) * w for d, w in zip(cvr, WEIGHTS)) % 11 == 0

is_valid_cvr("10403782")  # True  (Vestas Wind Systems A/S)
is_valid_cvr("12345678")  # False"""

_MOD11_JS = """const WEIGHTS = [2, 7, 6, 5, 4, 3, 2, 1];

function isValidCvr(input) {
  const cvr = String(input).replace(/\\s/g, "");
  if (!/^[1-9]\\d{7}$/.test(cvr)) return false;
  const sum = [...cvr].reduce((acc, d, i) => acc + Number(d) * WEIGHTS[i], 0);
  return sum % 11 === 0;
}

async function checkCvr(cvr) {
  if (!isValidCvr(cvr)) return { valid: false, reason: "checksum" };
  const res = await fetch(`{site}/api/v1/${cvr}`);
  if (res.status === 404) return { valid: false, reason: "not_found" };
  const company = await res.json();
  const active = !company.enddate && !company.bankrupt;
  return { valid: true, active, name: company.name };
}"""


PAGES = [
    # ------------------------------------------------------------------
    {
        "id": "find-by-phone",
        "family": "usecase",
        "slug": {
            "da": "find-virksomhed-ud-fra-telefonnummer",
            "en": "find-company-by-phone-number",
        },
        "related": ["find-by-email", "find-by-address", "python"],
        "da": {
            "title": "Find virksomhed ud fra telefonnummer – CVR API",
            "description": (
                "Slå en dansk virksomhed op ud fra telefonnummer med et gratis CVR API. "
                "Ét GET-kald returnerer alle virksomheder med nummeret registreret i CVR."
            ),
            "h1": "Find en virksomhed ud fra telefonnummer",
            "lead": (
                "Har du et telefonnummer og vil vide, hvilken virksomhed der står bag? Endpointet "
                "/api/v1/search/phone/{telefon} søger i de telefonnumre, virksomhederne selv har "
                "registreret i CVR, og returnerer de fulde virksomhedsprofiler."
            ),
            "blocks": [
                ("h2", "Sådan kalder du endpointet"),
                ("p", "Send telefonnummeret som de 8 cifre uden landekode, mellemrum eller bindestreger:"),
                ("code", "bash", "curl {site}/api/v1/search/phone/44448888"),
                ("h2", "Eksempel på svar"),
                ("p", "Svaret er en liste, fordi flere virksomheder kan dele nummer – typisk koncernselskaber "
                      "eller foreninger på samme hovednummer:"),
                ("code", "json", _PHONE_JSON),
                ("h2", "Normalisér nummeret først"),
                ("p", "Søgningen er en fritekstsøgning i CVR-registrets telefonfelt. Sender du "
                      "<code>+45 44 44 88 88</code>, bliver de enkelte tal matchet hver for sig, og du får "
                      "tilfældige resultater. Fjern derfor landekode og alt andet end cifre, før du kalder API'et:"),
                ("code", "python", """import re
import requests

def find_by_phone(raw: str) -> list:
    digits = re.sub(r"\\D", "", raw)
    if digits.startswith("45") and len(digits) == 10:
        digits = digits[2:]
    if len(digits) != 8:
        return []
    res = requests.get(f"{site}/api/v1/search/phone/{digits}", timeout=10)
    res.raise_for_status()
    return [c for c in res.json() if c["phone"] == digits]

for company in find_by_phone("+45 44 44 88 88"):
    print(company["vat"], company["name"], company["status"])"""),
                ("h2", "Gode råd"),
                ("ul", [
                    "Tjek feltet <code>phone</code> i hvert resultat, hvis du kun vil have eksakte match.",
                    "Resultatet indeholder også ophørte virksomheder. Filtrér på <code>enddate</code> eller "
                    "<code>status</code>, hvis du kun vil have aktive.",
                    "Kun numre, virksomheden selv har registreret i CVR, kan findes. Mobilnumre på "
                    "medarbejdere står der typisk ikke.",
                    "Brug <code>?limit=</code> til at begrænse antallet af resultater (standard er 100).",
                    "Ringer du til virksomhederne i markedsføringsøjemed, så respektér "
                    "<code>protected</code>: er feltet <code>true</code>, har virksomheden frabedt sig "
                    "reklamehenvendelser.",
                ]),
            ],
            "faq": [
                ("Kan jeg søge med +45 foran nummeret?",
                 "Nej, send kun de 8 cifre. Landekode og mellemrum giver upræcise resultater, fordi "
                 "søgningen matcher hvert tal for sig."),
                ("Hvorfor får jeg flere virksomheder på ét nummer?",
                 "Flere CVR-enheder kan have registreret samme telefonnummer, fx datterselskaber, fonde "
                 "eller personaleforeninger på et fælles hovednummer."),
                ("Koster det noget?",
                 "Nej. Endpointet er gratis og kræver ingen API-nøgle."),
            ],
        },
        "en": {
            "title": "Find a Danish Company by Phone Number – CVR API",
            "description": (
                "Look up a Danish company by phone number with a free CVR API. One GET request "
                "returns every company that registered the number in the CVR register."
            ),
            "h1": "Find a Danish company by phone number",
            "lead": (
                "Got a phone number and want to know which company is behind it? The "
                "/api/v1/search/phone/{phone} endpoint searches the phone numbers companies have "
                "registered in CVR and returns full company profiles."
            ),
            "blocks": [
                ("h2", "Calling the endpoint"),
                ("p", "Pass the number as its 8 digits, without country code, spaces or dashes:"),
                ("code", "bash", "curl {site}/api/v1/search/phone/44448888"),
                ("h2", "Example response"),
                ("p", "The response is a list, because several companies can share a number – typically "
                      "group companies or associations on the same switchboard:"),
                ("code", "json", _PHONE_JSON),
                ("h2", "Normalize the number first"),
                ("p", "The search is a full-text match on the register's phone field. If you send "
                      "<code>+45 44 44 88 88</code>, each group of digits is matched separately and you get "
                      "unrelated results. Strip the country code and every non-digit before calling the API:"),
                ("code", "python", """import re
import requests

def find_by_phone(raw: str) -> list:
    digits = re.sub(r"\\D", "", raw)
    if digits.startswith("45") and len(digits) == 10:
        digits = digits[2:]
    if len(digits) != 8:
        return []
    res = requests.get(f"{site}/api/v1/search/phone/{digits}", timeout=10)
    res.raise_for_status()
    return [c for c in res.json() if c["phone"] == digits]

for company in find_by_phone("+45 44 44 88 88"):
    print(company["vat"], company["name"], company["status"])"""),
                ("h2", "Tips"),
                ("ul", [
                    "Check the <code>phone</code> field on each result if you only want exact matches.",
                    "Results include companies that have ceased. Filter on <code>enddate</code> or "
                    "<code>status</code> if you only want active ones.",
                    "Only numbers the company registered in CVR can be found. Employees' mobile numbers "
                    "usually aren't there.",
                    "Use <code>?limit=</code> to cap the number of results (default 100).",
                    "If you call companies for marketing, respect <code>protected</code>: when it's "
                    "<code>true</code>, the company has opted out of marketing contact.",
                ]),
            ],
            "faq": [
                ("Can I include +45 in the number?",
                 "No, send only the 8 digits. A country code or spaces give imprecise results because "
                 "each group of digits is matched separately."),
                ("Why do I get several companies for one number?",
                 "Several CVR entities can register the same phone number, such as subsidiaries, "
                 "foundations or staff associations sharing a switchboard."),
                ("Does it cost anything?",
                 "No. The endpoint is free and needs no API key."),
            ],
        },
    },
    # ------------------------------------------------------------------
    {
        "id": "find-by-email",
        "family": "usecase",
        "slug": {
            "da": "find-virksomhed-ud-fra-email",
            "en": "find-company-by-email",
        },
        "related": ["find-by-phone", "zapier-make", "javascript"],
        "da": {
            "title": "Find virksomhed ud fra email eller domæne – CVR API",
            "description": (
                "Find danske virksomheder ud fra en emailadresse eller et emaildomæne. Gratis CVR API "
                "uden API-nøgle – perfekt til at berige leads og CRM-data."
            ),
            "h1": "Find en virksomhed ud fra email eller domæne",
            "lead": (
                "To endpoints søger i de emailadresser, virksomheder har registreret i CVR: ét til en "
                "konkret adresse og ét til et helt domæne. Det er nyttigt, når du vil koble en "
                "tilmelding eller et lead til det rigtige CVR-nummer."
            ),
            "blocks": [
                ("h2", "Søg på en emailadresse"),
                ("code", "bash", "curl {site}/api/v1/search/email/vestas@vestas.dk"),
                ("h2", "Søg på et domæne"),
                ("p", "Send domænet uden <code>@</code> – API'et tilføjer det selv:"),
                ("code", "bash", "curl {site}/api/v1/search/email-domain/vestas.dk"),
                ("h2", "Eksempel på svar"),
                ("p", "Begge endpoints returnerer en liste af fulde virksomhedsprofiler:"),
                ("code", "json", _EMAIL_JSON),
                ("h2", "Filtrér på eksakt match"),
                ("p", "Søgningen er en fritekstsøgning, så den finder også virksomheder, der blot deler "
                      "ord med adressen – fx andre selskaber med <em>vestas</em> i emailen eller uden "
                      "email overhovedet. Sorter de bedste match først, og tjek feltet <code>email</code> "
                      "selv:"),
                ("code", "javascript", """async function companiesForEmail(email) {
  const url = `{site}/api/v1/search/email/${encodeURIComponent(email)}?limit=20`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const companies = await res.json();
  return companies.filter(
    (c) => c.email && c.email.toLowerCase() === email.toLowerCase()
  );
}

async function companiesForDomain(domain) {
  const res = await fetch(`{site}/api/v1/search/email-domain/${domain}?limit=50`);
  const companies = await res.json();
  return companies.filter((c) => c.email?.toLowerCase().endsWith("@" + domain));
}"""),
                ("h2", "Begrænsninger"),
                ("ul", [
                    "Kun den email, virksomheden har registreret i CVR, kan findes. Mange store "
                    "virksomheder har slet ikke en email registreret.",
                    "Freemail-domæner som gmail.com eller hotmail.com giver tusindvis af træf og siger "
                    "ikke noget om virksomheden – spring dem over.",
                    "Domænesøgningen kan også ramme lignende domæner (fx vestas.com ved søgning på "
                    "vestas.dk). Tjek altid domænet i <code>email</code>.",
                    "Bruger du resultatet til markedsføring, så filtrér virksomheder med "
                    "<code>protected: true</code> fra.",
                ]),
            ],
            "faq": [
                ("Kan jeg finde en virksomhed ud fra en medarbejders email?",
                 "Kun hvis den præcise adresse er registreret i CVR. Brug i stedet domænesøgningen "
                 "og tjek domænet i feltet <code>email</code>."),
                ("Hvorfor indeholder svaret virksomheder med en anden email?",
                 "Søgningen matcher ord i adressen, ikke hele adressen. Filtrér på feltet "
                 "<code>email</code>, hvis du kun vil have eksakte match."),
            ],
        },
        "en": {
            "title": "Find a Danish Company by Email or Domain – CVR API",
            "description": (
                "Find Danish companies from an email address or email domain. A free CVR API with no "
                "API key – ideal for enriching leads and CRM records."
            ),
            "h1": "Find a Danish company by email or domain",
            "lead": (
                "Two endpoints search the email addresses companies have registered in CVR: one for a "
                "specific address and one for a whole domain. It's handy when you want to link a "
                "sign-up or lead to the right CVR number."
            ),
            "blocks": [
                ("h2", "Search by email address"),
                ("code", "bash", "curl {site}/api/v1/search/email/vestas@vestas.dk"),
                ("h2", "Search by domain"),
                ("p", "Pass the domain without <code>@</code> – the API adds it for you:"),
                ("code", "bash", "curl {site}/api/v1/search/email-domain/vestas.dk"),
                ("h2", "Example response"),
                ("p", "Both endpoints return a list of full company profiles:"),
                ("code", "json", _EMAIL_JSON),
                ("h2", "Filter for exact matches"),
                ("p", "The search is full-text, so it also returns companies that merely share words with "
                      "the address – other companies with <em>vestas</em> in their email, or no email at "
                      "all. Check the <code>email</code> field yourself:"),
                ("code", "javascript", """async function companiesForEmail(email) {
  const url = `{site}/api/v1/search/email/${encodeURIComponent(email)}?limit=20`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const companies = await res.json();
  return companies.filter(
    (c) => c.email && c.email.toLowerCase() === email.toLowerCase()
  );
}

async function companiesForDomain(domain) {
  const res = await fetch(`{site}/api/v1/search/email-domain/${domain}?limit=50`);
  const companies = await res.json();
  return companies.filter((c) => c.email?.toLowerCase().endsWith("@" + domain));
}"""),
                ("h2", "Limitations"),
                ("ul", [
                    "Only the email a company registered in CVR can be found. Many large companies have "
                    "no email registered at all.",
                    "Free-mail domains like gmail.com or hotmail.com return thousands of hits and say "
                    "nothing about the company – skip them.",
                    "Domain search can also hit similar domains (e.g. vestas.com when searching for "
                    "vestas.dk). Always check the domain in <code>email</code>.",
                    "If you use the results for marketing, drop companies with "
                    "<code>protected: true</code>.",
                ]),
            ],
            "faq": [
                ("Can I find a company from an employee's email?",
                 "Only if that exact address is registered in CVR. Use the domain search instead and "
                 "check the domain in the <code>email</code> field."),
                ("Why does the response include companies with a different email?",
                 "The search matches words in the address, not the whole address. Filter on the "
                 "<code>email</code> field if you only want exact matches."),
            ],
        },
    },
    # ------------------------------------------------------------------
    {
        "id": "find-by-address",
        "family": "usecase",
        "slug": {
            "da": "find-virksomheder-paa-adresse",
            "en": "find-companies-by-address",
        },
        "related": ["p-units", "find-by-phone", "python"],
        "da": {
            "title": "Find virksomheder på en adresse – CVR API",
            "description": (
                "Se hvilke virksomheder der er registreret på en dansk adresse. Gratis CVR API med "
                "eksakt, struktureret og fejltolerant adressesøgning – ingen API-nøgle."
            ),
            "h1": "Find virksomheder registreret på en adresse",
            "lead": (
                "Med /api/v1/search/address kan du se alle virksomheder, der har deres adresse på en "
                "bestemt vej og et bestemt husnummer. Brug det til at tjekke kontorfællesskaber, "
                "verificere en kundes adresse eller finde selskaberne i en koncern."
            ),
            "blocks": [
                ("h2", "Sådan kalder du endpointet"),
                ("p", "Send adressen i <code>address</code> og gerne postnummeret i <code>postal_code</code>, "
                      "så søgningen holdes inden for ét postdistrikt:"),
                ("code", "bash", 'curl "{site}/api/v1/search/address?address=Hedeager%2042&postal_code=8200"'),
                ("h2", "Eksempel på svar"),
                ("code", "json", _ADDRESS_JSON),
                ("h2", "Sådan matcher søgningen"),
                ("p", "API'et prøver tre strategier i rækkefølge og returnerer resultatet fra den første, "
                      "der finder noget:"),
                ("ol", [
                    "<strong>Eksakt match</strong> på hele adressebetegnelsen.",
                    "<strong>Struktureret match</strong> på vejnavn og husnummer, som API'et selv udleder "
                    "af teksten.",
                    "<strong>Fejltolerant match</strong> på tværs af adressefelterne, så stavefejl og "
                    "forkortelser stadig giver resultater.",
                ]),
                ("p", "Derfor får du næsten altid noget tilbage – men et fejltolerant match kan ramme "
                      "nabonumre. Tjek <code>address</code> og <code>zipcode</code> i svaret, hvis du skal "
                      "være sikker."),
                ("h2", "Eksempel i Python"),
                ("code", "python", """import requests

res = requests.get(
    "{site}/api/v1/search/address",
    params={"address": "Hedeager 42", "postal_code": "8200", "limit": 50},
    timeout=10,
)
res.raise_for_status()

active = [c for c in res.json() if not c["enddate"]]
for company in active:
    print(company["vat"], company["name"])"""),
                ("h2", "Gode råd"),
                ("ul", [
                    "Angiv altid <code>postal_code</code>, når du kender det – det fjerner mange falske træf.",
                    "Svaret indeholder også ophørte virksomheder. Filtrér på <code>enddate</code>.",
                    "Søgningen kigger på virksomhedens hovedadresse. Skal du finde arbejdssteder, så brug "
                    "P-enhederne i et opslag på CVR-nummeret.",
                    "Enkeltmandsvirksomheder er ofte registreret på ejerens bopæl. Behandl dem med omtanke, "
                    "og respektér <code>protected</code> ved markedsføring.",
                ]),
            ],
            "faq": [
                ("Skal adressen staves helt korrekt?",
                 "Nej. Finder den eksakte søgning intet, falder API'et tilbage til en fejltolerant "
                 "søgning. Tilføj postnummer for at få mere præcise resultater."),
                ("Kan jeg søge på et helt postnummer eller en hel vej?",
                 "Endpointet er lavet til konkrete adresser. En vej uden husnummer kan give mange "
                 "resultater, og <code>limit</code> er højst det antal, du beder om (standard 100)."),
            ],
        },
        "en": {
            "title": "Find Companies at a Danish Address – CVR API",
            "description": (
                "See which companies are registered at a Danish address. Free CVR API with exact, "
                "structured and typo-tolerant address search – no API key needed."
            ),
            "h1": "Find companies registered at an address",
            "lead": (
                "With /api/v1/search/address you can list every company registered at a given street "
                "and house number. Use it to check shared offices, verify a customer's address or find "
                "the companies in a group."
            ),
            "blocks": [
                ("h2", "Calling the endpoint"),
                ("p", "Pass the address in <code>address</code> and, ideally, the postal code in "
                      "<code>postal_code</code> to keep the search within one postal district:"),
                ("code", "bash", 'curl "{site}/api/v1/search/address?address=Hedeager%2042&postal_code=8200"'),
                ("h2", "Example response"),
                ("code", "json", _ADDRESS_JSON),
                ("h2", "How matching works"),
                ("p", "The API tries three strategies in order and returns the result of the first one "
                      "that finds anything:"),
                ("ol", [
                    "<strong>Exact match</strong> on the full address designation.",
                    "<strong>Structured match</strong> on street name and house number, which the API "
                    "parses from your text.",
                    "<strong>Typo-tolerant match</strong> across the address fields, so misspellings and "
                    "abbreviations still return results.",
                ]),
                ("p", "So you almost always get something back – but a fuzzy match can hit neighbouring "
                      "numbers. Check <code>address</code> and <code>zipcode</code> in the response if you "
                      "need certainty."),
                ("h2", "Python example"),
                ("code", "python", """import requests

res = requests.get(
    "{site}/api/v1/search/address",
    params={"address": "Hedeager 42", "postal_code": "8200", "limit": 50},
    timeout=10,
)
res.raise_for_status()

active = [c for c in res.json() if not c["enddate"]]
for company in active:
    print(company["vat"], company["name"])"""),
                ("h2", "Tips"),
                ("ul", [
                    "Always pass <code>postal_code</code> when you know it – it removes many false hits.",
                    "Results include companies that have ceased. Filter on <code>enddate</code>.",
                    "The search looks at each company's main address. To find workplaces, use the "
                    "production units from a CVR lookup.",
                    "Sole proprietorships are often registered at the owner's home. Handle them with care, "
                    "and respect <code>protected</code> for marketing.",
                ]),
            ],
            "faq": [
                ("Does the address have to be spelled exactly right?",
                 "No. If the exact search finds nothing, the API falls back to a typo-tolerant search. "
                 "Add the postal code for more precise results."),
                ("Can I search a whole postal code or street?",
                 "The endpoint is built for specific addresses. A street without a house number can "
                 "return many results, capped by <code>limit</code> (default 100)."),
            ],
        },
    },
    # ------------------------------------------------------------------
    {
        "id": "owners-management",
        "family": "usecase",
        "slug": {
            "da": "ejere-og-direktion-api",
            "en": "company-owners-and-management-api",
        },
        "related": ["validate-cvr", "company-types", "python"],
        "da": {
            "title": "Ejere og direktion via API – gratis CVR API",
            "description": (
                "Hent legale ejere med ejerandel og stemmeret samt direktion og fuldt ansvarlige for "
                "enhver dansk virksomhed. Gratis CVR API i JSON uden API-nøgle."
            ),
            "h1": "Hent ejere og direktion for en dansk virksomhed",
            "lead": (
                "Til KYC, kreditvurdering og onboarding skal du ofte vide, hvem der ejer og leder en "
                "virksomhed. CVR-API giver dig de aktuelle legale ejere med ejerandel og stemmeret, "
                "direktionen og de fuldt ansvarlige deltagere – direkte fra CVR."
            ),
            "blocks": [
                ("h2", "To måder at hente dem på"),
                ("p", "Det fulde opslag <code>/api/v1/{cvr}</code> indeholder felterne <code>direktion</code>, "
                      "<code>fuldt_ansvarlige</code> og <code>ejere</code>. Har du kun brug for personerne, "
                      "er det slanke endpoint hurtigere, fordi det springer P-enheder og stamdata over:"),
                ("code", "bash", "curl {site}/api/v1/24256790/direktion-og-ansvarlig"),
                ("h2", "Eksempel på svar"),
                ("code", "json", _OWNERS_JSON),
                ("h2", "Sådan læser du felterne"),
                ("table", ["Felt", "Betydning"], [
                    ["<code>direktion</code>", "Nuværende direktører (fx DIREKTØR eller ADM. DIR.)."],
                    ["<code>fuldt_ansvarlige</code>", "Deltagere med personlig hæftelse, fx interessenter i et I/S."],
                    ["<code>ejere</code>", "Legale ejere fra ejerregistret med andel og stemmeret."],
                    ["<code>ownership_percent</code>", "Ejerandel som decimaltal: <code>0.25</code> betyder 25 %."],
                    ["<code>ownership_range</code>", "Det interval, CVR registrerer andelen i, fx <code>25-33,32%</code>."],
                    ["<code>type</code>", "<code>PERSON</code>, <code>VIRKSOMHED</code> (med <code>cvr</code>) "
                                          "eller <code>ANDEN_DELTAGER</code>, fx en udenlandsk ejer."],
                ]),
                ("h2", "Find den samlede ejerkæde"),
                ("p", "Når en ejer er en virksomhed, har den selv et CVR-nummer. Så kan du gå et niveau op ad "
                      "gangen:"),
                ("code", "python", """import requests

def owner_chain(cvr: int, depth: int = 0, max_depth: int = 5):
    url = f"{site}/api/v1/{cvr}/direktion-og-ansvarlig"
    data = requests.get(url, timeout=10).json()
    for owner in data["ejere"]:
        share = owner["ownership_percent"] or 0
        print("  " * depth + f"{owner['name']} ({share:.0%})")
        if owner["type"] == "VIRKSOMHED" and owner["cvr"] and depth < max_depth:
            owner_chain(owner["cvr"], depth + 1, max_depth)

owner_chain(24256790)"""),
                ("h2", "Værd at vide"),
                ("ul", [
                    "Kun ejere med mindst 5 % af kapitalen eller stemmerne skal registreres som legale ejere. "
                    "Listen kan derfor være tom for børsnoterede selskaber med spredt ejerskab.",
                    "Ejerandele registreres i intervaller. Brug <code>ownership_range</code>, når du viser "
                    "andelen for brugere.",
                    "Svaret viser kun de nuværende roller – tidligere direktører og ejere er filtreret fra.",
                    "Personoplysninger er persondata. Brug dem kun til det formål, du har lovligt grundlag for.",
                ]),
            ],
            "faq": [
                ("Får jeg også de reelle ejere?",
                 "API'et returnerer de legale ejere fra CVR. Reelle ejere (UBO) registreres separat og "
                 "er ikke en del af svaret."),
                ("Hvorfor er ownership_percent 0.25 og ikke 25?",
                 "Andelen er et decimaltal mellem 0 og 1. Gang med 100 for at få procent."),
                ("Hvad er forskellen på direktion og fuldt ansvarlige?",
                 "Direktionen leder selskabet. Fuldt ansvarlige hæfter personligt for gælden, fx "
                 "interessenter i et I/S eller komplementarer i et K/S."),
            ],
        },
        "en": {
            "title": "Danish Company Owners and Management API – Free",
            "description": (
                "Get legal owners with ownership share and voting rights, plus management and fully "
                "liable participants, for any Danish company. Free CVR API, JSON, no API key."
            ),
            "h1": "Get owners and management of a Danish company",
            "lead": (
                "For KYC, credit checks and onboarding you often need to know who owns and runs a "
                "company. CVR-API gives you the current legal owners with ownership share and voting "
                "rights, the management and the fully liable participants – straight from CVR."
            ),
            "blocks": [
                ("h2", "Two ways to get them"),
                ("p", "The full lookup <code>/api/v1/{cvr}</code> includes the <code>direktion</code>, "
                      "<code>fuldt_ansvarlige</code> and <code>ejere</code> fields. If you only need the "
                      "people, the slim endpoint is faster because it skips production units and company "
                      "details:"),
                ("code", "bash", "curl {site}/api/v1/24256790/direktion-og-ansvarlig"),
                ("h2", "Example response"),
                ("code", "json", _OWNERS_JSON),
                ("h2", "Reading the fields"),
                ("table", ["Field", "Meaning"], [
                    ["<code>direktion</code>", "Current executives (e.g. DIREKTØR or ADM. DIR.)."],
                    ["<code>fuldt_ansvarlige</code>", "Participants with personal liability, e.g. partners in an I/S."],
                    ["<code>ejere</code>", "Legal owners from the ownership register, with share and voting rights."],
                    ["<code>ownership_percent</code>", "Ownership as a decimal: <code>0.25</code> means 25%."],
                    ["<code>ownership_range</code>", "The band CVR records the share in, e.g. <code>25-33,32%</code>."],
                    ["<code>type</code>", "<code>PERSON</code>, <code>VIRKSOMHED</code> (with <code>cvr</code>) "
                                          "or <code>ANDEN_DELTAGER</code>, e.g. a foreign owner."],
                ]),
                ("h2", "Walk the ownership chain"),
                ("p", "When an owner is a company, it has its own CVR number, so you can walk up one level "
                      "at a time:"),
                ("code", "python", """import requests

def owner_chain(cvr: int, depth: int = 0, max_depth: int = 5):
    url = f"{site}/api/v1/{cvr}/direktion-og-ansvarlig"
    data = requests.get(url, timeout=10).json()
    for owner in data["ejere"]:
        share = owner["ownership_percent"] or 0
        print("  " * depth + f"{owner['name']} ({share:.0%})")
        if owner["type"] == "VIRKSOMHED" and owner["cvr"] and depth < max_depth:
            owner_chain(owner["cvr"], depth + 1, max_depth)

owner_chain(24256790)"""),
                ("h2", "Good to know"),
                ("ul", [
                    "Only owners with at least 5% of the capital or votes must be registered as legal owners. "
                    "The list can be empty for listed companies with dispersed ownership.",
                    "Shares are recorded in bands. Use <code>ownership_range</code> when showing the share "
                    "to users.",
                    "The response only contains current roles – former executives and owners are filtered out.",
                    "Names of people are personal data. Only use them for purposes you have a lawful basis for.",
                ]),
            ],
            "faq": [
                ("Do I also get the beneficial owners?",
                 "The API returns the legal owners from CVR. Beneficial owners (UBOs) are registered "
                 "separately and aren't part of the response."),
                ("Why is ownership_percent 0.25 and not 25?",
                 "The share is a decimal between 0 and 1. Multiply by 100 to get a percentage."),
                ("What's the difference between management and fully liable participants?",
                 "Management runs the company. Fully liable participants are personally liable for its "
                 "debts, such as partners in an I/S or general partners in a K/S."),
            ],
        },
    },
    # ------------------------------------------------------------------
    {
        "id": "p-units",
        "family": "usecase",
        "slug": {
            "da": "p-nummer-opslag-api",
            "en": "p-number-production-unit-api",
        },
        "related": ["p-number", "find-by-address", "industry-codes"],
        "da": {
            "title": "P-nummer opslag via API – alle P-enheder for et CVR",
            "description": (
                "Hent alle P-enheder (produktionsenheder) for en dansk virksomhed med P-nummer, adresse, "
                "branche og antal ansatte. Gratis CVR API uden API-nøgle."
            ),
            "h1": "Hent P-enheder og P-numre for en virksomhed",
            "lead": (
                "En virksomhed har ét CVR-nummer, men en P-enhed for hvert fysisk sted, hvor den driver "
                "forretning. Når du slår et CVR-nummer op, får du alle virksomhedens P-enheder med i "
                "feltet p_units."
            ),
            "blocks": [
                ("h2", "Sådan henter du P-enhederne"),
                ("code", "bash", "curl {site}/api/v1/24256790"),
                ("h2", "Eksempel på svar"),
                ("code", "json", _PUNITS_JSON),
                ("h2", "Felterne på en P-enhed"),
                ("table", ["Felt", "Betydning"], [
                    ["<code>p_number</code>", "P-nummeret – 10 cifre."],
                    ["<code>name</code>, <code>address</code>, <code>zipcode</code>, <code>city</code>",
                     "Enhedens navn og fysiske adresse."],
                    ["<code>industrycode</code>, <code>industrydesc</code>", "Branchekode for netop dette sted."],
                    ["<code>employees</code>", "Antal ansatte, når det er indberettet."],
                    ["<code>startdate</code>, <code>enddate</code>", "Hvornår enheden startede og evt. lukkede."],
                    ["<code>protected</code>", "Om P-enheden er reklamebeskyttet."],
                ]),
                ("h2", "Kun aktive P-enheder"),
                ("p", "Listen indeholder også lukkede enheder – store virksomheder kan have hundredvis. "
                      "Filtrér på <code>enddate</code>:"),
                ("code", "javascript", """const res = await fetch("{site}/api/v1/24256790");
const company = await res.json();

const active = company.p_units.filter((p) => !p.enddate);
for (const p of active) {
  console.log(p.p_number, p.address, p.zipcode, p.city, p.employees ?? "-");
}"""),
                ("h2", "Gode råd"),
                ("ul", [
                    "Opslaget henter alle P-enheder, så store koncerner giver store svar. Har du kun brug for "
                    "ejere og direktion, så brug <code>/api/v1/{cvr}/direktion-og-ansvarlig</code>.",
                    "Reklamebeskyttelse gælder pr. P-enhed. En virksomhed kan være åben for reklame, mens en "
                    "enkelt P-enhed er beskyttet.",
                    "Brancheteksten på en P-enhed kan afvige fra virksomhedens hovedbranche.",
                ]),
            ],
            "faq": [
                ("Kan jeg slå et P-nummer op direkte?",
                 "Ikke endnu. Slå virksomhedens CVR-nummer op, og find P-enheden i <code>p_units</code>."),
                ("Hvorfor har en virksomhed lukkede P-enheder med?",
                 "Listen er virksomhedens fulde historik. Enheder med en <code>enddate</code> er lukket."),
            ],
        },
        "en": {
            "title": "P-Number Lookup API – All Production Units for a CVR",
            "description": (
                "Get every production unit (P-number) for a Danish company with address, industry and "
                "headcount. Free CVR API with no API key."
            ),
            "h1": "Get production units and P-numbers for a company",
            "lead": (
                "A Danish company has one CVR number, but a production unit (P-unit) for every physical "
                "site it operates from. When you look up a CVR number, all of the company's production "
                "units come back in the p_units field."
            ),
            "blocks": [
                ("h2", "Fetching the production units"),
                ("code", "bash", "curl {site}/api/v1/24256790"),
                ("h2", "Example response"),
                ("code", "json", _PUNITS_JSON),
                ("h2", "Production-unit fields"),
                ("table", ["Field", "Meaning"], [
                    ["<code>p_number</code>", "The P-number – 10 digits."],
                    ["<code>name</code>, <code>address</code>, <code>zipcode</code>, <code>city</code>",
                     "The unit's name and physical address."],
                    ["<code>industrycode</code>, <code>industrydesc</code>", "Industry code for this specific site."],
                    ["<code>employees</code>", "Headcount, when reported."],
                    ["<code>startdate</code>, <code>enddate</code>", "When the unit opened and, if so, closed."],
                    ["<code>protected</code>", "Whether the unit has marketing protection."],
                ]),
                ("h2", "Active units only"),
                ("p", "The list includes closed units too – large companies can have hundreds. Filter on "
                      "<code>enddate</code>:"),
                ("code", "javascript", """const res = await fetch("{site}/api/v1/24256790");
const company = await res.json();

const active = company.p_units.filter((p) => !p.enddate);
for (const p of active) {
  console.log(p.p_number, p.address, p.zipcode, p.city, p.employees ?? "-");
}"""),
                ("h2", "Tips"),
                ("ul", [
                    "The lookup fetches every production unit, so large groups mean large responses. If you "
                    "only need owners and management, use <code>/api/v1/{cvr}/direktion-og-ansvarlig</code>.",
                    "Marketing protection applies per unit. A company can accept marketing while one of its "
                    "units is protected.",
                    "A unit's industry can differ from the company's main industry.",
                ]),
            ],
            "faq": [
                ("Can I look up a P-number directly?",
                 "Not yet. Look up the company's CVR number and find the unit in <code>p_units</code>."),
                ("Why does a company include closed production units?",
                 "The list is the company's full history. Units with an <code>enddate</code> are closed."),
            ],
        },
    },
    # ------------------------------------------------------------------
    {
        "id": "validate-cvr",
        "family": "usecase",
        "slug": {
            "da": "valider-cvr-nummer",
            "en": "validate-cvr-number",
        },
        "related": ["cvr-number", "react-form", "woocommerce"],
        "da": {
            "title": "Validér CVR-nummer – modulus 11 og live opslag",
            "description": (
                "Sådan validerer du et dansk CVR-nummer: tjek de 8 cifre med modulus 11, og bekræft "
                "derefter med et gratis API-opslag, at virksomheden findes og er aktiv."
            ),
            "h1": "Sådan validerer du et CVR-nummer",
            "lead": (
                "Et gyldigt CVR-nummer skal bestå to tjek: det skal have det rigtige format med korrekt "
                "kontrolciffer, og det skal tilhøre en virksomhed, der findes og stadig er aktiv. Det "
                "første klarer du lokalt, det andet med ét API-kald."
            ),
            "blocks": [
                ("h2", "1. Tjek formatet med modulus 11"),
                ("p", "Et CVR-nummer har 8 cifre og starter ikke med 0. Gang hvert ciffer med vægtene "
                      "<code>2, 7, 6, 5, 4, 3, 2, 1</code>, og læg resultaterne sammen. Summen skal gå op i 11."),
                ("p", "Eksempel for 10403782: 1·2 + 0·7 + 4·6 + 0·5 + 3·4 + 7·3 + 8·2 + 2·1 = 77, og "
                      "77 / 11 = 7. Nummeret er altså gyldigt."),
                ("code", "python", _MOD11_PY),
                ("h2", "2. Bekræft at virksomheden findes"),
                ("p", "Et nummer kan have korrekt kontrolciffer uden at være tildelt. Slå det op:"),
                ("code", "bash", "curl {site}/api/v1/10403782"),
                ("code", "json", _VALIDATE_JSON),
                ("p", "Findes nummeret ikke, svarer API'et med HTTP 404:"),
                ("code", "json", _NOT_FOUND_JSON),
                ("h2", "3. Tjek at den er aktiv"),
                ("p", "En virksomhed kan findes i CVR, selvom den er ophørt eller gået konkurs. Kig på "
                      "<code>enddate</code> (sat, når virksomheden er ophørt), <code>bankrupt</code> og "
                      "<code>status</code>. Her er hele flowet i JavaScript:"),
                ("code", "javascript", _MOD11_JS),
                ("h2", "Gode råd"),
                ("ul", [
                    "Kør modulus 11-tjekket i browseren, så brugeren får besked med det samme – og spar "
                    "API-kaldet på oplagte tastefejl.",
                    "Fjern mellemrum og et evt. <code>DK</code>-præfiks (fra momsnumre) før validering.",
                    "Brug <code>enddate</code> og <code>bankrupt</code> frem for at matche på tekst i "
                    "<code>status</code>, som kan have mange forskellige værdier.",
                ]),
            ],
            "faq": [
                ("Er alle CVR-numre, der består modulus 11, tildelt?",
                 "Nej. Modulus 11 fanger tastefejl, men kun et opslag i CVR kan bekræfte, at nummeret "
                 "tilhører en virksomhed."),
                ("Er CVR-nummer og momsnummer det samme?",
                 "For danske virksomheder er momsnummeret som regel CVR-nummeret med <code>DK</code> foran, "
                 "fx DK10403782."),
                ("Hvad svarer API'et ved et ugyldigt format?",
                 "Indeholder nummeret andet end cifre, svarer API'et med HTTP 422. Findes nummeret ikke, "
                 "svarer det med HTTP 404 og fejlkoden <code>NOT_FOUND</code>."),
            ],
        },
        "en": {
            "title": "Validate a Danish CVR Number – Mod 11 and Live Lookup",
            "description": (
                "How to validate a Danish CVR number: check the 8 digits with modulus 11, then confirm "
                "with a free API lookup that the company exists and is still active."
            ),
            "h1": "How to validate a Danish CVR number",
            "lead": (
                "A valid CVR number has to pass two checks: it must have the right format with a correct "
                "check digit, and it must belong to a company that exists and is still active. You do the "
                "first locally and the second with one API call."
            ),
            "blocks": [
                ("h2", "1. Check the format with modulus 11"),
                ("p", "A CVR number has 8 digits and doesn't start with 0. Multiply each digit by the "
                      "weights <code>2, 7, 6, 5, 4, 3, 2, 1</code> and add up the results. The sum must be "
                      "divisible by 11."),
                ("p", "For 10403782: 1·2 + 0·7 + 4·6 + 0·5 + 3·4 + 7·3 + 8·2 + 2·1 = 77, and 77 / 11 = 7, "
                      "so the number is valid."),
                ("code", "python", _MOD11_PY),
                ("h2", "2. Confirm the company exists"),
                ("p", "A number can have a correct check digit without being assigned. Look it up:"),
                ("code", "bash", "curl {site}/api/v1/10403782"),
                ("code", "json", _VALIDATE_JSON),
                ("p", "If the number doesn't exist, the API responds with HTTP 404:"),
                ("code", "json", _NOT_FOUND_JSON),
                ("h2", "3. Check that it's active"),
                ("p", "A company can exist in CVR even though it has ceased or gone bankrupt. Look at "
                      "<code>enddate</code> (set once the company has ceased), <code>bankrupt</code> and "
                      "<code>status</code>. Here's the whole flow in JavaScript:"),
                ("code", "javascript", _MOD11_JS),
                ("h2", "Tips"),
                ("ul", [
                    "Run the modulus 11 check in the browser so users get instant feedback – and you save "
                    "the API call on obvious typos.",
                    "Strip spaces and any <code>DK</code> prefix (from VAT numbers) before validating.",
                    "Rely on <code>enddate</code> and <code>bankrupt</code> rather than matching text in "
                    "<code>status</code>, which can take many different values.",
                ]),
            ],
            "faq": [
                ("Is every CVR number that passes modulus 11 assigned?",
                 "No. Modulus 11 catches typos, but only a CVR lookup can confirm that the number "
                 "belongs to a company."),
                ("Is a CVR number the same as a Danish VAT number?",
                 "For Danish companies, the VAT number is usually the CVR number prefixed with "
                 "<code>DK</code>, e.g. DK10403782."),
                ("What does the API return for an invalid format?",
                 "If the number contains anything but digits, the API responds with HTTP 422. If it "
                 "doesn't exist, it responds with HTTP 404 and the error code <code>NOT_FOUND</code>."),
            ],
        },
    },
]
