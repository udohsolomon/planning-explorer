#!/usr/bin/env python3
"""
Add Content Discovery Fields to Elasticsearch Schema
Phase 1 - Elasticsearch Architect Deliverable

Adds slug fields and metadata needed for content discovery pages:
- Authority pages
- Location pages
- Sector pages

Master Orchestrator: content-discovery-implementation-plan.md Phase 1 Week 1
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from requests.auth import HTTPBasicAuth
import json

ES_NODE = "https://95.217.117.251:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "d41=*sDuOnhQqXonYz2U"
INDEX_NAME = "planning_applications"


def add_content_discovery_fields():
    """Add content discovery fields to ES mapping"""

    # Only add fields that don't exist yet
    mapping_update = {
        "properties": {
            # Slug fields for SEO URLs (without normalizer since they might exist)
            "location_slug": {
                "type": "keyword"
            },
            "sector_slug": {
                "type": "keyword"
            },

            # Decision tracking
            "is_approved": {
                "type": "boolean"
            },

            # Agent/Consultant tracking (Phase 2)
            "agent_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "consultant_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },

            # Project value estimation
            "project_value_estimate": {
                "type": "float"
            },

            # Location boundary (for geo_shape queries)
            "location_boundary": {
                "type": "geo_shape"
            },

            # Content discovery metadata
            "last_indexed_for_discovery": {
                "type": "date"
            },
            "discovery_page_views": {
                "type": "long"
            }
        }
    }

    try:
        print(f"🔧 Adding content discovery fields to {INDEX_NAME}...")

        response = requests.put(
            f"{ES_NODE}/{INDEX_NAME}/_mapping",
            json=mapping_update,
            auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            print("✅ Content discovery fields added successfully")
            print("\nAdded fields:")
            for field in mapping_update["properties"].keys():
                print(f"  - {field}")
            return True
        else:
            print(f"❌ Failed to update mapping: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def verify_fields():
    """Verify the new fields are in the mapping"""
    try:
        print("\n🔍 Verifying field additions...")

        response = requests.get(
            f"{ES_NODE}/{INDEX_NAME}/_mapping",
            auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            mapping = response.json()
            properties = mapping[INDEX_NAME]["mappings"]["properties"]

            required_fields = [
                "authority_slug",
                "location_slug",
                "sector_slug",
                "decision_days",
                "is_approved"
            ]

            all_present = True
            for field in required_fields:
                if field in properties:
                    print(f"✅ {field}: {properties[field].get('type')}")
                else:
                    print(f"❌ {field}: MISSING")
                    all_present = False

            if all_present:
                print("\n🎉 All content discovery fields configured!")
                return True
            else:
                print("\n⚠️  Some fields are missing")
                return False
        else:
            print(f"❌ Failed to verify: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False


def main():
    """Main execution"""
    print("=" * 60)
    print("Content Discovery Fields - Schema Enhancement")
    print("Phase 1 Week 1 - Elasticsearch Architect")
    print("=" * 60)
    print()

    # Add fields
    if not add_content_discovery_fields():
        print("\n❌ Schema enhancement failed")
        return 1

    # Verify
    if not verify_fields():
        print("\n⚠️  Verification incomplete")

    print("\n" + "=" * 60)
    print("✅ Schema Enhancement Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run slug generation script")
    print("2. Create ingest pipeline for decision_days calculation")
    print("3. Backfill existing documents with slugs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
