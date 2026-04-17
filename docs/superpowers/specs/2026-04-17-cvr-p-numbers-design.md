# Include P-numbers on single-CVR API response

## Goal

Add a list of production units (P-numbers / *produktionsenheder*) to the response of `GET /api/v1/{cvrNumber}`. Each item is returned with full detail (parity with company-level fields).

Only this endpoint is affected. Search endpoints (`/search/company`, `/fuzzy_search/company`, `/email/...`, `/phone/...`, `/search/address`) remain unchanged.

## Motivation

A Danish company (CVR number) may have many production units, each with its own name, address, industry code, contact info, and headcount. The current API surfaces none of this. Consumers doing a single-company lookup need the full P-number list to model sites, locations, or dependent activity.

## Response shape

A new top-level key `p_units` is added to the existing response dict. Its value is a JSON array, possibly empty. Ordering is the order returned by the CVR index (no explicit sort).

Each element mirrors the company schema where fields are meaningful for a production unit:

| Field          | Source (under `Vrproduktionsenhed`)                                    |
|----------------|------------------------------------------------------------------------|
| `p_number`     | `pNummer`                                                              |
| `name`         | `produktionsEnhedMetadata.nyesteNavn.navn`                             |
| `address`      | derived from `produktionsEnhedMetadata.nyesteBeliggenhedsadresse`      |
| `zipcode`      | `produktionsEnhedMetadata.nyesteBeliggenhedsadresse.postnummer`        |
| `city`         | `produktionsEnhedMetadata.nyesteBeliggenhedsadresse.postdistrikt`      |
| `cityname`     | `produktionsEnhedMetadata.nyesteBeliggenhedsadresse.bynavn`            |
| `addressco`    | `produktionsEnhedMetadata.nyesteBeliggenhedsadresse.conavn`            |
| `phone`        | extracted from `produktionsEnhedMetadata.nyesteKontaktoplysninger`     |
| `email`        | extracted from `produktionsEnhedMetadata.nyesteKontaktoplysninger`     |
| `website`      | extracted from `produktionsEnhedMetadata.nyesteKontaktoplysninger`     |
| `fax`          | `telefaxNummer` (top-level on the P-unit doc, mirrors company)         |
| `startdate`    | `produktionsEnhedMetadata.stiftelsesDato`, formatted `dd/mm - yyyy`    |
| `enddate`      | `livsforloeb[0].periode.gyldigTil`, formatted the same way             |
| `industrycode` | `produktionsEnhedMetadata.nyesteHovedbranche.branchekode`              |
| `industrydesc` | `produktionsEnhedMetadata.nyesteHovedbranche.branchetekst`             |
| `employees`    | `produktionsEnhedMetadata.nyesteErstMaanedsbeskaeftigelse.antalAnsatte`|
| `protected`    | `reklamebeskyttet`                                                     |

All fields are optional and may be `null` when the source field is absent. Closed P-numbers are included (no filtering). Consumers infer active/closed status from `enddate`.

## Architecture

Change is scoped to `apis/searchcvr.py`. No changes to `main.py` or templates.

**New constant**

```
url_p = "http://distribution.virk.dk/cvr-permanent/produktionsenhed/_search"
```

**New function `fetch_p_units(p_numbers: list[int]) -> list[dict]`**

- Returns `[]` if `p_numbers` is empty.
- POSTs to `url_p` with payload:
  ```json
  {
    "_source": ["Vrproduktionsenhed"],
    "query": {"terms": {"Vrproduktionsenhed.pNummer": [...]}},
    "size": 1000
  }
  ```
- Uses the same `Authorization: Basic <APITOKEN>` header and `timeout=10` as existing calls.
- On non-200 response, JSON parse failure, or request exception: returns `[]`. No exception propagates to the endpoint.
- On success: iterates `json_response['hits']['hits']`, calls `format_p_unit_data` per hit, returns the list.

**New function `format_p_unit_data(p_unit: dict) -> dict`**

Mirrors `format_company_data` but reads from `produktionsEnhedMetadata` instead of `virksomhedMetadata` and uses `pNummer` instead of `cvrNummer`.

**Shared helpers (small refactor)**

The existing `get_combined_address`, `get_address_field`, `get_phone_number`, `get_email`, and `get_website` helpers read `company['virksomhedMetadata']` internally. They will be refactored to take a metadata dict directly, so both `format_company_data` and `format_p_unit_data` can reuse them:

```
def get_combined_address(metadata: dict) -> Optional[str]
def get_address_field(metadata: dict, field: str)
def get_phone_number(metadata: dict) -> Optional[str]
def get_email(metadata: dict) -> Optional[str]
def get_website(metadata: dict) -> Optional[str]
def get_employees(metadata: dict)
```

Call sites inside `format_company_data` are updated to pass `company.get('virksomhedMetadata') or {}` explicitly. Behavior is unchanged.

**Modified `search_cvr_api`**

After building `company_data` via `format_company_data`, collect P-numbers:

```
penheder = company.get('penheder') or []
p_numbers = [p['pNummer'] for p in penheder if isinstance(p, dict) and p.get('pNummer')]
company_data['p_units'] = fetch_p_units(p_numbers)
```

Attach to the returned dict.

## Error handling

- Company lookup error paths (`HTTP_ERROR`, `INVALID_RESPONSE`, `NOT_FOUND`) are unchanged. They return early without touching `fetch_p_units`.
- P-unit fetch failures degrade silently to `p_units: []`. The main response still succeeds.
- A company with zero P-numbers returns `p_units: []`.

## Testing / verification

No automated test suite exists in the repo; verification is manual.

1. Implement locally.
2. Commit and push.
3. Ask the user for confirmation before running `kamal deploy`.
4. Once deployed, hit `https://cvr.nordplaner.dk/api/v1/{cvrNumber}` against a CVR known to have multiple P-numbers.
5. Confirm `p_units` is a populated array with the expected fields and that a CVR with no P-numbers returns `p_units: []`.

## Out of scope

- Adding `p_units` to the search endpoints.
- Dedicated `/api/v1/pnummer/{pNumber}` lookup endpoint.
- Filtering by active/inactive status at the API layer.
- Caching, pagination, or sort order for `p_units`.
- Frontend template changes (the `/da/virksomhed/{cvrNumber}` Jinja template is not required to render P-numbers as part of this change).
