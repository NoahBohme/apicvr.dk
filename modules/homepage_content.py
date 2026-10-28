"""Copy for the Danish and English homepages.

Kept as data so one template renders both languages and the visible FAQ
and its FAQPage JSON-LD can never drift apart.
"""

ENDPOINTS = [
    # (path, da, en)
    ("/api/v1/{cvr}", "Fuld virksomhedsprofil: adresse, branche, status, P-enheder, direktion og ejere",
     "Full company profile: address, industry, status, production units, management and owners"),
    ("/api/v1/{cvr}/direktion-og-ansvarlig", "Kun direktion, fuldt ansvarlige deltagere og legale ejere",
     "Just management, fully liable participants and legal owners"),
    ("/api/v1/search?name=…&cvr=…", "Kombineret søgning på navn og/eller CVR-nummer",
     "Combined search by name and/or CVR number"),
    ("/api/v1/search/fuzzy/{navn}", "Fejltolerant navnesøgning – perfekt til autocomplete",
     "Typo-tolerant name search – perfect for autocomplete"),
    ("/api/v1/search/address?address=…", "Find virksomheder på en adresse",
     "Find companies at a street address"),
    ("/api/v1/search/email/{email}", "Find virksomheder ud fra email eller emaildomæne",
     "Find companies by email or email domain"),
    ("/api/v1/search/phone/{telefon}", "Find virksomheder ud fra telefonnummer",
     "Find companies by phone number"),
]

_DA = {
    "lang": "da",
    "locale": "da_DK",
    "alt_locale": "en_US",
    "path": "/",
    "alt_path": "/en/",
    "company_path": "/da/virksomhed/",
    "title": "CVR API – Gratis API til danske virksomhedsdata | APICVR.dk",
    "description": (
        "Slå danske virksomheder op med et gratis CVR API uden API-nøgle. Hent navn, adresse, "
        "ejere, direktion og P-enheder som ren JSON direkte fra CVR-registret."
    ),
    "og_title": "CVR API – gratis, open source og uden API-nøgle",
    "og_image": "/static/og-da.png",
    "nav_docs": "Dokumentation",
    "nav_endpoints": "Endpoints",
    "nav_faq": "FAQ",
    "eyebrow": "Gratis · Open source · Ingen API-nøgle",
    "h1": "Gratis CVR API til danske virksomhedsdata",
    "lead": (
        "Slå enhver dansk virksomhed op på CVR-nummer, navn, adresse, email eller telefon. "
        "Få ejere, direktion og P-enheder tilbage som ren JSON – direkte fra Det Centrale "
        "Virksomhedsregister."
    ),
    "cta_try": "Prøv API'et nu",
    "cta_docs": "Læs dokumentationen",
    "stats_heading": "Live trafik på API'et",
    "stats_note": "Opdateres hvert 10. minut",
    "stat_total": "forespørgsler besvaret",
    "stat_total_since": "siden",
    "stat_30d": "de seneste 30 dage",
    "stat_per_day": "i gennemsnit pr. dag",
    "stat_today": "i dag (UTC)",
    "try_heading": "Prøv det live",
    "try_sub": "Søg på et virksomhedsnavn, eller skriv et CVR-nummer på 8 cifre.",
    "try_placeholder": "Fx Novo Nordisk eller 41013583",
    "code_heading": "Et HTTP-kald. Ingen opsætning.",
    "code_sub": "Ingen nøgler, ingen konto, ingen SDK. Kald endpointet fra det sprog, du allerede bruger.",
    "endpoints_heading": "Endpoints",
    "endpoints_sub": "Alle endpoints er GET og returnerer JSON. Se den fulde specifikation i",
    "endpoints_link": "dokumentationen",
    "features_heading": "Hvorfor CVR-API?",
    "features": [
        ("Ingen API-nøgle", "Ingen tilmelding eller token. Send et GET-kald, og du har data på sekunder."),
        ("Open source (MIT)", "Al kildekode ligger på GitHub. Kør det selv, fork det, eller bidrag."),
        ("Ejere og direktion", "Legale ejere med ejerandel og stemmerettigheder samt direktion og fuldt ansvarlige."),
        ("Fejltolerant søgning", "Fuzzy-søgning på navn, der finder virksomheden selv med stavefejl."),
        ("P-enheder", "Alle produktionsenheder med adresse, branche og antal ansatte."),
        ("Reklamebeskyttelse", "Feltet protected viser, om virksomheden har frabedt sig reklame."),
    ],
    "usecases_heading": "Bruges typisk til",
    "usecases": [
        "Autoudfyldning af firmaoplysninger i checkout og tilmeldingsformularer",
        "Validering af CVR-numre ved onboarding og KYC",
        "Berigelse af CRM-data med branche, adresse og ejerforhold",
        "Fakturering og bogføring med korrekte virksomhedsoplysninger",
    ],
    "faq_heading": "Ofte stillede spørgsmål",
    "faq": [
        ("Hvad er CVR-API?",
         "CVR-API er et gratis open source REST API til opslag i Det Centrale Virksomhedsregister (CVR). "
         "Det oversætter Erhvervsstyrelsens komplekse datastruktur til simpel, stabil JSON."),
        ("Er CVR-API gratis?",
         "Ja. API'et er gratis og kræver hverken konto eller API-nøgle. Der gælder rimelige rate limits. "
         "Skal du bruge vedvarende høj trafik, så skriv til noah@noahbohme.com."),
        ("Hvor kommer data fra?",
         "Data hentes fra distribution.virk.dk, som er Erhvervsstyrelsens officielle distribution af CVR-data. "
         "Opslag sker live, så du får de nyeste registrerede oplysninger."),
        ("Hvordan slår jeg en virksomhed op på CVR-nummer?",
         "Send et GET-kald til <code>https://apicvr.dk/api/v1/{cvr}</code>, fx "
         "<code>/api/v1/41013583</code>. Svaret indeholder navn, adresse, branche, status, P-enheder, "
         "direktion og ejere."),
        ("Kan jeg se ejere og direktion?",
         "Ja. Det fulde opslag indeholder legale ejere med ejerandel samt direktion. Har du kun brug for "
         "personerne, så brug <code>/api/v1/{cvr}/direktion-og-ansvarlig</code>."),
        ("Må jeg bruge data til markedsføring?",
         "Kun for virksomheder uden reklamebeskyttelse. Feltet <code>protected</code> er <code>true</code>, "
         "når en virksomhed har frabedt sig reklamehenvendelser, jf. CVR-lovens § 19 og § 22."),
    ],
    "disclaimer_heading": "Vigtig information om reklamebeskyttelse",
    "disclaimer_html": """\
<p>Alle brugere af CVR-API skal overholde reglerne om reklamebeskyttelse i henhold til CVR-loven.</p>
<p><strong>Virksomheder kan frabede sig reklamehenvendelser.</strong> Som bruger forpligter du dig til:</p>
<ul>
    <li>At respektere virksomheders ønske om reklamebeskyttelse</li>
    <li>At oplysninger om reklamebeskyttede virksomheder eller p-enheder ikke må bruges til direkte markedsføring, herunder telefonopkald, målrettede postudsendelser og lignende</li>
    <li>At markere tydeligt ved videregivelse til tredjemand, at en virksomhed eller p-enhed er beskyttet</li>
</ul>
<p><strong>Disse forpligtelser følger af CVR-lovens § 19 og § 22.</strong> Overtrædelse af disse regler kan medføre juridiske konsekvenser.</p>
<p><strong>Referencebrug:</strong> Ved brug af CVR-API accepterer du, at vi kan identificere din organisation som bruger af denne API — baseret på det henvisende domæne i vores analyse — og anvende dit navn eller logo som reference på denne hjemmeside og i relaterede markedsføringsmaterialer. Ønsker du at framelde dig, er du velkommen til at kontakte os.</p>
""",
}

_EN = {
    "lang": "en",
    "locale": "en_US",
    "alt_locale": "da_DK",
    "path": "/en/",
    "alt_path": "/",
    "company_path": "/en/company/",
    "title": "Free CVR API – Danish Company Data as JSON | APICVR.dk",
    "description": (
        "Look up any Danish company with a free CVR API that needs no API key. Get name, address, "
        "owners, management and production units as clean JSON from the official CVR register."
    ),
    "og_title": "CVR API – free, open source, no API key",
    "og_image": "/static/og-en.png",
    "nav_docs": "Docs",
    "nav_endpoints": "Endpoints",
    "nav_faq": "FAQ",
    "eyebrow": "Free · Open source · No API key",
    "h1": "The free CVR API for Danish company data",
    "lead": (
        "Look up any Danish company by CVR number, name, address, email or phone. Get owners, "
        "management and production units back as clean JSON, straight from the Danish Central "
        "Business Register."
    ),
    "cta_try": "Try the API",
    "cta_docs": "Read the docs",
    "stats_heading": "Live API traffic",
    "stats_note": "Updated every 10 minutes",
    "stat_total": "requests served",
    "stat_total_since": "since",
    "stat_30d": "in the last 30 days",
    "stat_per_day": "per day on average",
    "stat_today": "today (UTC)",
    "try_heading": "Try it live",
    "try_sub": "Search for a company name, or type an 8-digit CVR number.",
    "try_placeholder": "E.g. Novo Nordisk or 41013583",
    "code_heading": "One HTTP call. Zero setup.",
    "code_sub": "No keys, no account, no SDK. Call the endpoint from whatever language you already use.",
    "endpoints_heading": "Endpoints",
    "endpoints_sub": "Every endpoint is a GET that returns JSON. See the full specification in the",
    "endpoints_link": "API docs",
    "features_heading": "Why CVR-API?",
    "features": [
        ("No API key", "No sign-up and no token. Send a GET request and you have data in seconds."),
        ("Open source (MIT)", "All source code is on GitHub. Self-host it, fork it, or contribute."),
        ("Owners and management", "Legal owners with ownership share and voting rights, plus management and fully liable participants."),
        ("Typo-tolerant search", "Fuzzy name search that finds the company even when it's misspelled."),
        ("Production units", "Every production unit (P-number) with address, industry and headcount."),
        ("Marketing protection", "The protected field tells you whether a company has opted out of marketing."),
    ],
    "usecases_heading": "Commonly used for",
    "usecases": [
        "Autofilling company details in checkout and sign-up forms",
        "Validating CVR numbers during onboarding and KYC",
        "Enriching CRM records with industry, address and ownership",
        "Invoicing and bookkeeping with correct company details",
    ],
    "faq_heading": "Frequently asked questions",
    "faq": [
        ("What is CVR-API?",
         "CVR-API is a free, open source REST API for the Danish Central Business Register (CVR). "
         "It turns the Danish Business Authority's complex data model into simple, stable JSON."),
        ("Is CVR-API free?",
         "Yes. The API is free and needs no account or API key. Fair-use rate limits apply. "
         "If you need sustained heavy traffic, email noah@noahbohme.com."),
        ("Where does the data come from?",
         "Data comes from distribution.virk.dk, the Danish Business Authority's official CVR distribution. "
         "Lookups happen live, so you get the latest registered information."),
        ("How do I look up a company by CVR number?",
         "Send a GET request to <code>https://apicvr.dk/api/v1/{cvr}</code>, for example "
         "<code>/api/v1/41013583</code>. The response includes name, address, industry, status, "
         "production units, management and owners."),
        ("Can I get owners and management?",
         "Yes. The full lookup includes legal owners with ownership share, plus management. If you only "
         "need the people, use <code>/api/v1/{cvr}/direktion-og-ansvarlig</code>."),
        ("Can I use the data for marketing?",
         "Only for companies without marketing protection. The <code>protected</code> field is "
         "<code>true</code> when a company has opted out of marketing, under sections 19 and 22 of the "
         "Danish CVR Act."),
    ],
    "disclaimer_heading": "Important information about marketing protection",
    "disclaimer_html": """\
<p>All users of CVR-API must comply with the advertising protection rules under Danish CVR law.</p>
<p><strong>Companies may opt out of advertising contact.</strong> As a user you commit to:</p>
<ul>
    <li>Respecting companies' wishes regarding advertising protection</li>
    <li>Not using information about advertising-protected companies or production units for direct marketing, including phone calls, targeted mailings and similar activities</li>
    <li>Clearly marking when passing data to third parties that a company or production unit is protected</li>
</ul>
<p><strong>These obligations follow from CVR Act § 19 and § 22.</strong> Violation of these rules may result in legal consequences.</p>
<p><strong>Reference usage:</strong> By using CVR-API you agree that we may identify your organisation as a user of this API — based on the referring domain observed in our analytics — and use your name or logo as a reference on this website and in related marketing materials. If you wish to opt out, contact us.</p>
""",
}

CONTENT = {"da": _DA, "en": _EN}
