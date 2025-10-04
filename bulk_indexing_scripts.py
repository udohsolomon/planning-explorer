#!/usr/bin/env python3
"""
Elasticsearch Bulk Indexing Scripts for Planning Explorer
Optimized for single-node deployment with vector embeddings
"""

import json
import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import ElasticsearchException
import openai
import numpy as np
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IndexingConfig:
    """Configuration for bulk indexing operations"""
    es_host: str = "http://localhost:9200"
    index_name: str = "planning_applications"
    bulk_size: int = 1000
    max_workers: int = 4
    timeout: int = 60
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 1536

class PlanningApplicationProcessor:
    """Process and index planning applications with AI enhancements"""

    def __init__(self, config: IndexingConfig):
        self.config = config
        self.es_client = None
        self.openai_client = openai.AsyncOpenAI()

    async def initialize(self):
        """Initialize Elasticsearch connection"""
        self.es_client = AsyncElasticsearch(
            [self.config.es_host],
            timeout=self.config.timeout,
            max_retries=3,
            retry_on_timeout=True
        )

        # Test connection
        try:
            await self.es_client.ping()
            logger.info("Connected to Elasticsearch successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise

    async def create_index(self, force_recreate: bool = False):
        """Create the planning applications index with optimized settings"""

        if force_recreate:
            try:
                await self.es_client.indices.delete(index=self.config.index_name)
                logger.info(f"Deleted existing index: {self.config.index_name}")
            except:
                pass

        # Load schema from file
        try:
            with open('elasticsearch_schema.json', 'r') as f:
                schema = json.load(f)
        except FileNotFoundError:
            logger.error("elasticsearch_schema.json not found")
            raise

        try:
            await self.es_client.indices.create(
                index=self.config.index_name,
                body=schema
            )
            logger.info(f"Created index: {self.config.index_name}")
        except ElasticsearchException as e:
            if "already_exists" in str(e):
                logger.info(f"Index {self.config.index_name} already exists")
            else:
                logger.error(f"Failed to create index: {e}")
                raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.config.embedding_model,
                input=texts,
                encoding_format="float"
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return [[0.0] * self.config.embedding_dimensions] * len(texts)

    def prepare_text_for_embedding(self, application: Dict[str, Any]) -> Dict[str, str]:
        """Prepare different text fields for embedding generation"""

        # Description embedding
        description = application.get('description', '')

        # Full content embedding (concatenate multiple fields)
        full_content_parts = [
            application.get('description', ''),
            application.get('proposal', ''),
            application.get('ai_summary', ''),
            application.get('address', ''),
            str(application.get('development_type', '')),
            str(application.get('use_class', ''))
        ]
        full_content = ' '.join(filter(None, full_content_parts))

        # Summary embedding
        summary = application.get('ai_summary', '') or description[:500]

        # Location context for geographic embedding
        location_parts = [
            application.get('postcode', ''),
            application.get('ward', ''),
            application.get('authority', ''),
            application.get('address', '')
        ]
        location_context = ' '.join(filter(None, location_parts))

        return {
            'description': description[:8000],  # Truncate to avoid token limits
            'full_content': full_content[:8000],
            'summary': summary[:8000],
            'location': location_context[:2000]
        }

    async def process_applications_batch(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of applications with AI enhancements"""

        # Prepare texts for embedding
        embedding_texts = {
            'descriptions': [],
            'full_contents': [],
            'summaries': [],
            'locations': []
        }

        for app in applications:
            texts = self.prepare_text_for_embedding(app)
            embedding_texts['descriptions'].append(texts['description'])
            embedding_texts['full_contents'].append(texts['full_content'])
            embedding_texts['summaries'].append(texts['summary'])
            embedding_texts['locations'].append(texts['location'])

        # Generate embeddings in batches
        try:
            desc_embeddings = await self.generate_embeddings(embedding_texts['descriptions'])
            content_embeddings = await self.generate_embeddings(embedding_texts['full_contents'])
            summary_embeddings = await self.generate_embeddings(embedding_texts['summaries'])
            # Note: Location embeddings would use a different model optimized for geographic data

            # Add embeddings to applications
            processed_applications = []
            current_time = datetime.now(timezone.utc).isoformat()

            for i, app in enumerate(applications):
                processed_app = app.copy()

                # Add vector embeddings
                processed_app['description_embedding'] = desc_embeddings[i]
                processed_app['full_content_embedding'] = content_embeddings[i]
                processed_app['summary_embedding'] = summary_embeddings[i]

                # Add processing metadata
                processed_app['ai_processing'] = {
                    'last_processed': current_time,
                    'model_version': 'gpt-4-turbo',
                    'processing_status': 'completed',
                    'human_reviewed': False,
                    'embedding_model': self.config.embedding_model,
                    'processing_duration': 0.0  # Would be calculated in real implementation
                }

                # Add timestamps
                processed_app['indexed_at'] = current_time
                if 'created_at' not in processed_app:
                    processed_app['created_at'] = current_time
                if 'updated_at' not in processed_app:
                    processed_app['updated_at'] = current_time

                processed_applications.append(processed_app)

            return processed_applications

        except Exception as e:
            logger.error(f"Failed to process applications batch: {e}")
            return applications  # Return original applications if processing fails

    def prepare_bulk_actions(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare bulk actions for Elasticsearch"""
        actions = []

        for app in applications:
            action = {
                "_index": self.config.index_name,
                "_id": app["application_id"],
                "_source": app
            }
            actions.append(action)

        return actions

    async def bulk_index_applications(self, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index applications with optimizations"""

        start_time = time.time()
        total_apps = len(applications)

        logger.info(f"Starting bulk indexing of {total_apps} applications")

        # Temporarily adjust index settings for bulk operations
        await self.optimize_for_bulk_indexing(True)

        try:
            # Process applications in batches
            success_count = 0
            error_count = 0

            for i in range(0, total_apps, self.config.bulk_size):
                batch = applications[i:i + self.config.bulk_size]
                batch_start = time.time()

                # Process batch with AI enhancements
                processed_batch = await self.process_applications_batch(batch)

                # Prepare bulk actions
                actions = self.prepare_bulk_actions(processed_batch)

                # Execute bulk indexing
                try:
                    response = await helpers.async_bulk(
                        self.es_client,
                        actions,
                        chunk_size=self.config.bulk_size,
                        max_chunk_bytes=10 * 1024 * 1024,  # 10MB chunks
                        timeout=f"{self.config.timeout}s"
                    )

                    batch_success, batch_errors = response
                    success_count += batch_success
                    error_count += len(batch_errors) if batch_errors else 0

                    batch_time = time.time() - batch_start
                    rate = len(batch) / batch_time

                    logger.info(f"Batch {i//self.config.bulk_size + 1}: "
                               f"{len(batch)} docs in {batch_time:.2f}s "
                               f"({rate:.1f} docs/sec)")

                    if batch_errors:
                        logger.warning(f"Batch had {len(batch_errors)} errors")

                except Exception as e:
                    logger.error(f"Bulk indexing batch failed: {e}")
                    error_count += len(batch)

            # Restore normal index settings
            await self.optimize_for_bulk_indexing(False)

            total_time = time.time() - start_time
            overall_rate = total_apps / total_time if total_time > 0 else 0

            result = {
                'total_applications': total_apps,
                'successful': success_count,
                'errors': error_count,
                'total_time_seconds': total_time,
                'rate_docs_per_second': overall_rate
            }

            logger.info(f"Bulk indexing completed: {result}")
            return result

        except Exception as e:
            await self.optimize_for_bulk_indexing(False)  # Restore settings
            logger.error(f"Bulk indexing failed: {e}")
            raise

    async def optimize_for_bulk_indexing(self, enable: bool):
        """Optimize index settings for bulk operations"""

        if enable:
            settings = {
                "index": {
                    "refresh_interval": "30s",
                    "number_of_replicas": 0,
                    "translog.durability": "async",
                    "translog.sync_interval": "30s"
                }
            }
        else:
            settings = {
                "index": {
                    "refresh_interval": "5s",
                    "number_of_replicas": 0,  # Keep 0 for single node
                    "translog.durability": "request",
                    "translog.sync_interval": "5s"
                }
            }

        try:
            await self.es_client.indices.put_settings(
                index=self.config.index_name,
                body=settings
            )
            logger.info(f"Updated index settings for bulk indexing: {enable}")
        except Exception as e:
            logger.warning(f"Failed to update index settings: {e}")

    async def warm_index(self):
        """Warm the index with common queries"""
        warming_queries = [
            # Basic search
            {"query": {"match_all": {}}},

            # Vector similarity query
            {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "1.0"  # Simplified for warming
                        }
                    }
                }
            },

            # Common aggregations
            {
                "aggs": {
                    "authorities": {
                        "terms": {"field": "authority", "size": 10}
                    }
                },
                "size": 0
            }
        ]

        logger.info("Warming index with common query patterns")

        for query in warming_queries:
            try:
                await self.es_client.search(
                    index=self.config.index_name,
                    body=query,
                    size=0
                )
            except Exception as e:
                logger.warning(f"Warning query failed: {e}")

        logger.info("Index warming completed")

    async def close(self):
        """Close the Elasticsearch connection"""
        if self.es_client:
            await self.es_client.close()

# Utility functions for data loading

def load_sample_data() -> List[Dict[str, Any]]:
    """Load sample data from template file"""
    try:
        with open('sample_data_template.json', 'r') as f:
            data = json.load(f)

        # Extract sample applications
        samples = [
            data['sample_planning_application'],
            data['sample_commercial_application'],
            data['sample_major_development']
        ]

        return samples
    except FileNotFoundError:
        logger.error("sample_data_template.json not found")
        return []

def generate_test_data(count: int = 100) -> List[Dict[str, Any]]:
    """Generate test data for bulk indexing"""
    import random
    from datetime import timedelta

    authorities = ["Camden Council", "Westminster City Council", "Southwark Council",
                  "Tower Hamlets Council", "Islington Council"]
    dev_types = ["Residential", "Commercial", "Mixed Use", "Industrial", "Retail"]
    statuses = ["Under Consideration", "Approved", "Refused", "Withdrawn"]

    base_date = datetime.now() - timedelta(days=365)

    applications = []
    for i in range(count):
        app_id = f"APP/2024/{i+1:04d}"

        app = {
            "application_id": app_id,
            "reference": f"24/{i+1:05d}/FUL",
            "authority": random.choice(authorities),
            "address": f"{random.randint(1, 999)} Test Street, London",
            "postcode": f"N{random.randint(1, 22)} {random.randint(1, 9)}AA",
            "location": {
                "lat": 51.5074 + random.uniform(-0.1, 0.1),
                "lon": -0.1278 + random.uniform(-0.1, 0.1)
            },
            "status": random.choice(statuses),
            "submission_date": (base_date + timedelta(days=random.randint(0, 365))).isoformat(),
            "development_type": random.choice(dev_types),
            "description": f"Test planning application {i+1} for {random.choice(dev_types).lower()} development",
            "project_value": random.randint(50000, 5000000),
            "opportunity_score": random.randint(20, 95),
            "ai_summary": f"AI-generated summary for application {app_id}",
            "approval_probability": random.uniform(0.3, 0.9),
            "applicant": {
                "name": f"Test Applicant {i+1}",
                "type": "Individual"
            }
        }
        applications.append(app)

    return applications

# Main execution functions

async def setup_index():
    """Set up the Elasticsearch index"""
    config = IndexingConfig()
    processor = PlanningApplicationProcessor(config)

    try:
        await processor.initialize()
        await processor.create_index(force_recreate=True)
        logger.info("Index setup completed successfully")
    except Exception as e:
        logger.error(f"Index setup failed: {e}")
        raise
    finally:
        await processor.close()

async def bulk_index_sample_data():
    """Index sample data"""
    config = IndexingConfig()
    processor = PlanningApplicationProcessor(config)

    try:
        await processor.initialize()

        # Load sample data
        applications = load_sample_data()
        if not applications:
            logger.warning("No sample data found, generating test data")
            applications = generate_test_data(50)

        # Bulk index
        result = await processor.bulk_index_applications(applications)

        # Warm index
        await processor.warm_index()

        return result

    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")
        raise
    finally:
        await processor.close()

async def bulk_index_test_data(count: int = 1000):
    """Index test data for performance testing"""
    config = IndexingConfig()
    processor = PlanningApplicationProcessor(config)

    try:
        await processor.initialize()

        # Generate test data
        applications = generate_test_data(count)

        # Bulk index
        result = await processor.bulk_index_applications(applications)

        return result

    except Exception as e:
        logger.error(f"Test data indexing failed: {e}")
        raise
    finally:
        await processor.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Planning Explorer Bulk Indexing")
    parser.add_argument("--setup", action="store_true", help="Set up the index")
    parser.add_argument("--sample", action="store_true", help="Index sample data")
    parser.add_argument("--test", type=int, help="Index test data (specify count)")

    args = parser.parse_args()

    if args.setup:
        asyncio.run(setup_index())
    elif args.sample:
        asyncio.run(bulk_index_sample_data())
    elif args.test:
        asyncio.run(bulk_index_test_data(args.test))
    else:
        print("Usage: python bulk_indexing_scripts.py [--setup|--sample|--test COUNT]")