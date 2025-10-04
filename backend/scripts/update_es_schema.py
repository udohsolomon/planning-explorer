#!/usr/bin/env python3
"""
Script to update Elasticsearch schema with vector embedding fields
for Planning Explorer semantic search capabilities.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import requests
from requests.auth import HTTPBasicAuth

ES_NODE = "https://95.217.117.251:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "d41=*sDuOnhQqXonYz2U"
INDEX_NAME = "planning_applications"

def update_mapping():
    """Update Elasticsearch mapping to include vector fields"""

    # Enhanced mapping with vector fields for semantic search
    mapping_update = {
        "properties": {
            # Vector embedding fields for semantic search
            "description_embedding": {
                "type": "dense_vector",
                "dims": 1536,  # OpenAI text-embedding-3-large dimensions
                "index": True,
                "similarity": "cosine"
            },
            "summary_embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine"
            },
            "embedding_vector": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine"
            },

            # AI processing status fields
            "ai_processed": {
                "type": "boolean"
            },
            "ai_processed_at": {
                "type": "date"
            },
            "ai_processing_version": {
                "type": "keyword"
            },

            # Opportunity scoring fields
            "opportunity_score": {
                "type": "integer"
            },
            "approval_probability": {
                "type": "float"
            },
            "ai_confidence_score": {
                "type": "float"
            },
            "ai_rationale": {
                "type": "text",
                "analyzer": "english"
            },
            "ai_risk_factors": {
                "type": "keyword"
            },
            "ai_recommendations": {
                "type": "keyword"
            },

            # AI summarization fields
            "ai_summary": {
                "type": "text",
                "analyzer": "english"
            },
            "ai_key_points": {
                "type": "keyword"
            },
            "ai_sentiment": {
                "type": "keyword"
            },
            "complexity_score": {
                "type": "float"
            },

            # Embedding metadata
            "embedding_model": {
                "type": "keyword"
            },
            "embedding_dimensions": {
                "type": "integer"
            },

            # Market context for AI insights
            "market_context": {
                "type": "object",
                "properties": {
                    "development_type_trends": {
                        "type": "keyword"
                    },
                    "authority_performance": {
                        "type": "object"
                    },
                    "comparable_applications": {
                        "type": "keyword"
                    }
                }
            }
        }
    }

    try:
        print(f"Updating mapping for index: {INDEX_NAME}")

        # Update mapping
        response = requests.put(
            f"{ES_NODE}/{INDEX_NAME}/_mapping",
            json=mapping_update,
            auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            print("✅ Mapping updated successfully")
            return True
        else:
            print(f"❌ Failed to update mapping: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error updating mapping: {str(e)}")
        return False

def verify_mapping():
    """Verify the mapping was updated correctly"""
    try:
        print("\nVerifying mapping update...")

        response = requests.get(
            f"{ES_NODE}/{INDEX_NAME}/_mapping",
            auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            mapping = response.json()
            properties = mapping[INDEX_NAME]["mappings"]["properties"]

            # Check for vector fields
            vector_fields = ["description_embedding", "summary_embedding", "embedding_vector"]
            missing_fields = []

            for field in vector_fields:
                if field in properties:
                    field_config = properties[field]
                    if field_config.get("type") == "dense_vector":
                        print(f"✅ {field}: {field_config}")
                    else:
                        print(f"⚠️ {field}: exists but wrong type - {field_config}")
                        missing_fields.append(field)
                else:
                    print(f"❌ {field}: missing")
                    missing_fields.append(field)

            # Check AI fields
            ai_fields = ["ai_processed", "opportunity_score", "ai_summary"]
            for field in ai_fields:
                if field in properties:
                    print(f"✅ {field}: {properties[field]}")
                else:
                    print(f"❌ {field}: missing")

            if not missing_fields:
                print("\n🎉 All vector fields configured correctly!")
                return True
            else:
                print(f"\n⚠️ Missing or incorrect fields: {missing_fields}")
                return False

        else:
            print(f"❌ Failed to retrieve mapping: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error verifying mapping: {str(e)}")
        return False

def test_vector_search():
    """Test vector search capability with a dummy vector"""
    try:
        print("\nTesting vector search capability...")

        # Create a dummy vector (1536 dimensions filled with 0.1)
        dummy_vector = [0.1] * 1536

        # Test vector search query
        search_query = {
            "knn": {
                "field": "description_embedding",
                "query_vector": dummy_vector,
                "k": 1,
                "num_candidates": 10
            },
            "size": 1
        }

        response = requests.post(
            f"{ES_NODE}/{INDEX_NAME}/_search",
            json=search_query,
            auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            result = response.json()
            hits = result.get("hits", {}).get("hits", [])
            print(f"✅ Vector search query executed successfully")
            print(f"   Found {len(hits)} results (expected 0 since no vectors exist yet)")
            return True
        else:
            print(f"❌ Vector search failed: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error testing vector search: {str(e)}")
        return False

def main():
    """Main function"""
    print("=== Elasticsearch Schema Update for Vector Search ===\n")

    # Step 1: Update mapping
    if not update_mapping():
        print("\n❌ Schema update failed")
        return 1

    # Step 2: Verify mapping
    if not verify_mapping():
        print("\n⚠️ Schema verification had issues")

    # Step 3: Test vector search capability
    if not test_vector_search():
        print("\n⚠️ Vector search test failed")

    print("\n=== Schema Update Complete ===")
    print("\nNext steps:")
    print("1. Run data migration to populate vector embeddings")
    print("2. Fix search service to use correct field names")
    print("3. Test semantic search functionality")

    return 0

if __name__ == "__main__":
    sys.exit(main())