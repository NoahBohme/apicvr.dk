"""SEO guide pages (developer/API intent), rendered by frontend/templates/guide.html.

Company pages are deliberately NOT indexable; these pages target people
building with CVR data instead.

Page schema (one dict per page, in each family module's PAGES list):

    {
        "id": "python",                       # unique across all families
        "family": "language",                 # language | usecase | glossary | integration | compare
        "slug": {"da": "cvr-api-python", "en": "cvr-api-python"},
        "related": ["javascript", "php"],     # ids of other pages
        "updated": "2026-11-06",              # optional; defaults to GUIDES_UPDATED
        "da": {
            "title": "...",        # <title>, <= 60 chars, keyword first
            "description": "...",  # meta description, 120-160 chars
            "h1": "...",
            "lead": "...",         # plain text intro paragraph
            "blocks": [...],       # see below
            "faq": [("question", "answer html"), ...],   # optional, 2-4 items
        },
        "en": {...same keys...},
    }

Blocks (rendered in order):
    ("h2", "Heading text")
    ("p", "paragraph html")                 # may contain <code>, <a>, <strong>
    ("ul", ["item html", ...])
    ("ol", ["item html", ...])
    ("code", "python", "raw source")        # auto-escaped; label shown on the block
    ("note", "callout html")
    ("table", ["Col A", "Col B"], [["cell html", "cell html"], ...])

Use {site} inside any string to get the public origin (https://apicvr.dk).
"""

from . import compare, glossary, integration, language, usecase

FAMILIES = {
    "language": {"da": "Kom i gang i dit sprog", "en": "Get started in your language"},
    "usecase": {"da": "Opslag og søgninger", "en": "Lookups and searches"},
    "integration": {"da": "Integrationer", "en": "Integrations"},
    "glossary": {"da": "Ordbog: CVR-begreber forklaret", "en": "Glossary: CVR terms explained"},
    "compare": {"da": "Sammenligninger og alternativer", "en": "Comparisons and alternatives"},
}

PAGES = [*language.PAGES, *usecase.PAGES, *integration.PAGES, *glossary.PAGES, *compare.PAGES]
BY_ID = {page["id"]: page for page in PAGES}
BY_SLUG = {lang: {page["slug"][lang]: page for page in PAGES} for lang in ("da", "en")}

assert len(BY_ID) == len(PAGES), "duplicate guide id"
assert all(len(BY_SLUG[lang]) == len(PAGES) for lang in BY_SLUG), "duplicate guide slug"
assert all(rid in BY_ID for page in PAGES for rid in page.get("related", [])), "unknown related id"
