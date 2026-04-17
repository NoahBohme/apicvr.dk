# P-numbers on single-CVR response — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `p_units` array with full production-unit detail to the response of `GET /api/v1/{cvrNumber}`.

**Architecture:** All changes live in `apis/searchcvr.py`. Refactor existing helpers to accept a metadata dict so both company and p-unit formatters can share them. Add `fetch_p_units()` to query the `produktionsenhed` index by terms filter, `format_p_unit_data()` to shape each hit, and attach the result as `p_units` on the response dict. No changes to routes, templates, or other endpoints.

**Tech Stack:** Python 3, FastAPI, `requests`, CVR Elasticsearch API (`http://distribution.virk.dk/cvr-permanent/...`).

**Testing note:** The repo has no test framework. Verification is a mix of (a) static import/lint checks via `python -c`, (b) a local `uvicorn` smoke test against one CVR, and (c) final end-to-end verification against `https://cvr.nordplaner.dk/api/v1/{cvrNumber}` after a `kamal deploy`. **Do NOT run `kamal deploy` without explicit user confirmation at the deploy step.**

**Reference spec:** `docs/superpowers/specs/2026-04-17-cvr-p-numbers-design.md`

---

## Task 1: Refactor shared helpers to take a metadata dict

These helpers currently accept the full company document and pluck `virksomhedMetadata` out themselves. We change them to accept the metadata dict directly, so `format_p_unit_data` can reuse them by passing `produktionsEnhedMetadata` instead.

**Files:**
- Modify: `apis/searchcvr.py` (helpers near the bottom, `format_company_data` call sites)

- [ ] **Step 1: Change helper signatures and bodies**

Replace the existing helpers with these versions. Note signatures are changed and bodies read from `metadata` directly.

```python
# Get company/unit name from a metadata dict
def get_name(metadata: dict):
    navn = metadata.get('nyesteNavn') or {}
    return navn.get('navn')

# Get combined address from a metadata dict
def get_combined_address(metadata: dict):
    address = metadata.get('nyesteBeliggenhedsadresse') or {}

    vejnavn = address.get('vejnavn', '')
    if not vejnavn:
        return None

    combined_address = f"{vejnavn} {address.get('husnummerFra', '')}".rstrip()

    if address.get('husnummerTil'):
        combined_address += f"-{address['husnummerTil']}"

    combined_address += address.get('bogstavFra', '') or ''

    if address.get('bogstavTil'):
        combined_address += f"-{address['bogstavTil']}"

    combined_address += f", {address['etage']}" if address.get('etage') else ''

    return combined_address


# Get specific field from the address inside a metadata dict
def get_address_field(metadata: dict, field):
    address = metadata.get('nyesteBeliggenhedsadresse') or {}
    return address.get(field)

# Get formatted date (unchanged)
def get_formatted_date(date):
    if date is None:
        return None
    parts = date.split('-')
    return f"{parts[2]}/{parts[1]} - {parts[0]}"

# Get phone number from metadata
def get_phone_number(metadata: dict):
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
    phone = re.findall(r'\b\d{8}\b', str(contact_info))
    return phone[0] if phone else None

# Get email from metadata
def get_email(metadata: dict):
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
    email = re.findall(r'\b[\w.-]+@[\w.-]+\b', str(contact_info))
    return email[0] if email else None

# Get website from metadata
def get_website(metadata: dict):
    contact_info = metadata.get('nyesteKontaktoplysninger')
    if not contact_info:
        return None
    website = re.findall(r'\bhttp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b', str(contact_info))
    return website[0] if website else None

# Get number of employees from metadata
def get_employees(metadata: dict):
    erst_maaned_beskaeftigelse = metadata.get('nyesteErstMaanedsbeskaeftigelse')
    if erst_maaned_beskaeftigelse:
        return erst_maaned_beskaeftigelse.get('antalAnsatte')
    return None

# Check if the company is bankrupt (unchanged — company-only)
def is_bankrupt(company):
    metadata = company.get('virksomhedMetadata')
    if metadata:
        nyeste_status = metadata.get('nyesteStatus')
        if nyeste_status:
            return nyeste_status.get('kreditoplysningtekst') == "Konkurs"
    return False
```

Also **delete** the old `get_company_name` function — it's replaced by `get_name` taking metadata.

- [ ] **Step 2: Update `format_company_data` call sites**

The function already computes `metadata = company.get('virksomhedMetadata') or {}` at the top. Replace the body so every helper call passes `metadata`:

```python
def format_company_data(company: dict, cvr_number) -> dict:
    """Convert raw company data to the API response schema."""
    metadata = company.get('virksomhedMetadata') or {}
    hovedbranche = metadata.get('nyesteHovedbranche') or {}
    virksomhedsform = metadata.get('nyesteVirksomhedsform') or {}

    livsforloeb = company.get('livsforloeb') or []
    first_period = {}
    if livsforloeb and isinstance(livsforloeb[0], dict):
        first_period = livsforloeb[0].get('periode') or {}

    company_data = {
        "vat": cvr_number,
        "name": get_name(metadata),
        "address": get_combined_address(metadata),
        "zipcode": get_address_field(metadata, 'postnummer'),
        "city": get_address_field(metadata, 'postdistrikt'),
        "cityname": get_address_field(metadata, 'bynavn'),
        "protected": company.get('reklamebeskyttet'),
        "phone": get_phone_number(metadata),
        "email": get_email(metadata),
        "fax": company.get('telefaxNummer'),
        "startdate": get_formatted_date(metadata.get('stiftelsesDato')),
        "enddate": get_formatted_date(first_period.get('gyldigTil')),
        "employees": get_employees(metadata),
        "addressco": get_address_field(metadata, 'conavn'),
        "industrycode": hovedbranche.get('branchekode'),
        "industrydesc": hovedbranche.get('branchetekst'),
        "companycode": virksomhedsform.get('virksomhedsformkode'),
        "companydesc": virksomhedsform.get('langBeskrivelse'),
        "bankrupt": is_bankrupt(company),
        "status": metadata.get('sammensatStatus'),
        "companytypeshort": virksomhedsform.get('kortBeskrivelse'),
        "website": get_website(metadata),
        "version": 1
    }
    return company_data
```

Note: the only changed values vs. current behavior are `name` (now from `get_name(metadata)` instead of `get_company_name(company)`) and every other helper call — all should produce identical output because they read the same underlying fields.

- [ ] **Step 3: Smoke-check the module imports cleanly**

Run from the repo root:

```bash
python -c "from apis.searchcvr import search_cvr_api, format_company_data, get_name, get_combined_address, get_employees; print('OK')"
```

Expected output: `OK`

- [ ] **Step 4: Commit**

```bash
git add apis/searchcvr.py
git commit -m "Refactor shared helpers to accept metadata dict"
```

---

## Task 2: Add `fetch_p_units` function

Query the `produktionsenhed` Elasticsearch index by a list of P-numbers and return raw source dicts. Degrades silently to `[]` on any error so company lookup never breaks.

**Files:**
- Modify: `apis/searchcvr.py` (add new module constant + function)

- [ ] **Step 1: Add the p-unit URL constant**

Near the existing `url = "http://distribution.virk.dk/cvr-permanent/virksomhed/_search"` line, add:

```python
url_p = "http://distribution.virk.dk/cvr-permanent/produktionsenhed/_search"
```

- [ ] **Step 2: Add `fetch_p_units` function**

Add near the top of the file, after `search_cvr_api` (before the other search functions is fine; placement is flexible as long as it's defined before `search_cvr_api` calls it — see Task 4). For clarity, place it **directly after `search_cvr_api`**:

```python
def fetch_p_units(p_numbers: list) -> list:
    """Fetch full production-unit detail for each P-number. Returns [] on any error."""
    if not p_numbers:
        return []

    payload = json.dumps({
        "_source": ["Vrproduktionsenhed"],
        "query": {
            "terms": {
                "Vrproduktionsenhed.pNummer": p_numbers
            }
        },
        "size": 1000
    })
    headers = {
        'Authorization': 'Basic ' + APITOKEN,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url_p, headers=headers, data=payload, timeout=10)
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    try:
        json_response = response.json()
    except ValueError:
        return []

    hits = json_response.get('hits', {}).get('hits', [])
    p_units = []
    for hit in hits:
        p_unit = hit.get('_source', {}).get('Vrproduktionsenhed')
        if p_unit:
            p_units.append(format_p_unit_data(p_unit))
    return p_units
```

Note: this references `format_p_unit_data`, which we add in Task 3. Python resolves function names at call time, not definition time, so defining `fetch_p_units` before `format_p_unit_data` is fine — but we will not call `fetch_p_units` from anywhere until Task 4.

- [ ] **Step 3: Confirm module still imports**

```bash
python -c "from apis.searchcvr import fetch_p_units; print(fetch_p_units([]))"
```

Expected output: `[]`

- [ ] **Step 4: Commit**

```bash
git add apis/searchcvr.py
git commit -m "Add fetch_p_units for production-unit lookup"
```

---

## Task 3: Add `format_p_unit_data` function

Mirror `format_company_data` but for a production unit. All helpers from Task 1 are reused by passing `produktionsEnhedMetadata`.

**Files:**
- Modify: `apis/searchcvr.py` (add new function near `format_company_data`)

- [ ] **Step 1: Add the function**

Place this immediately **before** `format_company_data` so callers see a natural grouping (formatters together):

```python
def format_p_unit_data(p_unit: dict) -> dict:
    """Convert raw production-unit data to the API response schema."""
    metadata = p_unit.get('produktionsEnhedMetadata') or {}
    hovedbranche = metadata.get('nyesteHovedbranche') or {}

    livsforloeb = p_unit.get('livsforloeb') or []
    first_period = {}
    if livsforloeb and isinstance(livsforloeb[0], dict):
        first_period = livsforloeb[0].get('periode') or {}

    return {
        "p_number": p_unit.get('pNummer'),
        "name": get_name(metadata),
        "address": get_combined_address(metadata),
        "zipcode": get_address_field(metadata, 'postnummer'),
        "city": get_address_field(metadata, 'postdistrikt'),
        "cityname": get_address_field(metadata, 'bynavn'),
        "addressco": get_address_field(metadata, 'conavn'),
        "phone": get_phone_number(metadata),
        "email": get_email(metadata),
        "website": get_website(metadata),
        "fax": p_unit.get('telefaxNummer'),
        "startdate": get_formatted_date(metadata.get('stiftelsesDato')),
        "enddate": get_formatted_date(first_period.get('gyldigTil')),
        "industrycode": hovedbranche.get('branchekode'),
        "industrydesc": hovedbranche.get('branchetekst'),
        "employees": get_employees(metadata),
        "protected": p_unit.get('reklamebeskyttet'),
    }
```

- [ ] **Step 2: Confirm module still imports**

```bash
python -c "from apis.searchcvr import format_p_unit_data; print(format_p_unit_data({}))"
```

Expected: a dict printed with all values set to `None` except any defaults. No exception.

- [ ] **Step 3: Commit**

```bash
git add apis/searchcvr.py
git commit -m "Add format_p_unit_data for production-unit response shape"
```

---

## Task 4: Attach `p_units` to `search_cvr_api` response

Collect P-numbers from the company document's `penheder` array and enrich.

**Files:**
- Modify: `apis/searchcvr.py` — `search_cvr_api`

- [ ] **Step 1: Update `search_cvr_api` to attach `p_units`**

Replace the final `else` branch of `search_cvr_api`. The current code reads:

```python
    if json_response['hits']['total'] == 0:
        return {"error": "NOT_FOUND"}
    else:
        company = json_response['hits']['hits'][0]['_source']['Vrvirksomhed']
        return format_company_data(company, cvr_number)
```

Change to:

```python
    if json_response['hits']['total'] == 0:
        return {"error": "NOT_FOUND"}
    else:
        company = json_response['hits']['hits'][0]['_source']['Vrvirksomhed']
        company_data = format_company_data(company, cvr_number)

        penheder = company.get('penheder') or []
        p_numbers = [
            p['pNummer']
            for p in penheder
            if isinstance(p, dict) and p.get('pNummer')
        ]
        company_data['p_units'] = fetch_p_units(p_numbers)

        return company_data
```

- [ ] **Step 2: Confirm module still imports**

```bash
python -c "from apis.searchcvr import search_cvr_api; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Local smoke test against the CVR API**

Ensure `.env` has a valid `API_TOKEN` (or export it in the shell). Then:

```bash
uvicorn main:app --port 8000 &
UVICORN_PID=$!
sleep 3
curl -s http://localhost:8000/api/v1/28271026 | python -m json.tool | head -60
kill $UVICORN_PID
```

Expected: JSON response includes `"p_units": [ ... ]` with at least one entry for a company known to have production units. The pre-existing fields (`vat`, `name`, `address`, etc.) are unchanged.

If you don't have a known CVR with P-units handy, use any large Danish company's CVR (e.g. `28271026` Coop Danmark, or ask the user for a known-good test CVR).

If the company has zero P-units, `"p_units": []` is the expected value.

- [ ] **Step 4: Commit**

```bash
git add apis/searchcvr.py
git commit -m "Return p_units list on single-CVR API response"
```

---

## Task 5: Deploy and verify live

**Files:** none (deploy + manual verification only)

- [ ] **Step 1: Push to origin**

```bash
git push origin master
```

- [ ] **Step 2: Ask the user for explicit confirmation before deploying**

Stop and ask: *"All changes are pushed. Ready to run `kamal deploy`?"* Wait for an explicit yes before running the next step. Do NOT run `kamal deploy` on your own.

- [ ] **Step 3: Run `kamal deploy` (only after user confirms)**

```bash
kamal deploy
```

Expected: deploy completes without error.

- [ ] **Step 4: Verify against the live URL**

Pick a CVR known to have multiple P-numbers and hit:

```bash
curl -s https://cvr.nordplaner.dk/api/v1/28271026 | python -m json.tool | head -80
```

Verify:
- Top-level `p_units` key exists
- It is a JSON array
- Each element has `p_number`, `name`, `address`, `startdate`, `industrycode`, `employees`, etc.
- Existing top-level fields (`vat`, `name`, `phone`, `email`, ...) are unchanged

Also hit a CVR with no P-units (any sole-proprietorship CVR will do) and verify `"p_units": []`.

- [ ] **Step 5: Report completion to the user**

Report the tested CVR numbers and confirm both the populated and empty cases behave as expected.
