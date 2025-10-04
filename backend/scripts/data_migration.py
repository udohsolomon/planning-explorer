#!/usr/bin/env python3
"""
Data Migration Script for AI Enhancement Fields

This script migrates existing planning application data to include new AI
enhancement fields and populates them with AI-generated content.
"""

import asyncio
import logging
import argparse
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.elasticsearch import es_client
from app.services.ai_processor import ai_processor, ProcessingMode
from app.models.planning import PlanningApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """
    Data migration coordinator for adding AI enhancement fields
    to existing planning applications.
    """

    def __init__(self):
        self.migration_stats = {
            "total_applications": 0,
            "migrated_count": 0,
            "skipped_count": 0,
            "error_count": 0,
            "start_time": None,
            "end_time": None
        }

    async def run_migration(
        self,
        dry_run: bool = False,
        batch_size: int = 100,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete data migration for AI enhancement fields.

        Args:
            dry_run: If True, don't actually update data
            batch_size: Number of applications to process in each batch
            force_update: If True, update even applications that already have AI data

        Returns:
            Migration statistics
        """
        logger.info(f"Starting data migration (dry_run={dry_run}, force_update={force_update})")
        self.migration_stats["start_time"] = datetime.utcnow()

        try:
            # Step 1: Update Elasticsearch mapping
            if not dry_run:
                await self._update_elasticsearch_mapping()

            # Step 2: Get applications needing migration
            applications = await self._get_applications_for_migration(force_update)
            self.migration_stats["total_applications"] = len(applications)

            logger.info(f"Found {len(applications)} applications for migration")

            if not applications:
                logger.info("No applications need migration")
                return self.migration_stats

            # Step 3: Process applications in batches
            await self._migrate_applications_in_batches(
                applications, batch_size, dry_run
            )

            self.migration_stats["end_time"] = datetime.utcnow()

            # Step 4: Verify migration
            if not dry_run:
                await self._verify_migration()

            logger.info("Data migration completed successfully")
            return self.migration_stats

        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.migration_stats["error"] = str(e)
            return self.migration_stats

    async def _update_elasticsearch_mapping(self) -> None:
        """Update Elasticsearch mapping to include AI enhancement fields"""
        logger.info("Updating Elasticsearch mapping for AI fields")

        ai_field_mapping = {
            "properties": {
                # AI Processing Status
                "ai_processed": {
                    "type": "boolean"
                },
                "ai_processed_at": {
                    "type": "date"
                },
                "ai_processing_version": {
                    "type": "keyword"
                },

                # Opportunity Scoring
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

                # Summarization
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

                # Embeddings
                "embedding_vector": {
                    "type": "dense_vector",
                    "dims": 1536,  # OpenAI text-embedding-3-large dimensions
                    "index": True,
                    "similarity": "cosine"
                },
                "embedding_model": {
                    "type": "keyword"
                },
                "embedding_dimensions": {
                    "type": "integer"
                },

                # Market Context
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
            # Update mapping for planning_applications index
            await es_client.indices.put_mapping(
                index="planning_applications",
                body=ai_field_mapping
            )
            logger.info("Elasticsearch mapping updated successfully")

        except Exception as e:
            logger.error(f"Error updating Elasticsearch mapping: {str(e)}")
            raise

    async def _get_applications_for_migration(self, force_update: bool) -> List[PlanningApplication]:
        """Get applications that need migration"""
        logger.info("Fetching applications for migration")

        query = {
            "query": {
                "bool": {
                    "must": [{"match_all": {}}]
                }
            },
            "size": 10000,
            "_source": True
        }

        # If not forcing update, only get applications without AI data
        if not force_update:
            query["query"]["bool"]["must_not"] = [
                {"exists": {"field": "ai_processed"}}
            ]

        applications = []

        try:
            # Use scroll for large datasets
            response = await es_client.search(
                index="planning_applications",
                body=query,
                scroll="5m"
            )

            scroll_id = response.get("_scroll_id")
            hits = response["hits"]["hits"]

            while hits:
                for hit in hits:
                    try:
                        app_data = hit["_source"]
                        app = PlanningApplication(**app_data)
                        applications.append(app)
                    except Exception as e:
                        logger.warning(f"Error parsing application {hit.get('_id', 'unknown')}: {e}")

                # Get next batch
                if scroll_id:
                    response = await es_client.scroll(
                        scroll_id=scroll_id,
                        scroll="5m"
                    )
                    hits = response["hits"]["hits"]
                else:
                    break

            # Clean up scroll
            if scroll_id:
                try:
                    await es_client.clear_scroll(scroll_id=scroll_id)
                except:
                    pass

            return applications

        except Exception as e:
            logger.error(f"Error fetching applications: {str(e)}")
            return []

    async def _migrate_applications_in_batches(
        self,
        applications: List[PlanningApplication],
        batch_size: int,
        dry_run: bool
    ) -> None:
        """Migrate applications in batches"""
        total_batches = (len(applications) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(applications))
            batch = applications[start_idx:end_idx]

            logger.info(f"Migrating batch {batch_num + 1}/{total_batches} ({len(batch)} applications)")

            try:
                # Process batch with AI
                if not dry_run:
                    batch_results = await ai_processor.process_batch(
                        batch,
                        ProcessingMode.STANDARD,
                        ["opportunity_scoring", "summarization", "embeddings"],
                        max_concurrent=5  # Conservative for migration
                    )

                    # Update Elasticsearch with AI results
                    await self._update_applications_with_ai_data(batch_results)

                    self.migration_stats["migrated_count"] += batch_results.successful_count
                    self.migration_stats["error_count"] += batch_results.failed_count
                else:
                    # Dry run - just count
                    self.migration_stats["migrated_count"] += len(batch)

                # Log progress
                progress = (batch_num + 1) / total_batches * 100
                logger.info(f"Migration progress: {progress:.1f}% "
                           f"({self.migration_stats['migrated_count']} completed)")

            except Exception as e:
                logger.error(f"Error migrating batch {batch_num + 1}: {str(e)}")
                self.migration_stats["error_count"] += len(batch)

    async def _update_applications_with_ai_data(self, batch_results) -> None:
        """Update applications in Elasticsearch with AI data"""
        bulk_operations = []

        for result in batch_results.results:
            if result.success:
                # Prepare update document
                update_doc = {
                    "ai_processed": True,
                    "ai_processed_at": result.generated_at.isoformat(),
                    "ai_processing_version": "2.0.0"
                }

                # Add opportunity scoring results
                if "opportunity_scoring" in result.results:
                    scoring = result.results["opportunity_scoring"]
                    update_doc.update({
                        "opportunity_score": scoring["opportunity_score"],
                        "approval_probability": scoring["approval_probability"],
                        "ai_confidence_score": scoring["confidence_score"],
                        "ai_rationale": scoring["rationale"],
                        "ai_risk_factors": scoring["risk_factors"],
                        "ai_recommendations": scoring["recommendations"]
                    })

                # Add summarization results
                if "summarization" in result.results:
                    summary = result.results["summarization"]
                    update_doc.update({
                        "ai_summary": summary["summary"],
                        "ai_key_points": summary["key_points"],
                        "ai_sentiment": summary["sentiment"],
                        "complexity_score": summary["complexity_score"]
                    })

                # Add embedding results
                if "embeddings" in result.results:
                    embedding = result.results["embeddings"]
                    update_doc.update({
                        "embedding_vector": embedding.get("_vector"),
                        "embedding_model": embedding["model_used"],
                        "embedding_dimensions": embedding["dimensions"]
                    })

                # Add market context if available
                if "market_context" in result.results:
                    update_doc["market_context"] = result.results["market_context"]

                # Prepare bulk operation
                bulk_operations.extend([
                    {"update": {"_index": "planning_applications", "_id": result.application_id}},
                    {"doc": update_doc, "doc_as_upsert": False}
                ])

        # Execute bulk update
        if bulk_operations:
            try:
                response = await es_client.bulk(body=bulk_operations)

                if response.get("errors"):
                    error_count = len([
                        item for item in response["items"]
                        if "update" in item and "error" in item["update"]
                    ])
                    logger.warning(f"Bulk update had {error_count} errors")

            except Exception as e:
                logger.error(f"Error in bulk update: {str(e)}")
                raise

    async def _verify_migration(self) -> None:
        """Verify migration completed successfully"""
        logger.info("Verifying migration results")

        try:
            # Count applications with AI data
            ai_count_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "ai_processed"}},
                            {"term": {"ai_processed": True}}
                        ]
                    }
                },
                "size": 0
            }

            response = await es_client.search(
                index="planning_applications",
                body=ai_count_query
            )

            ai_processed_count = response["hits"]["total"]["value"]

            # Count total applications
            total_query = {"query": {"match_all": {}}, "size": 0}
            total_response = await es_client.search(
                index="planning_applications",
                body=total_query
            )

            total_count = total_response["hits"]["total"]["value"]

            logger.info(f"Migration verification: {ai_processed_count}/{total_count} applications have AI data")

            # Verify specific AI fields
            field_checks = [
                "opportunity_score",
                "ai_summary",
                "embedding_vector"
            ]

            for field in field_checks:
                field_query = {
                    "query": {"exists": {"field": field}},
                    "size": 0
                }

                field_response = await es_client.search(
                    index="planning_applications",
                    body=field_query
                )

                field_count = field_response["hits"]["total"]["value"]
                logger.info(f"Field '{field}': {field_count} applications")

        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")

    def create_migration_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Create migration report"""
        duration = None
        if self.migration_stats["start_time"] and self.migration_stats["end_time"]:
            duration = self.migration_stats["end_time"] - self.migration_stats["start_time"]

        report = {
            "migration_report": {
                "summary": {
                    "total_applications": self.migration_stats["total_applications"],
                    "migrated_count": self.migration_stats["migrated_count"],
                    "error_count": self.migration_stats["error_count"],
                    "success_rate": (
                        self.migration_stats["migrated_count"] /
                        max(1, self.migration_stats["total_applications"])
                    ) * 100
                },
                "timing": {
                    "start_time": self.migration_stats["start_time"].isoformat() if self.migration_stats["start_time"] else None,
                    "end_time": self.migration_stats["end_time"].isoformat() if self.migration_stats["end_time"] else None,
                    "duration": str(duration) if duration else None
                },
                "ai_fields_added": [
                    "ai_processed", "ai_processed_at", "ai_processing_version",
                    "opportunity_score", "approval_probability", "ai_confidence_score",
                    "ai_rationale", "ai_risk_factors", "ai_recommendations",
                    "ai_summary", "ai_key_points", "ai_sentiment", "complexity_score",
                    "embedding_vector", "embedding_model", "embedding_dimensions",
                    "market_context"
                ],
                "elasticsearch_mapping_updated": True
            }
        }

        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                logger.info(f"Migration report saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving report: {str(e)}")

        return report


async def main():
    """Main entry point for data migration script"""
    parser = argparse.ArgumentParser(description="Data Migration for AI Enhancement Fields")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without updating data")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
    parser.add_argument("--force-update", action="store_true", help="Update applications that already have AI data")
    parser.add_argument("--report", help="Output file for migration report")

    args = parser.parse_args()

    try:
        migrator = DataMigrator()

        # Run migration
        results = await migrator.run_migration(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            force_update=args.force_update
        )

        # Generate report
        report = migrator.create_migration_report(args.report)

        # Print summary
        print(f"\nData Migration Summary:")
        print(f"Total Applications: {results['total_applications']}")
        print(f"Migrated: {results['migrated_count']}")
        print(f"Errors: {results['error_count']}")

        if results['total_applications'] > 0:
            success_rate = (results['migrated_count'] / results['total_applications']) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        if args.dry_run:
            print("\n[DRY RUN] No data was actually modified")

        return 0 if results['error_count'] == 0 else 1

    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))