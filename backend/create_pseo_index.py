"""
Create pseo_pages Elasticsearch index with proper mapping
Handles all field types from pSEO page generation
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

# ES connection
es = Elasticsearch(
    [os.getenv('ELASTICSEARCH_NODE')],
    basic_auth=(os.getenv('ELASTICSEARCH_USERNAME'), os.getenv('ELASTICSEARCH_PASSWORD')),
    verify_certs=False
)

# Define comprehensive mapping for pseo_pages
mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            # Core identifiers
            "authority_id": {"type": "keyword"},
            "authority_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "url_slug": {"type": "keyword"},
            "generated_at": {"type": "date"},

            # SEO metadata
            "seo": {
                "properties": {
                    "meta_tags": {
                        "properties": {
                            "title": {"type": "text"},
                            "description": {"type": "text"},
                            "canonical": {"type": "keyword"},
                            "keywords": {"type": "keyword"}
                        }
                    },
                    "og_tags": {"type": "object", "enabled": False},
                    "structured_data": {"type": "object", "enabled": False},
                    "internal_links": {"type": "object", "enabled": False}
                }
            },

            # Page sections - store as objects (not indexed, just stored)
            "sections": {
                "type": "object",
                "enabled": False  # Don't index nested content, just store
            },

            # Raw data - flexible schema, don't enforce mapping
            "raw_data": {
                "type": "object",
                "dynamic": True,  # Allow any structure
                "properties": {
                    "core_metrics": {
                        "properties": {
                            "total_applications_ytd": {"type": "long"},
                            "approval_rate": {"type": "float"},
                            "avg_decision_time": {"type": "float"},
                            "pending_applications": {"type": "long"},
                            "by_type": {"type": "object", "enabled": False}
                        }
                    },
                    "trends": {
                        "properties": {
                            "monthly": {"type": "object", "enabled": False}
                        }
                    },
                    "charts": {"type": "object", "enabled": False},
                    "top_entities": {"type": "object", "enabled": False},
                    "geographic": {"type": "object", "enabled": False},
                    "notable_applications": {"type": "object", "enabled": False},
                    "comparative": {"type": "object", "enabled": False}
                }
            },

            # Metadata
            "metadata": {
                "properties": {
                    "total_words": {"type": "long"},
                    "total_sections": {"type": "integer"},
                    "total_visualizations": {"type": "integer"},
                    "scraper_used": {"type": "keyword"},
                    "generation_cost": {"type": "float"},
                    "meets_word_count": {"type": "boolean"}
                }
            }
        }
    }
}

# Create index
index_name = 'pseo_pages'
print(f"Creating index '{index_name}' with proper mapping...")

try:
    es.indices.create(index=index_name, body=mapping)
    print(f"✅ Successfully created index '{index_name}'")

    # Verify
    index_info = es.indices.get(index=index_name)
    print(f"\n📊 Index configuration:")
    print(f"   Shards: {index_info[index_name]['settings']['index']['number_of_shards']}")
    print(f"   Replicas: {index_info[index_name]['settings']['index']['number_of_replicas']}")
    print(f"   Mappings: {len(index_info[index_name]['mappings']['properties'])} top-level fields")

except Exception as e:
    print(f"❌ Error creating index: {e}")

es.close()
