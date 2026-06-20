from mcp.server.fastmcp import FastMCP
from apis.searchcvr import (
    search_cvr_api,
    search_cvr_by_name,
    search_cvr_by_fuzzy_name,
    search_cvr_by_email,
    search_cvr_by_email_domain,
    search_cvr_by_phone,
    search_cvr_by_address,
)

mcp = FastMCP("APICVR.dk")


@mcp.tool()
def lookup_company(cvr_number: int) -> dict:
    """Look up a Danish company by its CVR number (8-digit company registration number)."""
    return search_cvr_api(cvr_number)


@mcp.tool()
def search_company_by_name(name: str) -> list:
    """Search for Danish companies by name (prefix match)."""
    return search_cvr_by_name(name)


@mcp.tool()
def search_company_fuzzy(name: str) -> list:
    """Search for Danish companies by name using fuzzy matching."""
    return search_cvr_by_fuzzy_name(name)


@mcp.tool()
def search_company_by_email(email: str) -> list:
    """Find Danish companies registered with the given email address."""
    return search_cvr_by_email(email)


@mcp.tool()
def search_company_by_email_domain(domain: str) -> list:
    """Find Danish companies whose email matches the given domain (e.g. 'example.com')."""
    return search_cvr_by_email_domain(domain)


@mcp.tool()
def search_company_by_phone(phone: str) -> list:
    """Find Danish companies registered with the given phone number."""
    return search_cvr_by_phone(phone)


@mcp.tool()
def search_company_by_address(address: str, postal_code: str = None) -> list:
    """Find Danish companies at the given street address. Optionally filter by postal code."""
    return search_cvr_by_address(address, postal_code)


if __name__ == "__main__":
    mcp.run()
