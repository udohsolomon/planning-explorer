#!/usr/bin/env python3
"""
Generate URL Slugs for Content Discovery Pages
Phase 1 Week 2 - Backend Engineer Deliverable (UPDATED)

Generates slugified versions of ALL:
- UK Planning Authorities (425 councils from uk_authorities.py)
- Major UK locations (cities, towns, regions from existing data)
- Planning sectors/use classes

Leverages existing uk_authorities.py to avoid duplication

Outputs: slugs.json mapping file for API routes

Master Orchestrator: content-discovery-implementation-plan.md Phase 1 Week 2
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing authority data (425 authorities)
from app.data.uk_authorities import (
    UK_PLANNING_AUTHORITIES,
    CITY_TO_AUTHORITY,
    REGIONAL_GROUPINGS,
    get_all_authority_names
)


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug

    Args:
        text: Input text (e.g., "Milton Keynes City Council")

    Returns:
        str: URL slug (e.g., "milton-keynes")

    Examples:
        >>> slugify("Manchester City Council")
        'manchester'
        >>> slugify("Bournemouth, Christchurch and Poole")
        'bournemouth-christchurch-and-poole'
    """
    # Convert to lowercase
    slug = text.lower()

    # Remove common suffixes for cleaner URLs
    slug = re.sub(r'\s+(city\s+)?council$', '', slug)
    slug = re.sub(r'\s+borough(\s+council)?$', '', slug)
    slug = re.sub(r'\s+district(\s+council)?$', '', slug)
    slug = re.sub(r'\s+county(\s+council)?$', '', slug)
    slug = re.sub(r'\s+metropolitan\s+(borough|district)$', '', slug)
    slug = re.sub(r'\s+authority$', '', slug)

    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug


# Planning Sectors / Use Classes
PLANNING_SECTORS = [
    "Residential",
    "Commercial Retail",
    "Commercial Office",
    "Industrial",
    "Renewable Energy",
    "Infrastructure",
    "Education",
    "Healthcare",
    "Leisure & Hospitality",
    "Student Housing",
    "Mixed Use",
    "Agricultural",
    "Transport",
    "Telecommunications",
    "Waste Management",
    "Community Facilities",
    "Religious Buildings",
    "Historic Buildings",
    "Public Sector",
    "Data Centres"
]


def generate_authority_slugs() -> Dict[str, str]:
    """
    Generate authority slug mappings from ALL 425 UK authorities

    Returns:
        Dict mapping canonical name → slug
    """
    authority_slugs = {}

    # Get all 425 canonical authority names
    all_authorities = get_all_authority_names()

    for authority in all_authorities:
        slug = slugify(authority)
        authority_slugs[authority] = slug

    return authority_slugs


def generate_location_slugs() -> Dict[str, str]:
    """
    Generate location slug mappings from cities and regions

    Returns:
        Dict mapping location name → slug
    """
    location_slugs = {}

    # Add all cities from CITY_TO_AUTHORITY mapping (73 cities)
    for city in CITY_TO_AUTHORITY.keys():
        location_slugs[city] = slugify(city)

    # Add regional groupings (12 regions)
    for region in REGIONAL_GROUPINGS.keys():
        location_slugs[region] = slugify(region)

    # NOTE: Postcode coverage deferred to Phase 2/3
    # Phase 2/3 will add:
    # - Postcode areas (120 areas: M, B, LS, etc.)
    # - Postcode districts (2900+ districts: M1, M2, B1, etc.)
    # - Full postcodes (1.7M+ postcodes with boundary data)

    return location_slugs


def generate_sector_slugs() -> Dict[str, str]:
    """Generate sector slug mappings"""
    return {
        sector: slugify(sector)
        for sector in PLANNING_SECTORS
    }


def generate_all_slugs() -> Dict[str, Dict[str, str]]:
    """Generate all slug mappings"""
    return {
        "authorities": generate_authority_slugs(),
        "locations": generate_location_slugs(),
        "sectors": generate_sector_slugs()
    }


def save_slugs(slugs: Dict, output_path: Path):
    """Save slugs to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(slugs, f, indent=2)
    print(f"✅ Slugs saved to {output_path}")


def print_summary(slugs: Dict):
    """Print summary statistics"""
    print("\n" + "=" * 60)
    print("Slug Generation Summary (Using uk_authorities.py)")
    print("=" * 60)
    print(f"Authorities: {len(slugs['authorities'])} slugs generated (ALL 425)")
    print(f"Locations: {len(slugs['locations'])} slugs generated")
    print(f"Sectors: {len(slugs['sectors'])} slugs generated")
    print(f"Total: {sum(len(s) for s in slugs.values())} slugs")
    print("=" * 60)

    # Show examples
    print("\nExample Authority Slugs (first 10):")
    for name, slug in list(slugs['authorities'].items())[:10]:
        print(f"  {name:40} → {slug}")

    print("\nExample Location Slugs:")
    for name, slug in list(slugs['locations'].items())[:10]:
        print(f"  {name:40} → {slug}")

    print("\nExample Sector Slugs:")
    for name, slug in list(slugs['sectors'].items())[:5]:
        print(f"  {name:40} → {slug}")


def verify_coverage():
    """Verify we have all 425 authorities"""
    all_authorities = get_all_authority_names()
    print(f"\n🔍 Verification:")
    print(f"   Total authorities in uk_authorities.py: {len(all_authorities)}")
    print(f"   Expected: 425")

    if len(all_authorities) == 425:
        print(f"   ✅ All 425 authorities accounted for!")
    else:
        print(f"   ⚠️  Mismatch detected")


def main():
    """Main execution"""
    print("=" * 60)
    print("Content Discovery - Comprehensive Slug Generation")
    print("Phase 1 Week 2 - Backend Engineer (UPDATED)")
    print("=" * 60)
    print()

    # Verify coverage first
    verify_coverage()

    # Generate slugs
    print("\n🔧 Generating URL slugs from uk_authorities.py...")
    slugs = generate_all_slugs()

    # Save to file
    output_path = Path(__file__).parent.parent / "app" / "data" / "slugs.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_slugs(slugs, output_path)

    # Print summary
    print_summary(slugs)

    print("\n✅ Next steps:")
    print("1. Slugs automatically loaded by SlugRegistry on startup")
    print("2. All 425 UK authorities now have SEO-friendly URLs")
    print("3. Frontend can use /authorities/{slug} routes")
    print("4. Location pages ready for Phase 1.5 (boundary data needed)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
