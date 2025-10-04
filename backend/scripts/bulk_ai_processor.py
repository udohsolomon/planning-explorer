#!/usr/bin/env python3
"""
Bulk AI Processing Script for Planning Applications

This script processes large batches of planning applications through the
AI pipeline, with support for resumable processing, progress tracking,
and performance optimization.
"""

import asyncio
import logging
import argparse
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import csv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_processor import ai_processor, ProcessingMode, ProcessingPriority
from app.services.search import search_service
from app.models.planning import PlanningApplication
from app.core.ai_config import ai_config
from app.db.elasticsearch import es_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bulk_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BulkProcessor:
    """
    Bulk AI processing coordinator with advanced features for large-scale
    planning application processing.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.stats = {
            "total_applications": 0,
            "processed_count": 0,
            "successful_count": 0,
            "failed_count": 0,
            "start_time": None,
            "end_time": None,
            "processing_rate": 0.0,
            "errors": []
        }
        self.processed_ids = set()
        self.checkpoint_file = "bulk_processing_checkpoint.json"

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load processing configuration"""
        default_config = {
            "batch_size": 100,
            "max_concurrent": 10,
            "processing_mode": "standard",
            "features": ["opportunity_scoring", "summarization", "embeddings"],
            "checkpoint_interval": 50,
            "retry_attempts": 3,
            "retry_delay": 5,
            "output_format": "json",
            "elasticsearch_batch_size": 500,
            "performance_targets": {
                "max_processing_time_per_app": 5000,  # ms
                "min_processing_rate": 20  # apps per minute
            }
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                default_config.update(custom_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")

        return default_config

    async def process_all_applications(
        self,
        filters: Optional[Dict[str, Any]] = None,
        resume: bool = False
    ) -> Dict[str, Any]:
        """
        Process all planning applications with AI pipeline.

        Args:
            filters: Elasticsearch filters to apply
            resume: Whether to resume from checkpoint

        Returns:
            Processing results and statistics
        """
        logger.info("Starting bulk AI processing of all applications")
        self.stats["start_time"] = datetime.utcnow()

        try:
            # Load checkpoint if resuming
            if resume:
                self._load_checkpoint()

            # Get applications to process
            applications = await self._get_applications_to_process(filters)
            self.stats["total_applications"] = len(applications)

            logger.info(f"Found {len(applications)} applications to process")

            if not applications:
                logger.warning("No applications found to process")
                return self.stats

            # Process in batches
            await self._process_applications_in_batches(applications)

            self.stats["end_time"] = datetime.utcnow()
            self._calculate_final_stats()

            # Clean up checkpoint
            self._cleanup_checkpoint()

            logger.info(f"Bulk processing completed. Processed {self.stats['processed_count']} applications")
            return self.stats

        except Exception as e:
            logger.error(f"Critical error in bulk processing: {str(e)}")
            self.stats["errors"].append(f"Critical error: {str(e)}")
            return self.stats

    async def process_specific_applications(
        self,
        application_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Process specific applications by ID.

        Args:
            application_ids: List of application IDs to process

        Returns:
            Processing results
        """
        logger.info(f"Starting processing of {len(application_ids)} specific applications")
        self.stats["start_time"] = datetime.utcnow()
        self.stats["total_applications"] = len(application_ids)

        try:
            # Fetch applications
            applications = []
            for app_id in application_ids:
                try:
                    app = await search_service.get_application_by_id(app_id)
                    if app:
                        applications.append(app)
                    else:
                        logger.warning(f"Application {app_id} not found")
                        self.stats["errors"].append(f"Application {app_id} not found")
                except Exception as e:
                    logger.error(f"Error fetching application {app_id}: {e}")
                    self.stats["errors"].append(f"Error fetching {app_id}: {str(e)}")

            if not applications:
                logger.error("No valid applications found to process")
                return self.stats

            # Process applications
            await self._process_applications_in_batches(applications)

            self.stats["end_time"] = datetime.utcnow()
            self._calculate_final_stats()

            return self.stats

        except Exception as e:
            logger.error(f"Error processing specific applications: {str(e)}")
            self.stats["errors"].append(f"Processing error: {str(e)}")
            return self.stats

    async def _get_applications_to_process(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PlanningApplication]:
        """Get applications to process from Elasticsearch"""
        try:
            # Build Elasticsearch query
            query = {
                "query": {
                    "bool": {
                        "must": [{"match_all": {}}],
                        "must_not": []
                    }
                },
                "size": 10000,  # Maximum ES allows
                "_source": True
            }

            # Apply filters
            if filters:
                if "status" in filters:
                    query["query"]["bool"]["must"].append({
                        "term": {"status.keyword": filters["status"]}
                    })
                if "development_type" in filters:
                    query["query"]["bool"]["must"].append({
                        "term": {"development_type.keyword": filters["development_type"]}
                    })
                if "authority" in filters:
                    query["query"]["bool"]["must"].append({
                        "term": {"authority.keyword": filters["authority"]}
                    })
                if "date_range" in filters:
                    query["query"]["bool"]["must"].append({
                        "range": {"received_date": filters["date_range"]}
                    })

            # Exclude already processed applications if resuming
            if self.processed_ids:
                query["query"]["bool"]["must_not"].append({
                    "terms": {"id.keyword": list(self.processed_ids)}
                })

            # Execute search with scroll for large datasets
            applications = []

            # Use scroll for large datasets
            scroll_id = None
            try:
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

            finally:
                # Clean up scroll
                if scroll_id:
                    try:
                        await es_client.clear_scroll(scroll_id=scroll_id)
                    except:
                        pass

            return applications

        except Exception as e:
            logger.error(f"Error fetching applications from Elasticsearch: {str(e)}")
            return []

    async def _process_applications_in_batches(self, applications: List[PlanningApplication]) -> None:
        """Process applications in optimized batches"""
        batch_size = self.config["batch_size"]
        total_batches = (len(applications) + batch_size - 1) // batch_size

        logger.info(f"Processing {len(applications)} applications in {total_batches} batches of {batch_size}")

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(applications))
            batch = applications[start_idx:end_idx]

            logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch)} applications)")

            try:
                # Process batch with AI pipeline
                batch_result = await ai_processor.process_batch(
                    batch,
                    ProcessingMode(self.config["processing_mode"]),
                    self.config["features"],
                    self.config["max_concurrent"]
                )

                # Update statistics
                self.stats["processed_count"] += batch_result.total_applications
                self.stats["successful_count"] += batch_result.successful_count
                self.stats["failed_count"] += batch_result.failed_count

                # Track processed IDs
                for result in batch_result.results:
                    self.processed_ids.add(result.application_id)

                # Store results in Elasticsearch
                await self._store_batch_results(batch_result)

                # Update processing rate
                self._update_processing_rate()

                # Create checkpoint
                if self.stats["processed_count"] % self.config["checkpoint_interval"] == 0:
                    self._create_checkpoint()

                # Log progress
                progress_pct = (self.stats["processed_count"] / self.stats["total_applications"]) * 100
                logger.info(f"Progress: {progress_pct:.1f}% "
                           f"({self.stats['processed_count']}/{self.stats['total_applications']}) "
                           f"- Success rate: {self._get_success_rate():.1f}%")

            except Exception as e:
                logger.error(f"Error processing batch {batch_num + 1}: {str(e)}")
                self.stats["errors"].append(f"Batch {batch_num + 1} error: {str(e)}")

                # Add failed applications to processed set to avoid reprocessing
                for app in batch:
                    self.processed_ids.add(app.id)
                    self.stats["failed_count"] += 1
                    self.stats["processed_count"] += 1

    async def _store_batch_results(self, batch_result) -> None:
        """Store batch processing results in Elasticsearch"""
        try:
            bulk_operations = []

            for result in batch_result.results:
                if result.success:
                    # Update application with AI results
                    update_doc = {
                        "ai_processed": True,
                        "ai_processed_at": result.generated_at.isoformat(),
                        "ai_processing_version": "2.0.0"
                    }

                    # Add AI results
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

                    if "summarization" in result.results:
                        summary = result.results["summarization"]
                        update_doc.update({
                            "ai_summary": summary["summary"],
                            "ai_key_points": summary["key_points"],
                            "ai_sentiment": summary["sentiment"],
                            "complexity_score": summary["complexity_score"]
                        })

                    if "embeddings" in result.results:
                        embedding = result.results["embeddings"]
                        update_doc.update({
                            "embedding_vector": embedding.get("_vector"),  # Store vector
                            "embedding_model": embedding["model_used"],
                            "embedding_dimensions": embedding["dimensions"]
                        })

                    # Prepare bulk operation
                    bulk_operations.extend([
                        {"update": {"_index": "planning_applications", "_id": result.application_id}},
                        {"doc": update_doc, "doc_as_upsert": False}
                    ])

            # Execute bulk update
            if bulk_operations:
                response = await es_client.bulk(body=bulk_operations)

                if response.get("errors"):
                    error_count = len([item for item in response["items"]
                                     if "update" in item and "error" in item["update"]])
                    logger.warning(f"Bulk update had {error_count} errors")

        except Exception as e:
            logger.error(f"Error storing batch results: {str(e)}")

    def _update_processing_rate(self) -> None:
        """Update processing rate statistics"""
        if self.stats["start_time"]:
            elapsed = datetime.utcnow() - self.stats["start_time"]
            elapsed_minutes = elapsed.total_seconds() / 60
            if elapsed_minutes > 0:
                self.stats["processing_rate"] = self.stats["processed_count"] / elapsed_minutes

    def _get_success_rate(self) -> float:
        """Calculate current success rate"""
        if self.stats["processed_count"] > 0:
            return (self.stats["successful_count"] / self.stats["processed_count"]) * 100
        return 0.0

    def _create_checkpoint(self) -> None:
        """Create processing checkpoint"""
        checkpoint_data = {
            "processed_ids": list(self.processed_ids),
            "stats": self.stats.copy(),
            "timestamp": datetime.utcnow().isoformat(),
            "config": self.config
        }

        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, default=str)
            logger.info(f"Checkpoint created with {len(self.processed_ids)} processed applications")
        except Exception as e:
            logger.error(f"Error creating checkpoint: {str(e)}")

    def _load_checkpoint(self) -> None:
        """Load processing checkpoint"""
        try:
            if Path(self.checkpoint_file).exists():
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)

                self.processed_ids = set(checkpoint_data.get("processed_ids", []))

                # Restore relevant stats
                saved_stats = checkpoint_data.get("stats", {})
                for key in ["processed_count", "successful_count", "failed_count", "errors"]:
                    if key in saved_stats:
                        self.stats[key] = saved_stats[key]

                logger.info(f"Resumed from checkpoint with {len(self.processed_ids)} already processed applications")
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")

    def _cleanup_checkpoint(self) -> None:
        """Clean up checkpoint file after successful completion"""
        try:
            if Path(self.checkpoint_file).exists():
                Path(self.checkpoint_file).unlink()
                logger.info("Checkpoint file cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up checkpoint: {str(e)}")

    def _calculate_final_stats(self) -> None:
        """Calculate final processing statistics"""
        if self.stats["start_time"] and self.stats["end_time"]:
            total_time = self.stats["end_time"] - self.stats["start_time"]
            self.stats["total_processing_time"] = str(total_time)

            total_minutes = total_time.total_seconds() / 60
            if total_minutes > 0:
                self.stats["final_processing_rate"] = self.stats["processed_count"] / total_minutes

        self.stats["success_rate"] = self._get_success_rate()

    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate processing report"""
        report = {
            "bulk_processing_report": {
                "execution_summary": {
                    "total_applications": self.stats["total_applications"],
                    "processed_count": self.stats["processed_count"],
                    "successful_count": self.stats["successful_count"],
                    "failed_count": self.stats["failed_count"],
                    "success_rate": f"{self._get_success_rate():.1f}%",
                    "processing_rate": f"{self.stats.get('final_processing_rate', 0):.1f} apps/min"
                },
                "timing": {
                    "start_time": self.stats["start_time"].isoformat() if self.stats["start_time"] else None,
                    "end_time": self.stats["end_time"].isoformat() if self.stats["end_time"] else None,
                    "total_processing_time": self.stats.get("total_processing_time")
                },
                "configuration": self.config,
                "errors": self.stats["errors"],
                "ai_service_status": ai_processor.get_service_status()
            }
        }

        # Save report if output file specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                logger.info(f"Report saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving report: {str(e)}")

        return report


async def main():
    """Main entry point for bulk processing script"""
    parser = argparse.ArgumentParser(description="Bulk AI Processing for Planning Applications")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--application-ids", nargs="+", help="Specific application IDs to process")
    parser.add_argument("--filters", help="JSON filters for application selection")
    parser.add_argument("--report", help="Output file for processing report")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual processing")

    args = parser.parse_args()

    try:
        # Initialize processor
        processor = BulkProcessor(args.config)

        # Parse filters if provided
        filters = None
        if args.filters:
            try:
                filters = json.loads(args.filters)
            except Exception as e:
                logger.error(f"Invalid filters JSON: {e}")
                return 1

        # Perform dry run if requested
        if args.dry_run:
            logger.info("Performing dry run - no actual processing will occur")
            # Would implement dry run logic here
            return 0

        # Process applications
        if args.application_ids:
            results = await processor.process_specific_applications(args.application_ids)
        else:
            results = await processor.process_all_applications(filters, args.resume)

        # Generate report
        report = processor.generate_report(args.report)

        # Print summary
        print(f"\nBulk Processing Summary:")
        print(f"Total Applications: {results['total_applications']}")
        print(f"Processed: {results['processed_count']}")
        print(f"Successful: {results['successful_count']}")
        print(f"Failed: {results['failed_count']}")
        print(f"Success Rate: {processor._get_success_rate():.1f}%")

        if results["errors"]:
            print(f"Errors encountered: {len(results['errors'])}")

        return 0 if results["failed_count"] == 0 else 1

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))