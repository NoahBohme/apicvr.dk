"""Glossary pages: CVR terms explained, each tied back to API fields."""

_CVR_CHECK_PY = """\
def is_valid_cvr(cvr: str) -> bool:
    weights = [2, 7, 6, 5, 4, 3, 2, 1]
    if len(cvr) != 8 or not cvr.isdigit() or cvr[0] == "0":
        return False
    return sum(int(d) * w for d, w in zip(cvr, weights)) % 11 == 0

print(is_valid_cvr("24256790"))  # True  (Novo Nordisk A/S)
print(is_valid_cvr("24256791"))  # False (typo)"""

_CVR_LOOKUP = """\
curl {site}/api/v1/24256790"""

_CVR_JSON = """\
{
  "vat": 24256790,
  "name": "NOVO NORDISK A/S",
  "city": "Bagsværd",
  "companydesc": "Aktieselskab",
  "industrycode": 212000,
  "industrydesc": "Fremstilling af farmaceutiske præparater",
  "status": "NORMAL",
  ...
}"""

_PUNIT_JSON = """\
{
  "vat": 10403782,
  "name": "VESTAS WIND SYSTEMS A/S",
  "p_units": [
    {
      "p_number": 1017864846,
      "name": "Vestas Wind Systems A/S",
      "address": "Sahara 7",
      "zipcode": 6700,
      "city": "Esbjerg",
      "startdate": "2012-08-17",
      "enddate": "2013-02-13",
      "industrycode": 721900,
      "protected": false
    },
    ...
  ]
}"""

_PUNIT_PY = """\
import requests

company = requests.get("{site}/api/v1/10403782").json()
active = [p for p in company["p_units"] if not p["enddate"]]

for unit in active:
    print(unit["p_number"], unit["address"], unit["zipcode"], unit["city"])"""

_PROTECTED_PY = """\
import requests

company = requests.get("{site}/api/v1/41013583").json()

if company["protected"]:
    print("Reklamebeskyttet – må ikke bruges til direkte markedsføring")
else:
    print("Ingen reklamebeskyttelse registreret")"""

_PROTECTED_PY_EN = """\
import requests

company = requests.get("{site}/api/v1/41013583").json()

if company["protected"]:
    print("Marketing-protected: do not use for direct marketing")
else:
    print("No marketing protection registered")"""

_TYPES_JSON = """\
curl {site}/api/v1/24256790

{
  "vat": 24256790,
  "name": "NOVO NORDISK A/S",
  "companycode": 60,
  "companydesc": "Aktieselskab",
  "companytypeshort": "A/S",
  ...
}"""

_TYPES_JS = """\
const res = await fetch("{site}/api/v1/search/company/tømrer?limit=50");
const companies = await res.json();

// Keep only limited-liability companies (ApS and A/S)
const limited = companies.filter((c) => [60, 80].includes(c.companycode));
console.log(limited.map((c) => `${c.name} (${c.companytypeshort})`));"""

_INDUSTRY_JSON = """\
curl {site}/api/v1/10403782

{
  "vat": 10403782,
  "name": "VESTAS WIND SYSTEMS A/S",
  "industrycode": 721000,
  "industrydesc": "Forskning og eksperimentel udvikling inden for naturvidenskab og teknik",
  ...
}"""

_INDUSTRY_PY = """\
import requests

companies = requests.get("{site}/api/v1/search/fuzzy/holding?limit=50").json()

holding = [c for c in companies if str(c["industrycode"]) == "642120"]
for c in holding:
    print(c["cvr_number"], c["name"], c["industrytext"])"""


PAGES = [
    # --- CVR number ---------------------------------------------------------
    {
        "id": "cvr-number",
        "family": "glossary",
        "slug": {"da": "hvad-er-et-cvr-nummer", "en": "what-is-a-cvr-number"},
        "related": ["validate-cvr", "p-number", "python"],
        "da": {
            "title": "Hvad er et CVR-nummer? Format, kontrolciffer og opslag",
            "description": (
                "Et CVR-nummer er virksomhedens 8-cifrede ID i Det Centrale Virksomhedsregister. "
                "Se formatet, modulus 11-kontrollen, og hvordan du slår det op via API."
            ),
            "h1": "Hvad er et CVR-nummer?",
            "lead": (
                "CVR-nummeret er det unikke 8-cifrede nummer, som hver dansk virksomhed får, når den "
                "registreres i Det Centrale Virksomhedsregister (CVR). Det er nøglen til alle "
                "oplysninger om virksomheden – og til ethvert opslag i CVR-API."
            ),
            "blocks": [
                ("h2", "Kort fortalt"),
                ("ul", [
                    "Et CVR-nummer består af <strong>8 cifre</strong> og starter aldrig med 0.",
                    "Det tildeles af Erhvervsstyrelsen, når virksomheden registreres i CVR.",
                    "Nummeret følger virksomheden hele dens levetid – også ved navne- og adresseændringer.",
                    "Hver fysisk adresse, virksomheden driver aktivitet fra, får desuden et "
                    "<a href=\"/guides/hvad-er-et-p-nummer\">P-nummer</a>.",
                ]),
                ("h2", "Hvem får et CVR-nummer?"),
                ("p",
                 "Alle selskaber (fx ApS og A/S) skal registreres. Det samme gælder enkeltmandsvirksomheder "
                 "og andre virksomheder, der fx er momspligtige eller har ansatte. Også foreninger, fonde "
                 "og offentlige myndigheder har CVR-numre. Se de forskellige "
                 "<a href=\"/guides/virksomhedsformer\">virksomhedsformer</a>."),
                ("h2", "Hvor bruges CVR-nummeret?"),
                ("p",
                 "CVR-nummeret bruges på fakturaer, i kontrakter, ved moms- og skatteindberetning, i "
                 "e-fakturering (EAN/NemHandel) og når man opretter en virksomhed som kunde. Det er "
                 "også grundlaget for momsnummeret: et dansk momsnummer er <code>DK</code> efterfulgt "
                 "af CVR-nummeret."),
                ("h2", "Kontrolciffer: modulus 11"),
                ("p",
                 "CVR-numre er udstedt med et kontrolciffer efter modulus 11. Hvert ciffer ganges med "
                 "vægtene <code>2, 7, 6, 5, 4, 3, 2, 1</code>, og summen skal gå op i 11. Det fanger de "
                 "fleste tastefejl, før du overhovedet kalder et API – men det beviser ikke, at "
                 "virksomheden findes. Bekræft altid med et opslag."),
                ("code", "python", _CVR_CHECK_PY),
                ("h2", "Slå et CVR-nummer op via API"),
                ("p",
                 "Med CVR-API kræver et opslag hverken nøgle eller konto. Send et GET-kald med "
                 "CVR-nummeret, og få virksomhedens navn, adresse, branche, status, P-enheder, "
                 "direktion og ejere tilbage som JSON:"),
                ("code", "bash", _CVR_LOOKUP),
                ("code", "json", _CVR_JSON),
                ("note",
                 "Feltet <code>vat</code> indeholder CVR-nummeret. Findes nummeret ikke, svarer API'et "
                 "med HTTP 404 og fejlkoden <code>NOT_FOUND</code>."),
            ],
            "faq": [
                ("Hvor mange cifre har et CVR-nummer?",
                 "Et CVR-nummer har altid 8 cifre. Et P-nummer har til sammenligning 10 cifre."),
                ("Er CVR-nummer og momsnummer det samme?",
                 "Næsten. Det danske momsnummer (VAT-nummer) er landekoden <code>DK</code> efterfulgt af "
                 "CVR-nummeret, fx DK24256790."),
                ("Kan jeg tjekke om et CVR-nummer er gyldigt?",
                 "Ja. Modulus 11-kontrollen afslører de fleste tastefejl lokalt. Om virksomheden faktisk "
                 "findes, ser du ved et opslag på <code>/api/v1/{cvr}</code>."),
            ],
        },
        "en": {
            "title": "What Is a CVR Number? Format, Check Digit and Lookup",
            "description": (
                "A CVR number is a Danish company's 8-digit ID in the Central Business Register. "
                "Learn the format, the modulus 11 check, and how to look one up via API."
            ),
            "h1": "What is a CVR number?",
            "lead": (
                "The CVR number is the unique 8-digit number every Danish business receives when it is "
                "registered in the Central Business Register (CVR). It is the key to everything known "
                "about the company – and to every lookup in CVR-API."
            ),
            "blocks": [
                ("h2", "In short"),
                ("ul", [
                    "A CVR number has <strong>8 digits</strong> and never starts with 0.",
                    "It is issued by the Danish Business Authority (Erhvervsstyrelsen) on registration.",
                    "It stays with the company for life, through name and address changes.",
                    "Each physical location the company operates from also gets a "
                    "<a href=\"/en/guides/what-is-a-p-number\">P-number</a>.",
                ]),
                ("h2", "Who gets a CVR number?"),
                ("p",
                 "All companies (such as ApS and A/S) must register, as must sole proprietorships and other "
                 "businesses that are, for example, VAT-registered or have employees. Associations, "
                 "foundations and public authorities have CVR numbers too. See the different "
                 "<a href=\"/en/guides/danish-company-types\">Danish company types</a>."),
                ("h2", "Where is the CVR number used?"),
                ("p",
                 "On invoices, in contracts, for VAT and tax reporting, in e-invoicing, and whenever a "
                 "business is set up as a customer. It is also the basis of the Danish VAT number: "
                 "<code>DK</code> followed by the CVR number."),
                ("h2", "Check digit: modulus 11"),
                ("p",
                 "CVR numbers are issued with a modulus 11 check digit. Multiply each digit by the weights "
                 "<code>2, 7, 6, 5, 4, 3, 2, 1</code>; the sum must be divisible by 11. This catches most "
                 "typos before you call an API – but it doesn't prove the company exists. Always confirm "
                 "with a lookup."),
                ("code", "python", _CVR_CHECK_PY),
                ("h2", "Look up a CVR number via API"),
                ("p",
                 "CVR-API needs no key or account. Send a GET request with the CVR number and get the "
                 "company's name, address, industry, status, production units, management and owners "
                 "back as JSON:"),
                ("code", "bash", _CVR_LOOKUP),
                ("code", "json", _CVR_JSON),
                ("note",
                 "The <code>vat</code> field holds the CVR number. If the number doesn't exist, the API "
                 "responds with HTTP 404 and the error code <code>NOT_FOUND</code>."),
            ],
            "faq": [
                ("How many digits does a CVR number have?",
                 "A CVR number always has 8 digits. A P-number, by comparison, has 10."),
                ("Is a CVR number the same as a Danish VAT number?",
                 "Almost. The Danish VAT number is the country code <code>DK</code> followed by the CVR "
                 "number, e.g. DK24256790."),
                ("Can I check whether a CVR number is valid?",
                 "Yes. The modulus 11 check catches most typos locally. Whether the company actually "
                 "exists is confirmed by a lookup on <code>/api/v1/{cvr}</code>."),
            ],
        },
    },
    # --- P-number -----------------------------------------------------------
    {
        "id": "p-number",
        "family": "glossary",
        "slug": {"da": "hvad-er-et-p-nummer", "en": "what-is-a-p-number"},
        "related": ["p-units", "cvr-number", "find-by-address"],
        "da": {
            "title": "Hvad er et P-nummer? Produktionsenheder i CVR forklaret",
            "description": (
                "Et P-nummer er det 10-cifrede nummer for en produktionsenhed – én pr. adresse, "
                "virksomheden arbejder fra. Se forskellen på CVR og P-nummer, og hent dem via API."
            ),
            "h1": "Hvad er et P-nummer?",
            "lead": (
                "Et P-nummer (produktionsenhedsnummer) identificerer en fysisk adresse, hvor en virksomhed "
                "driver aktivitet – fx en butik, et kontor eller en fabrik. Én virksomhed har ét "
                "CVR-nummer, men kan have mange P-numre."
            ),
            "blocks": [
                ("h2", "CVR-nummer vs. P-nummer"),
                ("table", ["", "CVR-nummer", "P-nummer"], [
                    ["Identificerer", "Den juridiske virksomhed", "En fysisk lokation (produktionsenhed)"],
                    ["Længde", "8 cifre", "10 cifre"],
                    ["Antal pr. virksomhed", "Ét", "Ét pr. adresse, der drives aktivitet fra"],
                    ["Ved flytning", "Bevares", "Typisk ophører enheden, og en ny oprettes på den nye adresse"],
                    ["I CVR-API", "<code>vat</code>", "<code>p_units[].p_number</code>"],
                ]),
                ("h2", "Hvad bruges P-numre til?"),
                ("ul", [
                    "Statistik og registrering af ansatte på den rigtige arbejdsplads.",
                    "Myndigheders tilsyn med konkrete lokationer, fx fødevarekontrol.",
                    "Find alle butikker, afdelinger eller lagre for én kæde.",
                    "Leveringsadresser og filialer i CRM- og ERP-systemer.",
                ]),
                ("h2", "P-enheder i CVR-API"),
                ("p",
                 "Et opslag på <code>/api/v1/{cvr}</code> returnerer virksomhedens produktionsenheder i "
                 "listen <code>p_units</code>. Hver enhed har eget navn, adresse, branche, antal ansatte, "
                 "kontaktoplysninger og sit eget <code>protected</code>-flag for reklamebeskyttelse."),
                ("code", "json", _PUNIT_JSON),
                ("p",
                 "Listen indeholder også ophørte enheder. Feltet <code>enddate</code> er udfyldt for "
                 "enheder, der er lukket, og <code>null</code> for aktive. Sådan henter du kun de aktive:"),
                ("code", "python", _PUNIT_PY),
            ],
            "faq": [
                ("Hvor mange cifre har et P-nummer?",
                 "Et P-nummer har 10 cifre, mens et CVR-nummer har 8."),
                ("Kan en virksomhed have flere P-numre?",
                 "Ja. Der oprettes en produktionsenhed for hver adresse, virksomheden driver aktivitet fra. "
                 "Store kæder kan have hundredvis."),
                ("Gælder reklamebeskyttelse også P-enheder?",
                 "Ja. Hver P-enhed har sit eget <code>protected</code>-felt i API'et, som du skal respektere "
                 "ved markedsføring rettet mod den pågældende lokation."),
            ],
        },
        "en": {
            "title": "What Is a P-Number? Danish Production Units Explained",
            "description": (
                "A P-number is the 10-digit ID of a production unit – each physical address a Danish "
                "company operates from. See how it differs from a CVR number and fetch it via API."
            ),
            "h1": "What is a P-number?",
            "lead": (
                "A P-number (production unit number) identifies a physical address where a Danish "
                "company operates – a shop, an office or a factory. One company has one CVR number but "
                "can have many P-numbers."
            ),
            "blocks": [
                ("h2", "CVR number vs. P-number"),
                ("table", ["", "CVR number", "P-number"], [
                    ["Identifies", "The legal entity", "A physical location (production unit)"],
                    ["Length", "8 digits", "10 digits"],
                    ["Per company", "One", "One per address the company operates from"],
                    ["When relocating", "Kept", "Typically the unit closes and a new one is created at the new address"],
                    ["In CVR-API", "<code>vat</code>", "<code>p_units[].p_number</code>"],
                ]),
                ("h2", "What are P-numbers used for?"),
                ("ul", [
                    "Statistics and registering employees at the right workplace.",
                    "Authorities supervising specific locations, such as food inspections.",
                    "Finding every store, branch or warehouse of a chain.",
                    "Delivery addresses and branches in CRM and ERP systems.",
                ]),
                ("h2", "Production units in CVR-API"),
                ("p",
                 "A lookup on <code>/api/v1/{cvr}</code> returns the company's production units in the "
                 "<code>p_units</code> list. Each unit has its own name, address, industry, headcount, "
                 "contact details and its own <code>protected</code> flag for marketing protection."),
                ("code", "json", _PUNIT_JSON),
                ("p",
                 "The list also includes closed units. <code>enddate</code> is set for units that have "
                 "closed and <code>null</code> for active ones. To keep only the active units:"),
                ("code", "python", _PUNIT_PY),
            ],
            "faq": [
                ("How many digits does a P-number have?",
                 "A P-number has 10 digits; a CVR number has 8."),
                ("Can a company have several P-numbers?",
                 "Yes. A production unit is created for each address the company operates from. Large "
                 "chains can have hundreds."),
                ("Does marketing protection apply to P-units?",
                 "Yes. Each P-unit has its own <code>protected</code> field in the API, which you must "
                 "respect when marketing to that location."),
            ],
        },
    },
    # --- Reklamebeskyttelse -------------------------------------------------
    {
        "id": "reklamebeskyttelse",
        "family": "glossary",
        "slug": {"da": "reklamebeskyttelse", "en": "marketing-protection-reklamebeskyttelse"},
        "related": ["p-number", "owners-management", "zapier-make"],
        "da": {
            "title": "Reklamebeskyttelse i CVR: Hvad betyder det for dig?",
            "description": (
                "Reklamebeskyttede virksomheder har frabedt sig reklamehenvendelser. Se hvad det betyder, "
                "hvordan du tjekker feltet protected i CVR-API, og hvad du skal overholde."
            ),
            "h1": "Reklamebeskyttelse i CVR",
            "lead": (
                "Virksomheder kan få registreret reklamebeskyttelse i CVR. Det betyder, at deres "
                "oplysninger ikke må bruges til direkte markedsføring. Bruger du CVR-data til salg eller "
                "markedsføring, skal du kunne se og respektere markeringen."
            ),
            "blocks": [
                ("h2", "Hvad betyder reklamebeskyttelse?"),
                ("p",
                 "En reklamebeskyttet virksomhed har frabedt sig reklamehenvendelser. Oplysninger om "
                 "virksomheden – eller om en reklamebeskyttet P-enhed – må derfor ikke bruges til direkte "
                 "markedsføring som fx telefonsalg, målrettede postudsendelser og lignende. Reglerne "
                 "følger af CVR-loven (lov om Det Centrale Virksomhedsregister)."),
                ("p",
                 "Beskyttelsen fjerner ikke virksomheden fra CVR. Oplysningerne er stadig offentlige og "
                 "kan bruges til fx fakturering, kreditvurdering, kundeoprettelse og andre formål, der "
                 "ikke er reklame."),
                ("h2", "Feltet protected i CVR-API"),
                ("p",
                 "Både virksomheden og hver P-enhed har feltet <code>protected</code>. Er det "
                 "<code>true</code>, er der registreret reklamebeskyttelse:"),
                ("code", "python", _PROTECTED_PY),
                ("h2", "Gør og undgå"),
                ("table", ["Gør", "Undgå"], [
                    ["Tjek <code>protected</code> på både virksomhed og P-enhed, før du markedsfører",
                     "At ringe eller sende målrettet reklame til beskyttede virksomheder"],
                    ["Gem markeringen sammen med dine data, og opdatér den løbende",
                     "At bruge en gammel kopi af data, hvor markeringen kan være ændret"],
                    ["Markér tydeligt beskyttelsen, når du giver data videre til andre",
                     "At videregive lister uden at oplyse, hvem der er beskyttet"],
                ]),
                ("note",
                 "Reklamebeskyttelse i CVR gælder virksomheder og P-enheder. For privatpersoner findes "
                 "i stedet Robinsonlisten. Er du i tvivl om, hvad din konkrete brug kræver, så søg "
                 "juridisk rådgivning – denne side er ikke juridisk rådgivning."),
            ],
            "faq": [
                ("Må jeg slå en reklamebeskyttet virksomhed op?",
                 "Ja. Beskyttelsen begrænser brug til direkte markedsføring – ikke opslag, fakturering "
                 "eller kundeoprettelse."),
                ("Hvor ser jeg om en virksomhed er reklamebeskyttet?",
                 "I feltet <code>protected</code> på virksomheden og på hver P-enhed i svaret fra "
                 "<code>/api/v1/{cvr}</code>."),
                ("Gælder beskyttelsen for alle virksomhedens adresser?",
                 "Markeringen findes både for virksomheden og for den enkelte P-enhed, så tjek begge, før "
                 "du markedsfører til en bestemt lokation."),
            ],
        },
        "en": {
            "title": "Marketing Protection in CVR (Reklamebeskyttelse) Explained",
            "description": (
                "Marketing-protected Danish companies have opted out of direct marketing. Learn what it "
                "means, how to read the protected field in CVR-API, and what to respect."
            ),
            "h1": "Marketing protection (reklamebeskyttelse) in CVR",
            "lead": (
                "Danish companies can register marketing protection (reklamebeskyttelse) in CVR. Their "
                "details may then not be used for direct marketing. If you use CVR data for sales or "
                "marketing, you need to read and respect that flag."
            ),
            "blocks": [
                ("h2", "What does marketing protection mean?"),
                ("p",
                 "A marketing-protected company has opted out of advertising contact. Information about "
                 "the company – or about a protected production unit – may not be used for direct "
                 "marketing such as telemarketing, targeted mailings and similar. The rules follow from "
                 "the Danish CVR Act (lov om Det Centrale Virksomhedsregister)."),
                ("p",
                 "Protection doesn't remove the company from CVR. Its details remain public and can be "
                 "used for invoicing, credit checks, customer onboarding and other non-marketing purposes."),
                ("h2", "The protected field in CVR-API"),
                ("p",
                 "Both the company and every production unit have a <code>protected</code> field. When "
                 "it is <code>true</code>, marketing protection is registered:"),
                ("code", "python", _PROTECTED_PY_EN),
                ("h2", "Do's and don'ts"),
                ("table", ["Do", "Don't"], [
                    ["Check <code>protected</code> on both the company and the P-unit before marketing",
                     "Call or send targeted advertising to protected companies"],
                    ["Store the flag with your data and refresh it regularly",
                     "Rely on an old copy of the data where the flag may have changed"],
                    ["Clearly mark protection when passing data on to others",
                     "Share lists without stating which companies are protected"],
                ]),
                ("note",
                 "CVR marketing protection covers companies and production units. For private individuals "
                 "Denmark has the separate Robinson list. If you are unsure what your specific use requires, "
                 "get legal advice – this page is not legal advice."),
            ],
            "faq": [
                ("Can I look up a marketing-protected company?",
                 "Yes. Protection restricts direct marketing – not lookups, invoicing or customer onboarding."),
                ("Where do I see if a company is protected?",
                 "In the <code>protected</code> field on the company and on each P-unit in the response "
                 "from <code>/api/v1/{cvr}</code>."),
                ("Does protection cover all of a company's addresses?",
                 "The flag exists on both the company and each production unit, so check both before "
                 "marketing to a specific location."),
            ],
        },
    },
    # --- Company types ------------------------------------------------------
    {
        "id": "company-types",
        "family": "glossary",
        "slug": {"da": "virksomhedsformer", "en": "danish-company-types"},
        "related": ["cvr-number", "javascript", "owners-management"],
        "da": {
            "title": "Virksomhedsformer: ApS, A/S, I/S, ENK og flere forklaret",
            "description": (
                "Overblik over danske virksomhedsformer – enkeltmandsvirksomhed, I/S, K/S, P/S, ApS, A/S, "
                "IVS, forening og fond – og de tilhørende koder i CVR-API's companycode-felt."
            ),
            "h1": "Danske virksomhedsformer",
            "lead": (
                "Virksomhedsformen afgør, hvem der hæfter for gælden, og hvilke krav der stilles til "
                "kapital og regnskab. I CVR-API står formen i tre felter: companycode, companydesc og "
                "companytypeshort."
            ),
            "blocks": [
                ("h2", "Virksomhedsformer og koder"),
                ("p", "Koderne herunder er de værdier, CVR returnerer i feltet <code>companycode</code>:"),
                ("table", ["companycode", "companydesc", "companytypeshort", "Hæftelse"], [
                    ["10", "Enkeltmandsvirksomhed", "ENK", "Ejeren hæfter personligt og ubegrænset"],
                    ["15", "Personligt ejet Mindre Virksomhed", "PMV", "Ejeren hæfter personligt"],
                    ["30", "Interessentskab", "I/S", "Interessenterne hæfter personligt og solidarisk"],
                    ["40", "Kommanditselskab", "K/S", "Komplementar ubegrænset, kommanditister begrænset"],
                    ["60", "Aktieselskab", "A/S", "Begrænset til indskudt kapital (min. 400.000 kr.)"],
                    ["70", "Kommanditaktieselskab/Partnerselskab", "KAS", "Komplementar ubegrænset, aktionærer begrænset"],
                    ["80", "Anpartsselskab", "APS", "Begrænset til indskudt kapital (min. 40.000 kr.)"],
                    ["81", "Iværksætterselskab", "IVS", "Afskaffet – se nedenfor"],
                    ["90", "Fonde og andre selvejende institutioner", "FON", "Ingen ejere"],
                    ["100", "Erhvervsdrivende fond", "EFO", "Ingen ejere"],
                    ["110", "Forening", "FOR", "Foreningens formue"],
                    ["115", "Frivillig forening", "FFO", "Foreningens formue"],
                ]),
                ("h2", "Personligt ejede virksomheder"),
                ("p",
                 "<strong>Enkeltmandsvirksomheden</strong> er den enkleste form: én ejer, intet krav om "
                 "kapital, og ejeren hæfter med hele sin private formue. I et <strong>I/S</strong> er der "
                 "to eller flere ejere, som hæfter personligt og solidarisk. Et <strong>K/S</strong> har "
                 "mindst én komplementar med ubegrænset hæftelse og en eller flere kommanditister, der kun "
                 "hæfter med deres indskud."),
                ("h2", "Kapitalselskaber: ApS, A/S og P/S"),
                ("p",
                 "I <strong>ApS</strong> og <strong>A/S</strong> hæfter ejerne kun med den kapital, de har "
                 "indskudt. Et ApS kræver mindst 40.000 kr. i selskabskapital, et A/S mindst 400.000 kr. "
                 "Et <strong>P/S</strong> (partnerselskab) kombinerer en komplementar med ubegrænset "
                 "hæftelse og kapitalejere med begrænset hæftelse; i CVR har det samme kode som "
                 "kommanditaktieselskabet (70)."),
                ("h2", "Hvad skete der med IVS?"),
                ("p",
                 "Iværksætterselskabet (IVS) blev afskaffet i 2019. Eksisterende IVS'er skulle omdannes "
                 "til ApS eller opløses inden for en overgangsperiode. Du kan stadig møde koden 81 på "
                 "ældre og ophørte virksomheder."),
                ("h2", "Virksomhedsformen i API'et"),
                ("code", "bash", _TYPES_JSON),
                ("p",
                 "Brug den numeriske <code>companycode</code> til logik og filtrering – teksterne er "
                 "beregnet til visning. Fx kun kapitalselskaber fra en navnesøgning:"),
                ("code", "javascript", _TYPES_JS),
            ],
            "faq": [
                ("Hvad er forskellen på ApS og A/S?",
                 "Begge er kapitalselskaber med begrænset hæftelse. Et ApS kræver mindst 40.000 kr. i "
                 "kapital, et A/S mindst 400.000 kr., og A/S har flere krav til ledelse og kan børsnoteres."),
                ("Kan man stadig stifte et IVS?",
                 "Nej. IVS blev afskaffet i 2019, og eksisterende IVS'er skulle omdannes til ApS eller opløses."),
                ("Hvilket felt skal jeg bruge til at filtrere på virksomhedsform?",
                 "Brug <code>companycode</code>, fx 80 for ApS og 60 for A/S. Felterne "
                 "<code>companydesc</code> og <code>companytypeshort</code> er til visning."),
            ],
        },
        "en": {
            "title": "Danish Company Types: ApS, A/S, I/S, ENK and More",
            "description": (
                "Overview of Danish company types – sole proprietorship, I/S, K/S, P/S, ApS, A/S, IVS, "
                "associations and foundations – and their codes in CVR-API's companycode field."
            ),
            "h1": "Danish company types",
            "lead": (
                "The company type determines who is liable for debts and what capital and reporting rules "
                "apply. In CVR-API the type is exposed in three fields: companycode, companydesc and "
                "companytypeshort."
            ),
            "blocks": [
                ("h2", "Company types and codes"),
                ("p", "The codes below are the values CVR returns in the <code>companycode</code> field:"),
                ("table", ["companycode", "companydesc (Danish)", "companytypeshort", "Liability"], [
                    ["10", "Enkeltmandsvirksomhed (sole proprietorship)", "ENK", "Owner personally, unlimited"],
                    ["15", "Personligt ejet Mindre Virksomhed (small personally owned business)", "PMV", "Owner personally"],
                    ["30", "Interessentskab (general partnership)", "I/S", "Partners personally, jointly and severally"],
                    ["40", "Kommanditselskab (limited partnership)", "K/S", "General partner unlimited, limited partners limited"],
                    ["60", "Aktieselskab (public limited company)", "A/S", "Limited to paid-in capital (min. DKK 400,000)"],
                    ["70", "Kommanditaktieselskab/Partnerselskab (partnership limited by shares)", "KAS", "General partner unlimited, shareholders limited"],
                    ["80", "Anpartsselskab (private limited company)", "APS", "Limited to paid-in capital (min. DKK 40,000)"],
                    ["81", "Iværksætterselskab (entrepreneurial company)", "IVS", "Abolished – see below"],
                    ["90", "Fonde og andre selvejende institutioner (foundations)", "FON", "No owners"],
                    ["100", "Erhvervsdrivende fond (commercial foundation)", "EFO", "No owners"],
                    ["110", "Forening (association)", "FOR", "The association's assets"],
                    ["115", "Frivillig forening (voluntary association)", "FFO", "The association's assets"],
                ]),
                ("h2", "Personally owned businesses"),
                ("p",
                 "The <strong>sole proprietorship</strong> (enkeltmandsvirksomhed) is the simplest form: "
                 "one owner, no capital requirement, and the owner is liable with all personal assets. An "
                 "<strong>I/S</strong> has two or more owners who are personally, jointly and severally "
                 "liable. A <strong>K/S</strong> has at least one general partner with unlimited liability "
                 "and one or more limited partners liable only for their contribution."),
                ("h2", "Limited companies: ApS, A/S and P/S"),
                ("p",
                 "In an <strong>ApS</strong> or <strong>A/S</strong>, owners are only liable for the capital "
                 "they have paid in. An ApS requires at least DKK 40,000 in share capital, an A/S at least "
                 "DKK 400,000. A <strong>P/S</strong> (partnerselskab) combines a general partner with "
                 "unlimited liability and shareholders with limited liability; in CVR it shares code 70 "
                 "with the kommanditaktieselskab."),
                ("h2", "What happened to IVS?"),
                ("p",
                 "The entrepreneurial company (IVS) was abolished in 2019. Existing IVS companies had to "
                 "convert to an ApS or be dissolved within a transition period. You may still see code 81 "
                 "on older and dissolved companies."),
                ("h2", "The company type in the API"),
                ("code", "bash", _TYPES_JSON),
                ("p",
                 "Use the numeric <code>companycode</code> for logic and filtering – the text fields are "
                 "meant for display. For example, keep only limited companies from a name search:"),
                ("code", "javascript", _TYPES_JS),
            ],
            "faq": [
                ("What is the difference between ApS and A/S?",
                 "Both are limited companies. An ApS needs at least DKK 40,000 in capital, an A/S at least "
                 "DKK 400,000, and an A/S has stricter governance rules and can be publicly listed."),
                ("Can you still register an IVS?",
                 "No. The IVS was abolished in 2019, and existing IVS companies had to convert to an ApS or "
                 "be dissolved."),
                ("Which field should I filter on for the company type?",
                 "Use <code>companycode</code>, e.g. 80 for ApS and 60 for A/S. "
                 "<code>companydesc</code> and <code>companytypeshort</code> are for display."),
            ],
        },
    },
    # --- Industry codes -----------------------------------------------------
    {
        "id": "industry-codes",
        "family": "glossary",
        "slug": {"da": "branchekoder", "en": "danish-industry-codes"},
        "related": ["company-types", "python", "excel"],
        "da": {
            "title": "Branchekoder i CVR: Sådan læser du industrycode",
            "description": (
                "Danske branchekoder er 6-cifrede koder fra Danmarks Statistik baseret på EU's NACE. "
                "Se hvordan de er opbygget, og hvordan du bruger industrycode i CVR-API."
            ),
            "h1": "Branchekoder i CVR",
            "lead": (
                "Alle virksomheder i CVR er registreret med en hovedbranche – en 6-cifret branchekode, der "
                "beskriver, hvad virksomheden laver. Koden gør det muligt at gruppere og filtrere "
                "virksomheder efter branche."
            ),
            "blocks": [
                ("h2", "Hvad er en branchekode?"),
                ("p",
                 "Branchekoderne kommer fra Dansk Branchekode (DB), Danmarks Statistiks danske udgave af "
                 "EU's branchenomenklatur NACE. De første cifre følger NACE-hierarkiet, og de sidste "
                 "cifre er danske underopdelinger. Jo flere cifre, der matcher, jo tættere er brancherne "
                 "på hinanden."),
                ("h2", "Eksempler"),
                ("table", ["industrycode", "industrydesc", "Eksempel"], [
                    ["212000", "Fremstilling af farmaceutiske præparater", "Novo Nordisk A/S"],
                    ["721000", "Forskning og eksperimentel udvikling inden for naturvidenskab og teknik", "Vestas Wind Systems A/S"],
                    ["642120", "Ikke-finansielle holdingselskaber", "Mange holdingselskaber (ApS)"],
                    ["702200", "Virksomhedsrådgivning og anden rådgivning om driftsledelse", "Konsulentvirksomheder"],
                    ["949900", "Andre organisationer og foreninger i.a.n.", "Idræts- og interesseforeninger"],
                ]),
                ("h2", "Branchekoden i CVR-API"),
                ("p",
                 "Et opslag returnerer hovedbranchen i <code>industrycode</code> og beskrivelsen i "
                 "<code>industrydesc</code>. Hver P-enhed har desuden sin egen branchekode, som kan "
                 "afvige fra virksomhedens."),
                ("code", "bash", _INDUSTRY_JSON),
                ("p",
                 "Søgeendpoints som <code>/api/v1/search/fuzzy/{navn}</code> returnerer også "
                 "<code>industrycode</code> og <code>industrytext</code>, så du kan filtrere resultaterne:"),
                ("code", "python", _INDUSTRY_PY),
                ("note",
                 "Mangler en branche, kan søgeresultater returnere værdien <code>\"Unknown\"</code>. "
                 "Sammenlign derfor koden som tekst, eller håndtér værdier, der ikke er tal."),
            ],
            "faq": [
                ("Hvor mange cifre har en dansk branchekode?",
                 "Branchekoderne i CVR har 6 cifre, fx 642120 for ikke-finansielle holdingselskaber."),
                ("Kan en virksomhed have flere branchekoder?",
                 "Ja. Virksomheden har én hovedbranche og kan have bibrancher. CVR-API returnerer "
                 "hovedbranchen i <code>industrycode</code>, og hver P-enhed har sin egen."),
                ("Hvad er sammenhængen mellem branchekoder og NACE?",
                 "Dansk Branchekode bygger på EU's NACE-nomenklatur, så de første cifre svarer til NACE, "
                 "mens de sidste er danske underopdelinger."),
            ],
        },
        "en": {
            "title": "Danish Industry Codes in CVR: Reading industrycode",
            "description": (
                "Danish industry codes are 6-digit codes from Statistics Denmark based on the EU's NACE. "
                "Learn how they are structured and how to use industrycode in CVR-API."
            ),
            "h1": "Danish industry codes (branchekoder)",
            "lead": (
                "Every company in CVR is registered with a main industry – a 6-digit industry code that "
                "describes what the company does. The code lets you group and filter companies by sector."
            ),
            "blocks": [
                ("h2", "What is an industry code?"),
                ("p",
                 "The codes come from Dansk Branchekode (DB), Statistics Denmark's Danish version of the EU "
                 "industry classification NACE. The first digits follow the NACE hierarchy and the last "
                 "digits are Danish subdivisions. The more leading digits two codes share, the closer the "
                 "industries are."),
                ("h2", "Examples"),
                ("table", ["industrycode", "industrydesc (Danish)", "Example"], [
                    ["212000", "Fremstilling af farmaceutiske præparater (pharmaceutical preparations)", "Novo Nordisk A/S"],
                    ["721000", "Forskning og eksperimentel udvikling inden for naturvidenskab og teknik (R&amp;D in natural sciences and engineering)", "Vestas Wind Systems A/S"],
                    ["642120", "Ikke-finansielle holdingselskaber (non-financial holding companies)", "Many holding companies (ApS)"],
                    ["702200", "Virksomhedsrådgivning og anden rådgivning om driftsledelse (management consultancy)", "Consultancies"],
                    ["949900", "Andre organisationer og foreninger i.a.n. (other membership organisations)", "Sports and interest clubs"],
                ]),
                ("h2", "The industry code in CVR-API"),
                ("p",
                 "A lookup returns the main industry in <code>industrycode</code> and its Danish description "
                 "in <code>industrydesc</code>. Each production unit also has its own industry code, which "
                 "can differ from the company's."),
                ("code", "bash", _INDUSTRY_JSON),
                ("p",
                 "Search endpoints such as <code>/api/v1/search/fuzzy/{name}</code> also return "
                 "<code>industrycode</code> and <code>industrytext</code>, so you can filter results:"),
                ("code", "python", _INDUSTRY_PY),
                ("note",
                 "When the industry is missing, search results may return the value "
                 "<code>\"Unknown\"</code>. Compare codes as strings, or handle non-numeric values."),
            ],
            "faq": [
                ("How many digits does a Danish industry code have?",
                 "Industry codes in CVR have 6 digits, e.g. 642120 for non-financial holding companies."),
                ("Can a company have several industry codes?",
                 "Yes. A company has one main industry and may have secondary ones. CVR-API returns the main "
                 "industry in <code>industrycode</code>, and each P-unit has its own."),
                ("How do Danish industry codes relate to NACE?",
                 "Dansk Branchekode is built on the EU's NACE classification, so the leading digits match "
                 "NACE while the last digits are Danish subdivisions."),
            ],
        },
    },
]
