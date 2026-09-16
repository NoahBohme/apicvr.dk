"""
Client for the Danish CVR distribution API (distribution.virk.dk).

Wraps the Elasticsearch endpoints ERST exposes for the public register
of companies. Public functions all return plain dicts / lists so the FastAPI
routes and the Jinja templates can consume them directly.

Failures return a stable error dict:
    {"error": <machine-readable code>, "status": <int|None>, "message": <str|None>}
Route handlers convert these to HTTPException; templates render an error box.
"""
import json
import os
import re
from typing import Any, Iterable, Optional

import requests
from dotenv import load_dotenv


load_dotenv()

# --- Configuration ---------------------------------------------------------

_API_TOKEN = os.getenv("API_TOKEN", "")
_BASE = "http://distribution.virk.dk"
_COMPANY_URL = f"{_BASE}/cvr-permanent/virksomhed/_search"
_PRODUCTION_UNIT_URL = f"{_BASE}/cvr-permanent/produktionsenhed/_search"
_TIMEOUT = 10

_HEADERS = {
    "Authorization": f"Basic {_API_TOKEN}",
    "Content-Type": "application/json",
}

# Only currently-active roles are surfaced (FUNKTION periode.gyldigTil is None).
_DIRECTOR_FUNCTIONS = {"DIREKTØR", "ADM. DIR."}

# CVR ownership display buckets: (low, high, label) — half-open [low, high).
_OWNERSHIP_BUCKETS = [
    (0.05,   0.10,   "5-9,99%"),
    (0.10,   0.15,   "10-14,99%"),
    (0.15,   0.20,   "15-19,99%"),
    (0.20,   0.25,   "20-24,99%"),
    (0.25,   0.3333, "25-33,32%"),
    (0.3333, 0.50,   "33,33-49,99%"),
    (0.50,   0.6667, "50-66,66%"),
    (0.6667, 0.90,   "66,67-89,99%"),
    (0.90,   1.00,   "90-99,99%"),
]


# --- Internal transport ----------------------------------------------------

def _post_search(
    query: dict,
    *,
    endpoint: str = _COMPANY_URL,
    size: int = 100,
    source: Optional[list] = None,
) -> Any:
    """POST an Elasticsearch query. Returns the parsed body, or an error dict."""
    payload = {
        "_source": source or ["Vrvirksomhed"],
        "query": query,
        "size": size,
    }
    try:
        response = requests.post(
            endpoint, headers=_HEADERS, data=json.dumps(payload), timeout=_TIMEOUT
        )
    except requests.RequestException as exc:
        return {"error": "TRANSPORT_ERROR", "status": None, "message": str(exc)}

    if response.status_code != 200:
        return {
            "error": "HTTP_ERROR",
            "status": response.status_code,
            "message": response.text,
        }

    try:
        return response.json()
    except ValueError:
        return {
            "error": "INVALID_RESPONSE",
            "status": response.status_code,
            "message": response.text,
        }


def _is_error(result: Any) -> bool:
    return isinstance(result, dict) and bool(result.get("error"))


def _hits(result: Any) -> list:
    if _is_error(result) or not isinstance(result, dict):
        return []
    return result.get("hits", {}).get("hits", []) or []


def _companies_from_hits(hits: list) -> list:
    out = []
    for hit in hits:
        company = hit.get("_source", {}).get("Vrvirksomhed", {})
        cvr_number = company.get("cvrNummer")
        if cvr_number is None:
            continue
        out.append(format_company_data(company, cvr_number))
    return out


def _not_found() -> dict:
    return {"error": "NOT_FOUND", "status": 404, "message": None}


# --- Public search API -----------------------------------------------------

def search_cvr_api(cvr_number: int) -> dict:
    """Look up a company by CVR number, including production units and relations."""
    result = _post_search({"term": {"Vrvirksomhed.cvrNummer": cvr_number}}, size=1)
    if _is_error(result):
        return result

    hits = _hits(result)
    if not hits:
        return _not_found()

    company = hits[0]["_source"]["Vrvirksomhed"]
    data = format_company_data(company, cvr_number)

    p_numbers = [
        p["pNummer"]
        for p in company.get("penheder") or []
        if isinstance(p, dict) and p.get("pNummer")
    ]
    data["p_units"] = fetch_p_units(p_numbers)

    direktion, fuldt_ansvarlige, ejere = _extract_current_relations(company)
    data["direktion"] = direktion
    data["fuldt_ansvarlige"] = fuldt_ansvarlige
    data["ejere"] = ejere
    return data


def get_company_relations(cvr_number: int) -> dict:
    """Return only current direktion, fully-liable participants, and legal owners."""
    result = _post_search(
        {"term": {"Vrvirksomhed.cvrNummer": cvr_number}},
        source=["Vrvirksomhed.cvrNummer", "Vrvirksomhed.deltagerRelation"],
        size=1,
    )
    if _is_error(result):
        return result

    hits = _hits(result)
    if not hits:
        return _not_found()

    company = hits[0]["_source"].get("Vrvirksomhed", {}) or {}
    direktion, fuldt_ansvarlige, ejere = _extract_current_relations(company)
    return {
        "vat": cvr_number,
        "direktion": direktion,
        "fuldt_ansvarlige": fuldt_ansvarlige,
        "ejere": ejere,
    }


def search_cvr_combined(
    name: Optional[str] = None,
    cvr: Optional[int] = None,
    limit: int = 100,
) -> Any:
    """Search by name and/or CVR number. At least one must be provided."""
    must: list = []
    if cvr is not None:
        must.append({"term": {"Vrvirksomhed.cvrNummer": cvr}})
    if name:
        must.append({
            "match_phrase_prefix": {
                "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": name
            }
        })
    if not must:
        return []

    result = _post_search({"bool": {"must": must}}, size=limit)
    if _is_error(result):
        return result
    return _companies_from_hits(_hits(result))


def search_cvr_by_name(company_name: str, limit: int = 100) -> Any:
    """Match companies whose current name starts with the query."""
    result = _post_search(
        {"match_phrase_prefix": {
            "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": company_name
        }},
        size=limit,
    )
    if _is_error(result):
        return result
    return _companies_from_hits(_hits(result))


def search_cvr_by_fuzzy_name(company_name: str, limit: int = 100) -> Any:
    """Fuzzy-match on current company name. Returns a slimmer shape."""
    result = _post_search(
        {"multi_match": {
            "query": company_name,
            "fields": ["Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn^2"],
            "fuzziness": "AUTO",
        }},
        size=limit,
    )
    if _is_error(result):
        return result

    out = []
    for hit in _hits(result):
        company = hit.get("_source", {}).get("Vrvirksomhed", {})
        metadata = company.get("virksomhedMetadata") or {}
        nyeste_navn = metadata.get("nyesteNavn") or {}
        hovedbranche = metadata.get("nyesteHovedbranche") or {}
        out.append({
            "name": nyeste_navn.get("navn", "Unknown"),
            "cvr_number": company.get("cvrNummer"),
            "industrycode": hovedbranche.get("branchekode", "Unknown"),
            "industrytext": hovedbranche.get("branchetekst", "Unknown"),
        })
    return out


def search_cvr_by_email(email: str, limit: int = 100) -> Any:
    """Find companies registered with the given email address."""
    result = _post_search(
        {"match": {"Vrvirksomhed.elektroniskPost.kontaktoplysning": email}},
        source=["*"],
        size=limit,
    )
    if _is_error(result):
        return result
    return _companies_from_hits(_hits(result))


def search_cvr_by_email_domain(email_domain: str, limit: int = 100) -> Any:
    """Find companies whose registered email is on the given domain."""
    return search_cvr_by_email(f"@{email_domain}", limit=limit)


def search_cvr_by_phone(phone_number: str, limit: int = 100) -> Any:
    """Find companies by registered phone number."""
    result = _post_search(
        {"match": {"Vrvirksomhed.telefonNummer.kontaktoplysning": phone_number}},
        source=["*"],
        size=limit,
    )
    if _is_error(result):
        return result
    return _companies_from_hits(_hits(result))


def search_cvr_by_address(
    address: str,
    postal_code: Optional[str] = None,
    limit: int = 100,
) -> Any:
    """Find companies at an address; falls back to structured then fuzzy match."""
    cleaned = address.strip()
    if not cleaned:
        return []

    components = _parse_address_components(cleaned)
    filters = _postal_code_filter(postal_code)

    for build in (
        lambda: _exact_address_query(cleaned, filters),
        lambda: _structured_address_query(components, filters),
        lambda: _fuzzy_address_query(cleaned, filters),
    ):
        query = build()
        if query is None:
            continue
        result = _post_search(query["query"], size=limit)
        if _is_error(result):
            return result
        companies = _companies_from_hits(_hits(result))
        if companies:
            return companies
    return []


def fetch_p_units(p_numbers: list) -> list:
    """Fetch full production-unit detail for each P-number. Returns [] on error."""
    if not p_numbers:
        return []
    result = _post_search(
        {"terms": {"VrproduktionsEnhed.pNummer": p_numbers}},
        endpoint=_PRODUCTION_UNIT_URL,
        source=["VrproduktionsEnhed"],
        size=1000,
    )
    return [
        format_p_unit_data(hit["_source"]["VrproduktionsEnhed"])
        for hit in _hits(result)
        if hit.get("_source", {}).get("VrproduktionsEnhed")
    ]


# --- Address query builders ------------------------------------------------

def _postal_code_filter(postal_code: Optional[str]) -> list:
    if not postal_code:
        return []
    trimmed = postal_code.strip()
    if not trimmed:
        return []
    value: Any = int(trimmed) if trimmed.isdigit() else trimmed
    return [{"term": {
        "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.postnummer": value
    }}]


def _exact_address_query(address: str, filters: list) -> Optional[dict]:
    if not address:
        return None
    bool_q: dict = {"must": [{
        "match_phrase": {
            "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.adressebetegnelse": address
        }
    }]}
    if filters:
        bool_q["filter"] = filters
    return {"query": {"bool": bool_q}}


def _structured_address_query(components: dict, filters: list) -> Optional[dict]:
    street = components.get("street")
    number = components.get("number")
    letter = components.get("letter")
    if not street or number is None:
        return None
    must = [
        {"match_phrase": {
            "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.vejnavn": street
        }},
        {"term": {
            "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.husnummerFra": number
        }},
    ]
    if letter:
        must.append({"term": {
            "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.bogstavFra": letter
        }})
    bool_q: dict = {"must": must}
    if filters:
        bool_q["filter"] = filters
    return {"query": {"bool": bool_q}}


def _fuzzy_address_query(address: str, filters: list) -> dict:
    bool_q: dict = {"must": [{
        "multi_match": {
            "query": address,
            "fields": [
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.adressebetegnelse^3",
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.fritekst^2",
                "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse.vejnavn",
            ],
            "fuzziness": "AUTO",
            "type": "best_fields",
            "operator": "or",
        }
    }]}
    if filters:
        bool_q["filter"] = filters
    return {"query": {"bool": bool_q}}


_ADDRESS_RE = re.compile(
    r"^(?P<street>[^0-9]+?)\s+(?P<number>\d+)(?:\s*(?P<letter>[A-Za-z]))?$"
)


def _parse_address_components(address: str) -> dict:
    main = address.partition(",")[0].strip()
    if not main:
        return {"street": None, "number": None, "letter": None}
    m = _ADDRESS_RE.match(main)
    if not m:
        return {"street": None, "number": None, "letter": None}
    return {
        "street": (m.group("street") or "").strip() or None,
        "number": int(m.group("number")) if m.group("number") else None,
        "letter": (m.group("letter") or "").upper() or None,
    }


# --- Formatters ------------------------------------------------------------

def format_company_data(company: dict, cvr_number: int) -> dict:
    """Convert raw Vrvirksomhed to the public API response schema."""
    metadata = company.get("virksomhedMetadata") or {}
    hovedbranche = metadata.get("nyesteHovedbranche") or {}
    virksomhedsform = metadata.get("nyesteVirksomhedsform") or {}
    livsforloeb = company.get("livsforloeb") or []
    first_period = _first_period(livsforloeb)

    return {
        "vat": cvr_number,
        "name": _metadata_name(metadata),
        "address": _combined_address(metadata),
        "zipcode": _address_field(metadata, "postnummer"),
        "city": _address_field(metadata, "postdistrikt"),
        "cityname": _address_field(metadata, "bynavn"),
        "protected": company.get("reklamebeskyttet"),
        "phone": _contact_phone(metadata),
        "email": _contact_email(metadata),
        "fax": company.get("telefaxNummer"),
        "startdate": metadata.get("stiftelsesDato"),
        "enddate": first_period.get("gyldigTil"),
        "employees": _employees(metadata),
        "addressco": _address_field(metadata, "conavn"),
        "industrycode": hovedbranche.get("branchekode"),
        "industrydesc": hovedbranche.get("branchetekst"),
        "companycode": virksomhedsform.get("virksomhedsformkode"),
        "companydesc": virksomhedsform.get("langBeskrivelse"),
        "bankrupt": _is_bankrupt(metadata),
        "status": metadata.get("sammensatStatus"),
        "companytypeshort": virksomhedsform.get("kortBeskrivelse"),
        "website": _contact_website(metadata),
        "version": 1,
    }


def format_p_unit_data(p_unit: dict) -> dict:
    """Convert raw VrproduktionsEnhed to the public API response schema."""
    metadata = p_unit.get("produktionsEnhedMetadata") or {}
    hovedbranche = metadata.get("nyesteHovedbranche") or {}
    livsforloeb = p_unit.get("livsforloeb") or []
    first_period = _first_period(livsforloeb)

    return {
        "p_number": p_unit.get("pNummer"),
        "name": _metadata_name(metadata),
        "address": _combined_address(metadata),
        "zipcode": _address_field(metadata, "postnummer"),
        "city": _address_field(metadata, "postdistrikt"),
        "cityname": _address_field(metadata, "bynavn"),
        "addressco": _address_field(metadata, "conavn"),
        "phone": _contact_phone(metadata),
        "email": _contact_email(metadata),
        "website": _contact_website(metadata),
        "fax": p_unit.get("telefaxNummer"),
        "startdate": first_period.get("gyldigFra"),
        "enddate": first_period.get("gyldigTil"),
        "industrycode": hovedbranche.get("branchekode"),
        "industrydesc": hovedbranche.get("branchetekst"),
        "employees": _employees(metadata),
        "protected": p_unit.get("reklamebeskyttet"),
    }


# --- Metadata helpers ------------------------------------------------------

def _first_period(livsforloeb: list) -> dict:
    if livsforloeb and isinstance(livsforloeb[0], dict):
        return livsforloeb[0].get("periode") or {}
    return {}


def _metadata_name(metadata: dict) -> Optional[str]:
    return (metadata.get("nyesteNavn") or {}).get("navn")


def _combined_address(metadata: dict) -> Optional[str]:
    return _format_address_line(metadata.get("nyesteBeliggenhedsadresse") or {})


def _address_field(metadata: dict, field: str):
    return (metadata.get("nyesteBeliggenhedsadresse") or {}).get(field)


_PHONE_RE = re.compile(r"\b\d{8}\b")
_EMAIL_RE = re.compile(r"\b[\w.-]+@[\w.-]+\b")
_URL_RE = re.compile(
    r"\bhttps?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F]{2}))+\b"
)


def _contact_phone(metadata: dict) -> Optional[str]:
    info = metadata.get("nyesteKontaktoplysninger")
    if not info:
        return None
    match = _PHONE_RE.findall(str(info))
    return match[0] if match else None


def _contact_email(metadata: dict) -> Optional[str]:
    info = metadata.get("nyesteKontaktoplysninger")
    if not info:
        return None
    match = _EMAIL_RE.findall(str(info))
    return match[0] if match else None


def _contact_website(metadata: dict) -> Optional[str]:
    info = metadata.get("nyesteKontaktoplysninger")
    if not info:
        return None
    match = _URL_RE.findall(str(info))
    return match[0] if match else None


def _employees(metadata: dict) -> Optional[int]:
    return (metadata.get("nyesteErstMaanedsbeskaeftigelse") or {}).get("antalAnsatte")


def _is_bankrupt(metadata: dict) -> bool:
    return (metadata.get("nyesteStatus") or {}).get("kreditoplysningtekst") == "Konkurs"


# --- Address line formatting (shared by company + deltager) ---------------

def _format_address_line(address: dict) -> Optional[str]:
    vejnavn = address.get("vejnavn")
    if not vejnavn:
        return None
    line = f"{vejnavn} {address.get('husnummerFra', '') or ''}".rstrip()
    if address.get("husnummerTil"):
        line += f"-{address['husnummerTil']}"
    line += address.get("bogstavFra") or ""
    if address.get("bogstavTil"):
        line += f"-{address['bogstavTil']}"
    if address.get("etage"):
        line += f", {address['etage']}"
    return line


# --- Direktion / Fuldt ansvarlige / Ejere ---------------------------------

def _extract_current_relations(company: dict) -> tuple:
    """Return (direktion, fuldt_ansvarlige, ejere) — currently-active entries only."""
    direktion: list = []
    fuldt_ansvarlige: list = []
    ejere: list = []

    for relation in company.get("deltagerRelation") or []:
        deltager = relation.get("deltager") or {}
        for org in relation.get("organisationer") or []:
            hovedtype = org.get("hovedtype")
            if hovedtype == "LEDELSESORGAN":
                for value, periode in _iter_current_funktioner(org):
                    if value in _DIRECTOR_FUNCTIONS:
                        direktion.append(_format_deltager(deltager, value, periode.get("gyldigFra")))
            elif hovedtype == "FULDT_ANSVARLIG_DELTAGERE":
                for value, periode in _iter_current_funktioner(org):
                    fuldt_ansvarlige.append(_format_deltager(deltager, value, periode.get("gyldigFra")))
            elif hovedtype == "REGISTER" and _is_ejerregister(org):
                owner = _format_owner(deltager, org)
                if owner is not None:
                    ejere.append(owner)

    return direktion, fuldt_ansvarlige, ejere


def _iter_current_funktioner(organisation: dict) -> Iterable[tuple]:
    for member in organisation.get("medlemsData") or []:
        for attribute in member.get("attributter") or []:
            if attribute.get("type") != "FUNKTION":
                continue
            for value in attribute.get("vaerdier") or []:
                periode = value.get("periode") or {}
                if periode.get("gyldigTil") is None:
                    yield value.get("vaerdi"), periode


def _is_ejerregister(organisation: dict) -> bool:
    return any(
        isinstance(entry, dict) and entry.get("navn") == "EJERREGISTER"
        for entry in organisation.get("organisationsNavn") or []
    )


def _format_deltager(deltager: dict, role: str, startdate) -> dict:
    address = _current_deltager_address(deltager.get("beliggenhedsadresse"))
    enhedstype = deltager.get("enhedstype")
    return {
        "name": _current_deltager_name(deltager.get("navne")),
        "role": role,
        "type": enhedstype,
        "cvr": deltager.get("forretningsnoegle") if enhedstype == "VIRKSOMHED" else None,
        "address": _format_address_line(address) if address else None,
        "zipcode": address.get("postnummer") if address else None,
        "city": address.get("postdistrikt") if address else None,
        "country": address.get("landekode") if address else None,
        "startdate": startdate,
    }


def _format_owner(deltager: dict, organisation: dict) -> Optional[dict]:
    ownership = _current_owner_attribute(organisation, "EJERANDEL_PROCENT")
    voting = _current_owner_attribute(organisation, "EJERANDEL_STEMMERET_PROCENT")
    if ownership is None and voting is None:
        return None
    startdate = ownership[1] if ownership else (voting[1] if voting else None)

    address = _current_deltager_address(deltager.get("beliggenhedsadresse"))
    enhedstype = deltager.get("enhedstype")
    return {
        "name": _current_deltager_name(deltager.get("navne")),
        "type": enhedstype,
        "cvr": deltager.get("forretningsnoegle") if enhedstype == "VIRKSOMHED" else None,
        "address": _format_address_line(address) if address else None,
        "zipcode": address.get("postnummer") if address else None,
        "city": address.get("postdistrikt") if address else None,
        "country": address.get("landekode") if address else None,
        "ownership_percent": ownership[0] if ownership else None,
        "ownership_range": _ownership_range(ownership[0]) if ownership else None,
        "voting_rights_percent": voting[0] if voting else None,
        "voting_rights_range": _ownership_range(voting[0]) if voting else None,
        "startdate": startdate,
    }


def _current_owner_attribute(organisation: dict, attribute_type: str):
    for member in organisation.get("medlemsData") or []:
        for attribute in member.get("attributter") or []:
            if attribute.get("type") != attribute_type:
                continue
            for value in attribute.get("vaerdier") or []:
                periode = value.get("periode") or {}
                if periode.get("gyldigTil") is not None:
                    continue
                try:
                    return float(value.get("vaerdi")), periode.get("gyldigFra")
                except (TypeError, ValueError):
                    return None
    return None


def _ownership_range(percent: Optional[float]) -> Optional[str]:
    if percent is None:
        return None
    if percent >= 1.0:
        return "100%"
    for low, high, label in _OWNERSHIP_BUCKETS:
        if low <= percent < high:
            return label
    return None


def _current_deltager_name(navne) -> Optional[str]:
    if not navne:
        return None
    for entry in navne:
        if isinstance(entry, dict) and (entry.get("periode") or {}).get("gyldigTil") is None:
            navn = entry.get("navn")
            if navn:
                return navn
    first = navne[0]
    return first.get("navn") if isinstance(first, dict) else None


def _current_deltager_address(addresses) -> Optional[dict]:
    if not addresses:
        return None
    for entry in addresses:
        if isinstance(entry, dict) and (entry.get("periode") or {}).get("gyldigTil") is None:
            return entry
    first = addresses[0]
    return first if isinstance(first, dict) else None
