"""Comparison guides: CVR API options side by side, migrating from cvrapi.dk, and System-til-System.

Facts about other services were checked against their public docs in
November 2026. Keep claims to what their docs state, and re-check before
editing a row.
"""

_CHECKED_DA = "Oplysningerne om andre tjenester er tjekket mod deres offentlige dokumentation i november 2026. Tjek altid deres egne sider for aktuelle priser og vilkår."
_CHECKED_EN = "Details about other services were checked against their public documentation in November 2026. Always check their own sites for current prices and terms."

_ES_QUERY = """\
curl -u "$CVR_USER:$CVR_PASSWORD" \\
  -H "Content-Type: application/json" \\
  -X POST "http://distribution.virk.dk/cvr-permanent/virksomhed/_search" \\
  -d '{
    "query": { "term": { "Vrvirksomhed.cvrNummer": 24256790 } },
    "size": 1
  }'

# Svaret er hele CVR-dokumentet: navne, adresser, deltagere og
# attributter som historiske lister med gyldighedsperioder."""

_ES_QUERY_EN = _ES_QUERY.replace(
    "# Svaret er hele CVR-dokumentet: navne, adresser, deltagere og\n# attributter som historiske lister med gyldighedsperioder.",
    "# The response is the full CVR document: names, addresses, participants\n# and attributes as historical lists with validity periods.",
)

_ES_NAME_PY = """\
# Find det navn, der gælder i dag, i det rå System-til-System-svar
def current_name(vrvirksomhed):
    for navn in vrvirksomhed["navne"]:
        if navn["periode"]["gyldigTil"] is None:
            return navn["navn"]
    return None"""

_ES_NAME_PY_EN = _ES_NAME_PY.replace(
    "# Find det navn, der gælder i dag, i det rå System-til-System-svar",
    "# Find the name that is valid today in the raw System-til-System response",
)

_APICVR_ONE_LINER = """\
curl {site}/api/v1/24256790

{
  "vat": 24256790,
  "name": "NOVO NORDISK A/S",
  "address": "Novo Allé 1",
  "zipcode": 2880,
  "city": "Bagsværd",
  "status": "NORMAL",
  ...
}"""

_MIGRATE_URLS = """\
# cvrapi.dk
https://cvrapi.dk/api?search=24256790&country=dk
https://cvrapi.dk/api?name=novo%20nordisk&country=dk
https://cvrapi.dk/api?phone=44448888&country=dk

# apicvr.dk
{site}/api/v1/24256790
{site}/api/v1/search/company/novo%20nordisk?limit=1
{site}/api/v1/search/phone/44448888"""

_MIGRATE_PHP = """\
<?php
// Drop-in: returnerer det samme format, som din cvrapi.dk-kode forventer.
function cvr_lookup(string $cvr): ?array
{
    $ch = curl_init("{site}/api/v1/" . urlencode($cvr));
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
    $body = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($status === 404) {
        return ['error' => 'NOT_FOUND'];
    }
    if ($status !== 200) {
        return ['error' => 'INTERNAL_ERROR'];
    }

    $c = json_decode($body, true);

    // Omdøb de felter, der hedder noget andet hos apicvr.dk
    $c['productionunits'] = $c['p_units'];
    $c['owners'] = array_map(fn ($o) => ['name' => $o['name']], $c['ejere']);
    $c['creditbankrupt'] = $c['bankrupt'];
    $c['zipcode'] = (string) $c['zipcode'];

    return $c;
}

$company = cvr_lookup('24256790');
echo $company['name'] . ', ' . $company['zipcode'] . ' ' . $company['city'];"""

_MIGRATE_PHP_EN = (
    _MIGRATE_PHP
    .replace("// Drop-in: returnerer det samme format, som din cvrapi.dk-kode forventer.",
             "// Drop-in: returns the same shape your cvrapi.dk code expects.")
    .replace("// Omdøb de felter, der hedder noget andet hos apicvr.dk",
             "// Rename the fields that are named differently on apicvr.dk")
)

_MIGRATE_JS = """\
async function cvrLookup(cvr) {
  const res = await fetch(`{site}/api/v1/${cvr}`);
  if (res.status === 404) return { error: "NOT_FOUND" };
  if (!res.ok) return { error: "INTERNAL_ERROR" };

  const c = await res.json();
  return {
    ...c,
    productionunits: c.p_units,
    owners: c.ejere.map((o) => ({ name: o.name })),
    creditbankrupt: c.bankrupt,
    zipcode: String(c.zipcode),
  };
}"""


def _comparison_table(lang):
    if lang == "da":
        return ("table", ["", "apicvr.dk", "cvrapi.dk", "cvr.dev", "System-til-System (ERST)"], [
            ["Pris", "Gratis", "Gratis op til 50 opslag pr. dag", "Betalt abonnement, 30 dages prøveperiode", "Gratis, men kræver ansøgning og godkendelse"],
            ["Adgang", "Ingen nøgle, ingen konto", "Ingen nøgle; eget User-Agent påkrævet", "API-nøgle (demo uden nøgle)", "Brugernavn og adgangskode fra Erhvervsstyrelsen"],
            ["Grænse", "Fair use, ingen fast dagskvote", "50 opslag pr. IP pr. dag (<code>QUOTA_EXCEEDED</code>)", "Efter abonnement", "Efter Erhvervsstyrelsens vilkår"],
            ["Format", "Fladt, stabilt JSON", "JSON eller XML", "JSON, OpenAPI 3.0", "Rå Elasticsearch-dokumenter med fuld historik"],
            ["Ejere og direktion", "Ja: ejere med andel og stemmeret, direktion, fuldt ansvarlige", "Ejere (navn)", "Ja, inkl. ejerskabshierarki", "Ja, i rå form"],
            ["Søg på email, domæne og adresse", "Ja", "Nej (CVR, navn, P-nummer, telefon)", "Se deres dokumentation", "Ja, hvis du selv skriver forespørgslen"],
            ["Regnskaber og XBRL", "Nej", "Nej", "Ja", "Separat indeks"],
            ["Norske virksomheder", "Nej", "Ja", "Nej", "Nej"],
            ["Kildekode", "Open source (MIT)", "Lukket", "Lukket", "–"],
        ])
    return ("table", ["", "apicvr.dk", "cvrapi.dk", "cvr.dev", "System-til-System (ERST)"], [
        ["Price", "Free", "Free up to 50 lookups per day", "Paid subscription, 30-day trial", "Free, but requires an application and approval"],
        ["Access", "No key, no account", "No key; custom User-Agent required", "API key (demo without key)", "Username and password from the Danish Business Authority"],
        ["Limit", "Fair use, no fixed daily quota", "50 lookups per IP per day (<code>QUOTA_EXCEEDED</code>)", "Depends on plan", "Per the Business Authority's terms"],
        ["Format", "Flat, stable JSON", "JSON or XML", "JSON, OpenAPI 3.0", "Raw Elasticsearch documents with full history"],
        ["Owners and management", "Yes: owners with share and voting rights, management, fully liable", "Owners (name)", "Yes, incl. ownership hierarchy", "Yes, in raw form"],
        ["Search by email, domain and address", "Yes", "No (CVR, name, P-number, phone)", "See their docs", "Yes, if you write the query yourself"],
        ["Annual reports and XBRL", "No", "No", "Yes", "Separate index"],
        ["Norwegian companies", "No", "Yes", "No", "No"],
        ["Source code", "Open source (MIT)", "Closed", "Closed", "–"],
    ])


PAGES = [
    # --- Comparison ---------------------------------------------------------
    {
        "id": "comparison",
        "updated": "2026-11-06",
        "family": "compare",
        "slug": {"da": "cvr-api-sammenligning", "en": "cvr-api-comparison"},
        "related": ["migrate-cvrapi", "system-til-system", "owners-management"],
        "da": {
            "title": "CVR API sammenligning: apicvr.dk, cvrapi.dk og cvr.dev",
            "description": (
                "Sammenlign danske CVR API'er: pris, API-nøgle, opslag pr. dag, ejere, søgning og "
                "regnskaber. apicvr.dk, cvrapi.dk, cvr.dev og System-til-System side om side."
            ),
            "h1": "CVR API'er sammenlignet",
            "lead": (
                "Der findes flere måder at hente data fra CVR-registret på. De adskiller sig mest på pris, "
                "adgang, grænser og hvor meget data du får. Her er de fire mest brugte side om side, så du "
                "kan vælge den, der passer til dit projekt."
            ),
            "blocks": [
                ("h2", "Overblik"),
                _comparison_table("da"),
                ("note", _CHECKED_DA),
                ("h2", "Hvornår skal du vælge hvad?"),
                ("ul", [
                    "<strong>apicvr.dk</strong>, hvis du vil i gang med det samme uden nøgle og konto, skal "
                    "bruge ejere og direktion, eller vil søge på email, domæne, telefon eller adresse.",
                    "<strong>cvr.dev</strong>, hvis du skal bruge regnskabstal, XBRL eller ejerskabshierarkier "
                    "og har budget til et abonnement.",
                    "<strong>cvrapi.dk</strong>, hvis du også skal slå norske virksomheder op, eller hvis du har "
                    "brug for XML, og 50 opslag om dagen er nok.",
                    "<strong>System-til-System</strong>, hvis du skal bruge hele registret, historik eller "
                    "masseudtræk og selv vil vedligeholde koden til Elasticsearch.",
                ]),
                ("h2", "Den største forskel: grænser og adgang"),
                ("p", "Med cvrapi.dk er den gratis kvote 50 opslag pr. IP-adresse om dagen, og du skal sende et "
                      "User-Agent med dit firmanavn og projekt, ellers får du fejlen <code>INVALID_UA</code>. "
                      "cvr.dev kræver en API-nøgle til andet end demo. apicvr.dk kræver ingenting: et GET-kald "
                      "er nok, og der er ingen fast dagskvote, kun fair use."),
                ("code", "bash", "curl {site}/api/v1/24256790"),
                ("h2", "Dataformat"),
                ("p", "apicvr.dk og cvrapi.dk giver et fladt JSON-objekt med de aktuelle oplysninger. Feltnavnene "
                      "ligner hinanden meget, så det er let at skifte. Se "
                      "<a href=\"/guides/skift-fra-cvrapi-dk\">guiden til at skifte fra cvrapi.dk</a>. "
                      "System-til-System giver det rå dokument med historik for hvert felt, som du selv skal "
                      "pakke ud."),
                ("h2", "Hvad apicvr.dk ikke kan"),
                ("ul", [
                    "Regnskaber, nøgletal og XBRL-data er ikke med.",
                    "Kun danske virksomheder. Norske virksomheder findes ikke i CVR.",
                    "Svaret viser den aktuelle situation, ikke historik over tidligere navne, adresser og ejere.",
                ]),
            ],
            "faq": [
                ("Hvilket CVR API er gratis?",
                 "apicvr.dk er gratis uden kvote og uden nøgle. cvrapi.dk er gratis op til 50 opslag om dagen. "
                 "System-til-System er gratis, men kræver ansøgning hos Erhvervsstyrelsen. cvr.dev er betalt."),
                ("Hvilket CVR API har regnskabsdata?",
                 "Af de fire er det cvr.dev, der leverer regnskaber og XBRL via API. Erhvervsstyrelsen har "
                 "også regnskaberne i et separat indeks."),
                ("Er der et alternativ til cvrapi.dk uden 50 opslags-grænsen?",
                 "Ja. apicvr.dk har næsten de samme feltnavne og ingen fast dagskvote. Se guiden til at skifte."),
            ],
        },
        "en": {
            "title": "CVR API Comparison: apicvr.dk, cvrapi.dk and cvr.dev",
            "description": (
                "Compare Danish CVR APIs: price, API key, daily limits, owners, search and annual reports. "
                "apicvr.dk, cvrapi.dk, cvr.dev and System-til-System side by side."
            ),
            "h1": "Danish CVR APIs compared",
            "lead": (
                "There are several ways to get data from the Danish CVR register. They differ most on price, "
                "access, limits and how much data you get. Here are the four most used side by side, so you can "
                "pick the one that fits your project."
            ),
            "blocks": [
                ("h2", "Overview"),
                _comparison_table("en"),
                ("note", _CHECKED_EN),
                ("h2", "Which one should you pick?"),
                ("ul", [
                    "<strong>apicvr.dk</strong> if you want to start right away with no key or account, need "
                    "owners and management, or want to search by email, domain, phone or address.",
                    "<strong>cvr.dev</strong> if you need financial statements, XBRL or ownership hierarchies "
                    "and have budget for a subscription.",
                    "<strong>cvrapi.dk</strong> if you also need Norwegian companies or XML, and 50 lookups a "
                    "day is enough.",
                    "<strong>System-til-System</strong> if you need the whole register, history or bulk "
                    "extracts and are happy to maintain your own Elasticsearch code.",
                ]),
                ("h2", "The biggest difference: limits and access"),
                ("p", "On cvrapi.dk the free quota is 50 lookups per IP address per day, and you must send a "
                      "User-Agent with your company and project name, or you get an <code>INVALID_UA</code> error. "
                      "cvr.dev needs an API key for anything beyond the demo. apicvr.dk needs nothing: a GET "
                      "request is enough, and there's no fixed daily quota, just fair use."),
                ("code", "bash", "curl {site}/api/v1/24256790"),
                ("h2", "Data format"),
                ("p", "apicvr.dk and cvrapi.dk return a flat JSON object with current details. The field names are "
                      "very similar, so switching is easy. See the "
                      "<a href=\"/en/guides/migrate-from-cvrapi-dk\">guide to switching from cvrapi.dk</a>. "
                      "System-til-System returns the raw document with history for every field, which you have "
                      "to unpack yourself."),
                ("h2", "What apicvr.dk doesn't do"),
                ("ul", [
                    "Financial statements, key figures and XBRL data aren't included.",
                    "Danish companies only. Norwegian companies aren't in CVR.",
                    "The response shows the current situation, not the history of past names, addresses and owners.",
                ]),
            ],
            "faq": [
                ("Which CVR API is free?",
                 "apicvr.dk is free with no quota and no key. cvrapi.dk is free up to 50 lookups a day. "
                 "System-til-System is free but requires an application to the Danish Business Authority. "
                 "cvr.dev is paid."),
                ("Which CVR API has financial data?",
                 "Of the four, cvr.dev provides financial statements and XBRL via API. The Danish Business "
                 "Authority also has them in a separate index."),
                ("Is there a cvrapi.dk alternative without the 50-lookup limit?",
                 "Yes. apicvr.dk uses almost the same field names and has no fixed daily quota. See the "
                 "migration guide."),
            ],
        },
    },
    # --- Migrate from cvrapi.dk ----------------------------------------------
    {
        "id": "migrate-cvrapi",
        "updated": "2026-11-06",
        "family": "compare",
        "slug": {"da": "skift-fra-cvrapi-dk", "en": "migrate-from-cvrapi-dk"},
        "related": ["comparison", "php", "javascript"],
        "da": {
            "title": "Skift fra cvrapi.dk: gratis alternativ uden dagskvote",
            "description": (
                "Rammer du cvrapi.dk's grænse på 50 opslag om dagen? Skift til apicvr.dk på få minutter. "
                "URL'er, feltnavne og en drop-in-funktion til PHP og JavaScript."
            ),
            "h1": "Skift fra cvrapi.dk til apicvr.dk",
            "lead": (
                "apicvr.dk bruger næsten de samme feltnavne som cvrapi.dk, så de fleste integrationer kan "
                "skiftes ved at ændre URL'en og omdøbe tre felter. Til gengæld slipper du for kvoten på 50 "
                "opslag om dagen og kravet om et særligt User-Agent."
            ),
            "blocks": [
                ("h2", "Hvorfor skifte?"),
                ("ul", [
                    "<strong>Ingen dagskvote:</strong> cvrapi.dk giver 50 gratis opslag pr. IP om dagen og "
                    "svarer derefter med <code>QUOTA_EXCEEDED</code>. apicvr.dk har ingen fast kvote, kun fair use.",
                    "<strong>Intet User-Agent-krav:</strong> du får ikke <code>INVALID_UA</code>, fordi du "
                    "glemte at sætte et.",
                    "<strong>Mere data:</strong> ejere med ejerandel og stemmeret, direktion og fuldt ansvarlige.",
                    "<strong>Flere søgninger:</strong> email, emaildomæne, adresse og fejltolerant navnesøgning.",
                ]),
                ("h2", "URL'erne"),
                ("code", "text", _MIGRATE_URLS),
                ("p", "Bemærk, at søgning på navn og telefon hos apicvr.dk returnerer en liste. Tag det første "
                      "element, hvis du kun vil have ét hit som hos cvrapi.dk."),
                ("h2", "Felter, der hedder det samme"),
                ("p", "<code>vat</code>, <code>name</code>, <code>address</code>, <code>zipcode</code>, "
                      "<code>city</code>, <code>cityname</code>, <code>addressco</code>, <code>protected</code>, "
                      "<code>phone</code>, <code>email</code>, <code>fax</code>, <code>startdate</code>, "
                      "<code>enddate</code>, <code>employees</code>, <code>industrycode</code>, "
                      "<code>industrydesc</code>, <code>companycode</code>, <code>companydesc</code> og "
                      "<code>version</code>."),
                ("h2", "Felter, der er anderledes"),
                ("table", ["cvrapi.dk", "apicvr.dk", "Bemærk"], [
                    ["<code>productionunits</code>", "<code>p_units</code>", "P-nummeret ligger i <code>p_number</code>."],
                    ["<code>owners</code>", "<code>ejere</code>", "Hver ejer har også <code>type</code>, <code>cvr</code>, ejerandel og stemmeret."],
                    ["<code>creditbankrupt</code>", "<code>bankrupt</code>", "Samme betydning."],
                    ["<code>creditstatus</code>, <code>creditstartdate</code>", "<code>status</code>", "Fx <code>NORMAL</code>, <code>UNDERKONKURS</code> eller <code>OPHØRT</code>."],
                    ["<code>zipcode</code> (tekst)", "<code>zipcode</code> (tal)", "Konverter til tekst, hvis din kode forventer det."],
                    ["–", "<code>direktion</code>, <code>fuldt_ansvarlige</code>", "Nye felter."],
                ]),
                ("h2", "Fejl"),
                ("p", "cvrapi.dk lægger fejlen i et <code>error</code>-felt. apicvr.dk bruger HTTP-statuskoder: "
                      "<code>404</code> når virksomheden ikke findes, og <code>502</code> når CVR-registret ikke "
                      "svarer. Koden står i <code>detail.error</code>."),
                ("h2", "Drop-in-funktion i PHP"),
                ("p", "Funktionen henter fra apicvr.dk og returnerer det format, din eksisterende kode forventer. "
                      "Så kan du skifte uden at røre resten af koden."),
                ("code", "php", _MIGRATE_PHP),
                ("h2", "Drop-in-funktion i JavaScript"),
                ("code", "javascript", _MIGRATE_JS),
                ("h2", "Det kan apicvr.dk ikke"),
                ("ul", [
                    "Norske virksomheder (<code>country=no</code>).",
                    "XML-format. Svaret er altid JSON.",
                    "Opslag direkte på P-nummer (<code>produ</code>). Søg på virksomheden, og find P-enheden i "
                    "<code>p_units</code>.",
                ]),
            ],
            "faq": [
                ("Skal jeg sætte et User-Agent?",
                 "Nej, det er ikke påkrævet. Du må gerne sende et, der beskriver dit projekt."),
                ("Kan jeg beholde min cvrapi.dk-kode?",
                 "Ja, hvis du bruger drop-in-funktionen ovenfor. Den omdøber felterne, så resten af koden virker uændret."),
                ("Hvor mange opslag må jeg lave?",
                 "Der er ingen fast dagskvote. Hold et rimeligt tempo, og skriv til noah@noahbohme.com, hvis du "
                 "skal bruge vedvarende høj trafik."),
            ],
        },
        "en": {
            "title": "Migrate from cvrapi.dk: Free Alternative, No Daily Quota",
            "description": (
                "Hitting cvrapi.dk's 50 lookups-a-day limit? Switch to apicvr.dk in minutes. URLs, field names "
                "and a drop-in function for PHP and JavaScript."
            ),
            "h1": "Switch from cvrapi.dk to apicvr.dk",
            "lead": (
                "apicvr.dk uses almost the same field names as cvrapi.dk, so most integrations can switch by "
                "changing the URL and renaming three fields. In return you lose the 50 lookups-a-day quota and "
                "the custom User-Agent requirement."
            ),
            "blocks": [
                ("h2", "Why switch?"),
                ("ul", [
                    "<strong>No daily quota:</strong> cvrapi.dk gives 50 free lookups per IP per day and then "
                    "answers <code>QUOTA_EXCEEDED</code>. apicvr.dk has no fixed quota, just fair use.",
                    "<strong>No User-Agent requirement:</strong> you won't get <code>INVALID_UA</code> for "
                    "forgetting to set one.",
                    "<strong>More data:</strong> owners with ownership share and voting rights, management and "
                    "fully liable participants.",
                    "<strong>More searches:</strong> email, email domain, address and typo-tolerant name search.",
                ]),
                ("h2", "The URLs"),
                ("code", "text", _MIGRATE_URLS),
                ("p", "Note that name and phone search on apicvr.dk return a list. Take the first item if you "
                      "only want one hit like on cvrapi.dk."),
                ("h2", "Fields with the same name"),
                ("p", "<code>vat</code>, <code>name</code>, <code>address</code>, <code>zipcode</code>, "
                      "<code>city</code>, <code>cityname</code>, <code>addressco</code>, <code>protected</code>, "
                      "<code>phone</code>, <code>email</code>, <code>fax</code>, <code>startdate</code>, "
                      "<code>enddate</code>, <code>employees</code>, <code>industrycode</code>, "
                      "<code>industrydesc</code>, <code>companycode</code>, <code>companydesc</code> and "
                      "<code>version</code>."),
                ("h2", "Fields that differ"),
                ("table", ["cvrapi.dk", "apicvr.dk", "Note"], [
                    ["<code>productionunits</code>", "<code>p_units</code>", "The P-number is in <code>p_number</code>."],
                    ["<code>owners</code>", "<code>ejere</code>", "Each owner also has <code>type</code>, <code>cvr</code>, ownership share and voting rights."],
                    ["<code>creditbankrupt</code>", "<code>bankrupt</code>", "Same meaning."],
                    ["<code>creditstatus</code>, <code>creditstartdate</code>", "<code>status</code>", "E.g. <code>NORMAL</code>, <code>UNDERKONKURS</code> or <code>OPHØRT</code>."],
                    ["<code>zipcode</code> (string)", "<code>zipcode</code> (number)", "Cast to string if your code expects it."],
                    ["–", "<code>direktion</code>, <code>fuldt_ansvarlige</code>", "New fields."],
                ]),
                ("h2", "Errors"),
                ("p", "cvrapi.dk puts the error in an <code>error</code> field. apicvr.dk uses HTTP status codes: "
                      "<code>404</code> when the company doesn't exist and <code>502</code> when the CVR register "
                      "doesn't answer. The code is in <code>detail.error</code>."),
                ("h2", "Drop-in function in PHP"),
                ("p", "The function fetches from apicvr.dk and returns the shape your existing code expects, so you "
                      "can switch without touching the rest of your code."),
                ("code", "php", _MIGRATE_PHP_EN),
                ("h2", "Drop-in function in JavaScript"),
                ("code", "javascript", _MIGRATE_JS),
                ("h2", "What apicvr.dk doesn't do"),
                ("ul", [
                    "Norwegian companies (<code>country=no</code>).",
                    "XML. The response is always JSON.",
                    "Direct lookup by P-number (<code>produ</code>). Look up the company and find the unit in "
                    "<code>p_units</code>.",
                ]),
            ],
            "faq": [
                ("Do I need to set a User-Agent?",
                 "No, it's not required. You're welcome to send one that describes your project."),
                ("Can I keep my cvrapi.dk code?",
                 "Yes, if you use the drop-in function above. It renames the fields so the rest of your code "
                 "works unchanged."),
                ("How many lookups can I make?",
                 "There's no fixed daily quota. Keep a reasonable pace, and email noah@noahbohme.com if you need "
                 "sustained heavy traffic."),
            ],
        },
    },
    # --- System-til-System -----------------------------------------------------
    {
        "id": "system-til-system",
        "updated": "2026-11-06",
        "family": "compare",
        "slug": {"da": "cvr-system-til-system", "en": "cvr-system-til-system-access"},
        "related": ["comparison", "cvr-number", "python"],
        "da": {
            "title": "CVR System-til-System vs. CVR API: hvad skal du vælge?",
            "description": (
                "Hvad er Erhvervsstyrelsens System-til-System-adgang til CVR, hvordan ser en forespørgsel ud, "
                "og hvornår er et færdigt CVR API det nemmeste valg?"
            ),
            "h1": "CVR System-til-System eller et CVR API?",
            "lead": (
                "Erhvervsstyrelsen udstiller hele CVR-registret som et Elasticsearch-indeks på "
                "distribution.virk.dk. Det kaldes System-til-System-adgang. Det er gratis og komplet, men "
                "kræver ansøgning, og svarene er tunge at arbejde med. apicvr.dk bygger ovenpå og giver dig "
                "de samme data som simpelt JSON."
            ),
            "blocks": [
                ("h2", "Hvad er System-til-System?"),
                ("p", "System-til-System er Erhvervsstyrelsens officielle distribution af CVR-data. Du får et "
                      "brugernavn og en adgangskode og sender Elasticsearch-forespørgsler til indeksene "
                      "<code>cvr-permanent/virksomhed</code>, <code>cvr-permanent/produktionsenhed</code> og "
                      "<code>cvr-permanent/deltager</code>. Svarene indeholder hele historikken for hver virksomhed."),
                ("h2", "Sådan ser et opslag ud"),
                ("code", "bash", _ES_QUERY),
                ("p", "Hvert felt er en liste med gyldighedsperioder. Vil du have det nuværende navn, skal du selv "
                      "finde den periode, der stadig gælder:"),
                ("code", "python", _ES_NAME_PY),
                ("p", "Det samme gælder adresser, branchekoder, status, ansatte og ikke mindst deltagerrelationer, "
                      "hvor ejere og direktion ligger gemt i flere lag."),
                ("h2", "Det samme opslag med apicvr.dk"),
                ("code", "bash", _APICVR_ONE_LINER),
                ("p", "apicvr.dk sender forespørgslen til System-til-System for dig, plukker de gældende værdier ud "
                      "og returnerer et fladt objekt. Ingen ansøgning, ingen adgangskode."),
                ("h2", "Hvornår skal du bruge System-til-System selv?"),
                ("ul", [
                    "Du skal bruge historik: tidligere navne, adresser, ejere eller direktører.",
                    "Du skal lave masseudtræk, fx alle virksomheder i en branche eller kommune.",
                    "Du skal bruge felter, som apicvr.dk ikke returnerer.",
                    "Du vil ikke være afhængig af en tredjepart.",
                ]),
                ("p", "Til almindelige opslag i en webshop, et CRM, en onboarding eller et regneark er et færdigt "
                      "API som apicvr.dk hurtigere at komme i gang med og lettere at vedligeholde."),
                ("note", "Kildekoden til apicvr.dk er open source. Har du selv System-til-System-adgang, kan du "
                         "køre din egen instans med Docker. Se <a href=\"https://github.com/NoahBohme/apicvr.dk\">GitHub</a>."),
            ],
            "faq": [
                ("Hvordan får jeg System-til-System-adgang?",
                 "Du ansøger hos Erhvervsstyrelsen og accepterer deres vilkår. Når ansøgningen er godkendt, får du "
                 "et brugernavn og en adgangskode til distribution.virk.dk."),
                ("Er System-til-System gratis?",
                 "Ja, adgangen er gratis, men den kræver godkendelse og en teknisk integration med Elasticsearch."),
                ("Bruger apicvr.dk de samme data?",
                 "Ja. Hvert opslag går live til distribution.virk.dk, så du får de samme aktuelle oplysninger."),
            ],
        },
        "en": {
            "title": "CVR System-til-System vs. a CVR API: Which to Use?",
            "description": (
                "What is the Danish Business Authority's System-til-System access to CVR, what does a query look "
                "like, and when is a ready-made CVR API the easier choice?"
            ),
            "h1": "CVR System-til-System or a CVR API?",
            "lead": (
                "The Danish Business Authority publishes the entire CVR register as an Elasticsearch index on "
                "distribution.virk.dk. It's called System-til-System (system-to-system) access. It's free and "
                "complete, but needs an application, and the responses are heavy to work with. apicvr.dk is "
                "built on top of it and gives you the same data as simple JSON."
            ),
            "blocks": [
                ("h2", "What is System-til-System?"),
                ("p", "System-til-System is the Business Authority's official CVR data distribution. You get a "
                      "username and password and send Elasticsearch queries to the "
                      "<code>cvr-permanent/virksomhed</code>, <code>cvr-permanent/produktionsenhed</code> and "
                      "<code>cvr-permanent/deltager</code> indexes. Responses include the full history of each company."),
                ("h2", "What a lookup looks like"),
                ("code", "bash", _ES_QUERY_EN),
                ("p", "Every field is a list with validity periods. To get the current name, you have to find the "
                      "period that's still valid yourself:"),
                ("code", "python", _ES_NAME_PY_EN),
                ("p", "The same goes for addresses, industry codes, status, headcount and especially participant "
                      "relations, where owners and management are buried several levels deep."),
                ("h2", "The same lookup with apicvr.dk"),
                ("code", "bash", _APICVR_ONE_LINER),
                ("p", "apicvr.dk sends the query to System-til-System for you, picks out the current values and "
                      "returns a flat object. No application, no password."),
                ("h2", "When should you use System-til-System directly?"),
                ("ul", [
                    "You need history: previous names, addresses, owners or directors.",
                    "You need bulk extracts, e.g. every company in an industry or municipality.",
                    "You need fields apicvr.dk doesn't return.",
                    "You don't want to depend on a third party.",
                ]),
                ("p", "For everyday lookups in a web shop, CRM, onboarding flow or spreadsheet, a ready-made API "
                      "like apicvr.dk is faster to start with and easier to maintain."),
                ("note", "apicvr.dk is open source. If you have your own System-til-System access, you can run your "
                         "own instance with Docker. See <a href=\"https://github.com/NoahBohme/apicvr.dk\">GitHub</a>."),
            ],
            "faq": [
                ("How do I get System-til-System access?",
                 "You apply to the Danish Business Authority and accept their terms. Once approved, you get a "
                 "username and password for distribution.virk.dk."),
                ("Is System-til-System free?",
                 "Yes, access is free, but it requires approval and a technical integration with Elasticsearch."),
                ("Does apicvr.dk use the same data?",
                 "Yes. Every lookup goes live to distribution.virk.dk, so you get the same current information."),
            ],
        },
    },
]
