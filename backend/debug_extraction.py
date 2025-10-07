#!/usr/bin/env python3
"""
Debug script to see actual HTML from Dover portal
"""

import asyncio
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

from app.services.mcp_clients.firecrawl_client import FirecrawlClient


async def debug():
    url = "https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00"

    # Modify URL to details tab (as agent does)
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params["activeTab"] = ["details"]

    new_query = urlencode(query_params, doseq=True)
    details_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))

    print(f"Fetching: {details_url}")
    print()

    client = FirecrawlClient()
    html = await client.fetch(details_url)

    print(f"HTML length: {len(html)} bytes")
    print()

    # Parse and look for applicant/agent related content
    soup = BeautifulSoup(html, "html.parser")

    # Look for tables
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables")
    print()

    # Look for rows with "applicant" or "agent"
    print("Searching for applicant/agent references...")
    print("=" * 80)

    for row in soup.find_all("tr"):
        text = row.get_text().strip()
        if "applicant" in text.lower() or "agent" in text.lower():
            cells = row.find_all("td")
            print(f"Found row with {len(cells)} cells:")
            for i, cell in enumerate(cells):
                print(f"  Cell {i}: {cell.get_text().strip()[:100]}")
            print()

    # Also search for dt/dd structures
    print("=" * 80)
    print("Searching for dt/dd structures...")
    print("=" * 80)

    for dt in soup.find_all("dt"):
        text = dt.get_text().strip()
        if "applicant" in text.lower() or "agent" in text.lower():
            dd = dt.find_next_sibling("dd")
            print(f"Found: {text}")
            if dd:
                print(f"  Value: {dd.get_text().strip()[:100]}")
            print()

    # Save a sample of HTML for inspection
    with open("/tmp/dover_html_sample.html", "w") as f:
        f.write(html)

    print("Full HTML saved to: /tmp/dover_html_sample.html")


if __name__ == "__main__":
    asyncio.run(debug())
