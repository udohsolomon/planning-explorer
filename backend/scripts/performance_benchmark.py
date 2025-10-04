#!/usr/bin/env python3
"""
Performance Benchmarking Script for AI Pipeline

This script tests and benchmarks the performance of AI processing components
to ensure they meet the specified performance targets and identify optimization
opportunities.
"""

import asyncio
import logging
import argparse
import sys
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_processor import ai_processor, ProcessingMode
from app.ai.opportunity_scorer import OpportunityScorer
from app.ai.summarizer import DocumentSummarizer, SummaryType, SummaryLength
from app.ai.embeddings import EmbeddingService, EmbeddingType
from app.ai.nlp_processor import NLPProcessor
from app.ai.market_intelligence import MarketIntelligenceEngine, AnalysisPeriod
from app.models.planning import PlanningApplication
from app.core.ai_config import ai_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite for AI pipeline components.
    """

    def __init__(self):
        self.results = {
            "benchmark_metadata": {
                "start_time": None,
                "end_time": None,
                "total_duration": None,
                "ai_config": ai_config.to_dict()
            },
            "component_benchmarks": {},
            "integration_benchmarks": {},
            "performance_analysis": {},
            "recommendations": []
        }
        self.test_applications = []

    async def run_full_benchmark(
        self,
        sample_size: int = 100,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive performance benchmark of all AI components.

        Args:
            sample_size: Number of test applications to use
            output_file: File to save benchmark results

        Returns:
            Complete benchmark results
        """
        logger.info(f"Starting comprehensive AI pipeline benchmark with {sample_size} samples")
        self.results["benchmark_metadata"]["start_time"] = datetime.utcnow()

        try:
            # Generate test data
            await self._generate_test_data(sample_size)

            # Benchmark individual components
            await self._benchmark_opportunity_scorer()
            await self._benchmark_document_summarizer()
            await self._benchmark_embedding_service()
            await self._benchmark_nlp_processor()
            await self._benchmark_market_intelligence()

            # Benchmark integrated processing
            await self._benchmark_integrated_processing()

            # Analyze performance
            self._analyze_performance()

            # Generate recommendations
            self._generate_recommendations()

            self.results["benchmark_metadata"]["end_time"] = datetime.utcnow()
            self.results["benchmark_metadata"]["total_duration"] = str(
                self.results["benchmark_metadata"]["end_time"] -
                self.results["benchmark_metadata"]["start_time"]
            )

            # Save results
            if output_file:
                self._save_results(output_file)

            # Generate visualizations
            self._generate_visualizations()

            logger.info("Benchmark completed successfully")
            return self.results

        except Exception as e:
            logger.error(f"Benchmark failed: {str(e)}")
            self.results["error"] = str(e)
            return self.results

    async def _generate_test_data(self, sample_size: int) -> None:
        """Generate realistic test data for benchmarking"""
        logger.info(f"Generating {sample_size} test applications")

        development_types = ["residential", "commercial", "industrial", "mixed_use", "change_of_use"]
        statuses = ["submitted", "validated", "approved", "refused", "pending"]
        authorities = ["City Council", "Borough Council", "County Council", "District Council"]

        for i in range(sample_size):
            app = PlanningApplication(
                id=f"TEST-{i:06d}",
                reference=f"24/{i:06d}/APP",
                description=f"Test application {i} for {development_types[i % len(development_types)]} development. " +
                           "This is a detailed description that includes various planning considerations, " +
                           "environmental impact assessments, and community consultation requirements. " * (i % 3 + 1),
                proposal=f"Proposed {development_types[i % len(development_types)]} development with associated infrastructure",
                address=f"{100 + i} Test Street, Test Town, TE{i%9}T {i%9}ST",
                authority=authorities[i % len(authorities)],
                development_type=development_types[i % len(development_types)],
                status=statuses[i % len(statuses)],
                received_date=datetime.utcnow() - timedelta(days=i % 365),
                decision_date=datetime.utcnow() - timedelta(days=max(0, (i % 365) - 60)) if i % 3 == 0 else None
            )
            self.test_applications.append(app)

        logger.info(f"Generated {len(self.test_applications)} test applications")

    async def _benchmark_opportunity_scorer(self) -> None:
        """Benchmark opportunity scoring performance"""
        logger.info("Benchmarking Opportunity Scorer")

        if not ai_processor.opportunity_scorer:
            logger.warning("Opportunity Scorer not available - skipping benchmark")
            return

        scorer = ai_processor.opportunity_scorer
        test_sizes = [1, 5, 10, 25, 50]
        results = {
            "component": "OpportunityScorer",
            "target_time_ms": ai_config.settings.opportunity_scoring_timeout_ms,
            "test_results": []
        }

        for size in test_sizes:
            if size > len(self.test_applications):
                continue

            test_apps = self.test_applications[:size]
            times = []
            scores = []
            errors = 0

            logger.info(f"Testing opportunity scorer with {size} applications")

            for _ in range(3):  # Run multiple iterations
                start_time = time.time()
                try:
                    if size == 1:
                        result = await scorer.score_application(test_apps[0])
                        times.append((time.time() - start_time) * 1000)
                        scores.append(result.opportunity_score)
                    else:
                        batch_results = await scorer.batch_score_applications(test_apps)
                        batch_time = (time.time() - start_time) * 1000
                        times.append(batch_time / size)  # Per application time
                        scores.extend([r.opportunity_score for r in batch_results])
                except Exception as e:
                    errors += 1
                    logger.error(f"Error in opportunity scoring test: {e}")

            if times:
                results["test_results"].append({
                    "sample_size": size,
                    "avg_time_ms": statistics.mean(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "std_time_ms": statistics.stdev(times) if len(times) > 1 else 0,
                    "avg_score": statistics.mean(scores) if scores else 0,
                    "errors": errors,
                    "meets_target": statistics.mean(times) <= results["target_time_ms"]
                })

        self.results["component_benchmarks"]["opportunity_scorer"] = results

    async def _benchmark_document_summarizer(self) -> None:
        """Benchmark document summarization performance"""
        logger.info("Benchmarking Document Summarizer")

        if not ai_processor.document_summarizer:
            logger.warning("Document Summarizer not available - skipping benchmark")
            return

        summarizer = ai_processor.document_summarizer
        results = {
            "component": "DocumentSummarizer",
            "target_time_ms": ai_config.settings.summarization_timeout_ms,
            "test_results": []
        }

        # Test different summary types and lengths
        test_configs = [
            (SummaryType.GENERAL, SummaryLength.SHORT),
            (SummaryType.GENERAL, SummaryLength.MEDIUM),
            (SummaryType.GENERAL, SummaryLength.LONG),
            (SummaryType.OPPORTUNITIES, SummaryLength.MEDIUM),
            (SummaryType.RISKS, SummaryLength.MEDIUM)
        ]

        for summary_type, length in test_configs:
            times = []
            summary_lengths = []
            errors = 0

            logger.info(f"Testing summarizer with {summary_type.value} - {length.value}")

            for app in self.test_applications[:10]:  # Test with 10 applications
                start_time = time.time()
                try:
                    result = await summarizer.summarize_application(app, summary_type, length)
                    processing_time = (time.time() - start_time) * 1000
                    times.append(processing_time)
                    summary_lengths.append(len(result.summary))
                except Exception as e:
                    errors += 1
                    logger.error(f"Error in summarization test: {e}")

            if times:
                results["test_results"].append({
                    "summary_type": summary_type.value,
                    "length": length.value,
                    "avg_time_ms": statistics.mean(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "avg_summary_length": statistics.mean(summary_lengths),
                    "errors": errors,
                    "meets_target": statistics.mean(times) <= results["target_time_ms"]
                })

        self.results["component_benchmarks"]["document_summarizer"] = results

    async def _benchmark_embedding_service(self) -> None:
        """Benchmark vector embedding performance"""
        logger.info("Benchmarking Embedding Service")

        if not ai_processor.embedding_service:
            logger.warning("Embedding Service not available - skipping benchmark")
            return

        embedding_service = ai_processor.embedding_service
        results = {
            "component": "EmbeddingService",
            "target_time_ms": ai_config.settings.embedding_timeout_ms,
            "test_results": []
        }

        # Test different embedding types
        embedding_types = [EmbeddingType.DESCRIPTION, EmbeddingType.COMBINED, EmbeddingType.DOCUMENT]

        for emb_type in embedding_types:
            times = []
            dimensions = []
            errors = 0

            logger.info(f"Testing embeddings with type {emb_type.value}")

            for app in self.test_applications[:20]:  # Test with 20 applications
                start_time = time.time()
                try:
                    result = await embedding_service.generate_application_embedding(app, emb_type)
                    processing_time = (time.time() - start_time) * 1000
                    times.append(processing_time)
                    dimensions.append(result.dimensions)
                except Exception as e:
                    errors += 1
                    logger.error(f"Error in embedding test: {e}")

            if times:
                results["test_results"].append({
                    "embedding_type": emb_type.value,
                    "avg_time_ms": statistics.mean(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "avg_dimensions": statistics.mean(dimensions) if dimensions else 0,
                    "errors": errors,
                    "meets_target": statistics.mean(times) <= results["target_time_ms"]
                })

        # Test batch processing
        if self.test_applications:
            batch_sizes = [10, 25, 50]
            for batch_size in batch_sizes:
                if batch_size > len(self.test_applications):
                    continue

                start_time = time.time()
                try:
                    batch_results = await embedding_service.batch_generate_embeddings(
                        self.test_applications[:batch_size]
                    )
                    total_time = (time.time() - start_time) * 1000
                    avg_time_per_item = total_time / batch_size

                    results["test_results"].append({
                        "test_type": "batch_processing",
                        "batch_size": batch_size,
                        "total_time_ms": total_time,
                        "avg_time_per_item_ms": avg_time_per_item,
                        "successful_embeddings": len([r for r in batch_results if r.confidence_score > 0.5]),
                        "meets_target": avg_time_per_item <= results["target_time_ms"]
                    })
                except Exception as e:
                    logger.error(f"Error in batch embedding test: {e}")

        self.results["component_benchmarks"]["embedding_service"] = results

    async def _benchmark_nlp_processor(self) -> None:
        """Benchmark natural language processing performance"""
        logger.info("Benchmarking NLP Processor")

        if not ai_processor.nlp_processor:
            logger.warning("NLP Processor not available - skipping benchmark")
            return

        nlp_processor = ai_processor.nlp_processor
        results = {
            "component": "NLPProcessor",
            "test_results": []
        }

        # Test queries of varying complexity
        test_queries = [
            "residential developments",
            "approved commercial applications in London",
            "planning applications refused last year with environmental concerns",
            "show me mixed use developments near SW1A 1AA with high opportunity scores",
            "compare approval rates for residential vs commercial developments in 2024"
        ]

        for query in test_queries:
            times = []
            confidence_scores = []
            errors = 0

            logger.info(f"Testing NLP with query: '{query[:50]}...'")

            for _ in range(3):  # Multiple runs for consistency
                start_time = time.time()
                try:
                    result = await nlp_processor.process_query(query)
                    processing_time = (time.time() - start_time) * 1000
                    times.append(processing_time)
                    confidence_scores.append(result.confidence_score)
                except Exception as e:
                    errors += 1
                    logger.error(f"Error in NLP test: {e}")

            if times:
                results["test_results"].append({
                    "query": query,
                    "query_length": len(query),
                    "avg_time_ms": statistics.mean(times),
                    "avg_confidence": statistics.mean(confidence_scores),
                    "errors": errors
                })

        self.results["component_benchmarks"]["nlp_processor"] = results

    async def _benchmark_market_intelligence(self) -> None:
        """Benchmark market intelligence performance"""
        logger.info("Benchmarking Market Intelligence Engine")

        if not ai_processor.market_intelligence:
            logger.warning("Market Intelligence Engine not available - skipping benchmark")
            return

        market_intelligence = ai_processor.market_intelligence
        results = {
            "component": "MarketIntelligenceEngine",
            "test_results": []
        }

        # Test different analysis periods and data sizes
        test_configs = [
            (AnalysisPeriod.LAST_MONTH, 50),
            (AnalysisPeriod.LAST_QUARTER, 100),
            (AnalysisPeriod.LAST_YEAR, 200),
        ]

        for period, data_size in test_configs:
            if data_size > len(self.test_applications):
                continue

            times = []
            errors = 0

            logger.info(f"Testing market intelligence with {period.value} period and {data_size} applications")

            for _ in range(2):  # Run twice for consistency
                start_time = time.time()
                try:
                    result = await market_intelligence.generate_market_intelligence(
                        self.test_applications[:data_size], period
                    )
                    processing_time = (time.time() - start_time) * 1000
                    times.append(processing_time)
                except Exception as e:
                    errors += 1
                    logger.error(f"Error in market intelligence test: {e}")

            if times:
                results["test_results"].append({
                    "analysis_period": period.value,
                    "data_size": data_size,
                    "avg_time_ms": statistics.mean(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "errors": errors
                })

        self.results["component_benchmarks"]["market_intelligence"] = results

    async def _benchmark_integrated_processing(self) -> None:
        """Benchmark integrated AI processing pipeline"""
        logger.info("Benchmarking Integrated Processing Pipeline")

        results = {
            "test_results": []
        }

        # Test different processing modes
        processing_modes = [ProcessingMode.FAST, ProcessingMode.STANDARD, ProcessingMode.COMPREHENSIVE]
        test_sizes = [1, 5, 10]

        for mode in processing_modes:
            for size in test_sizes:
                if size > len(self.test_applications):
                    continue

                times = []
                success_rates = []
                errors = 0

                logger.info(f"Testing integrated processing with {mode.value} mode and {size} applications")

                for _ in range(2):  # Run twice
                    start_time = time.time()
                    try:
                        if size == 1:
                            result = await ai_processor.process_application(
                                self.test_applications[0], mode
                            )
                            processing_time = (time.time() - start_time) * 1000
                            times.append(processing_time)
                            success_rates.append(1.0 if result.success else 0.0)
                        else:
                            batch_result = await ai_processor.process_batch(
                                self.test_applications[:size], mode
                            )
                            total_time = (time.time() - start_time) * 1000
                            times.append(total_time / size)  # Per application
                            success_rates.append(batch_result.successful_count / batch_result.total_applications)
                    except Exception as e:
                        errors += 1
                        logger.error(f"Error in integrated processing test: {e}")

                if times:
                    results["test_results"].append({
                        "processing_mode": mode.value,
                        "batch_size": size,
                        "avg_time_per_app_ms": statistics.mean(times),
                        "avg_success_rate": statistics.mean(success_rates),
                        "errors": errors,
                        "meets_target": statistics.mean(times) <= 5000  # 5 second target
                    })

        self.results["integration_benchmarks"] = results

    def _analyze_performance(self) -> None:
        """Analyze benchmark results and identify performance issues"""
        logger.info("Analyzing performance results")

        analysis = {
            "performance_summary": {},
            "bottlenecks": [],
            "target_compliance": {},
            "scalability_analysis": {}
        }

        # Analyze component performance
        for component, results in self.results["component_benchmarks"].items():
            if "target_time_ms" in results:
                target = results["target_time_ms"]
                test_results = results["test_results"]

                if test_results:
                    avg_times = [r.get("avg_time_ms", 0) for r in test_results if "avg_time_ms" in r]
                    if avg_times:
                        analysis["performance_summary"][component] = {
                            "avg_processing_time_ms": statistics.mean(avg_times),
                            "target_time_ms": target,
                            "performance_ratio": statistics.mean(avg_times) / target,
                            "meets_target": all(t <= target for t in avg_times)
                        }

                        # Identify bottlenecks
                        if statistics.mean(avg_times) > target:
                            analysis["bottlenecks"].append({
                                "component": component,
                                "avg_time_ms": statistics.mean(avg_times),
                                "target_ms": target,
                                "slowdown_factor": statistics.mean(avg_times) / target
                            })

        # Analyze scalability
        for component, results in self.results["component_benchmarks"].items():
            test_results = results.get("test_results", [])
            batch_tests = [r for r in test_results if "batch_size" in r or "sample_size" in r]

            if len(batch_tests) > 1:
                sizes = [r.get("batch_size", r.get("sample_size", 1)) for r in batch_tests]
                times = [r.get("avg_time_ms", r.get("avg_time_per_item_ms", 0)) for r in batch_tests]

                if len(sizes) == len(times) and len(sizes) > 1:
                    # Simple linear regression to analyze scalability
                    scalability_factor = (times[-1] - times[0]) / (sizes[-1] - sizes[0]) if sizes[-1] != sizes[0] else 0
                    analysis["scalability_analysis"][component] = {
                        "scalability_factor": scalability_factor,
                        "scales_linearly": abs(scalability_factor) < 10  # Reasonable threshold
                    }

        self.results["performance_analysis"] = analysis

    def _generate_recommendations(self) -> None:
        """Generate performance optimization recommendations"""
        logger.info("Generating optimization recommendations")

        recommendations = []
        analysis = self.results.get("performance_analysis", {})

        # Recommendations based on bottlenecks
        bottlenecks = analysis.get("bottlenecks", [])
        for bottleneck in bottlenecks:
            component = bottleneck["component"]
            slowdown = bottleneck["slowdown_factor"]

            if component == "opportunity_scorer" and slowdown > 2:
                recommendations.append({
                    "priority": "high",
                    "component": component,
                    "issue": f"Processing time {slowdown:.1f}x slower than target",
                    "recommendation": "Consider model optimization or caching strategies",
                    "technical_details": "Implement result caching for similar applications or optimize scoring algorithm"
                })

            elif component == "document_summarizer" and slowdown > 2:
                recommendations.append({
                    "priority": "medium",
                    "component": component,
                    "issue": f"Summarization taking {slowdown:.1f}x longer than target",
                    "recommendation": "Optimize AI model selection or implement preprocessing",
                    "technical_details": "Use faster models for simple cases, preprocess text for better efficiency"
                })

            elif component == "embedding_service" and slowdown > 2:
                recommendations.append({
                    "priority": "high",
                    "component": component,
                    "issue": f"Embedding generation {slowdown:.1f}x slower than target",
                    "recommendation": "Implement batch processing optimization",
                    "technical_details": "Use batch embedding APIs, implement local caching, consider smaller models"
                })

        # General recommendations
        if not bottlenecks:
            recommendations.append({
                "priority": "low",
                "component": "general",
                "issue": "All components meeting performance targets",
                "recommendation": "Focus on monitoring and maintaining current performance",
                "technical_details": "Implement continuous performance monitoring and alerting"
            })

        # Scalability recommendations
        scalability = analysis.get("scalability_analysis", {})
        for component, scale_info in scalability.items():
            if not scale_info.get("scales_linearly", True):
                recommendations.append({
                    "priority": "medium",
                    "component": component,
                    "issue": "Non-linear scaling detected",
                    "recommendation": "Investigate and optimize for better scalability",
                    "technical_details": "Review algorithm complexity, implement better caching, consider parallelization"
                })

        self.results["recommendations"] = recommendations

    def _save_results(self, output_file: str) -> None:
        """Save benchmark results to file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"Benchmark results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

    def _generate_visualizations(self) -> None:
        """Generate performance visualization charts"""
        try:
            # Performance comparison chart
            plt.figure(figsize=(12, 8))

            # Extract performance data
            components = []
            avg_times = []
            targets = []

            for component, results in self.results["component_benchmarks"].items():
                if "target_time_ms" in results and results["test_results"]:
                    components.append(component.replace("_", " ").title())
                    avg_times.append(
                        statistics.mean([r.get("avg_time_ms", 0) for r in results["test_results"]
                                       if "avg_time_ms" in r])
                    )
                    targets.append(results["target_time_ms"])

            if components:
                x = range(len(components))
                plt.bar([i - 0.2 for i in x], avg_times, 0.4, label='Actual Time', alpha=0.8)
                plt.bar([i + 0.2 for i in x], targets, 0.4, label='Target Time', alpha=0.8)

                plt.xlabel('Components')
                plt.ylabel('Processing Time (ms)')
                plt.title('AI Component Performance vs Targets')
                plt.xticks(x, components, rotation=45)
                plt.legend()
                plt.tight_layout()
                plt.savefig('performance_benchmark.png', dpi=300, bbox_inches='tight')
                plt.close()

                logger.info("Performance visualization saved as performance_benchmark.png")

        except Exception as e:
            logger.warning(f"Could not generate visualizations: {str(e)}")

    def print_summary(self) -> None:
        """Print benchmark summary to console"""
        print("\n" + "="*60)
        print("AI PIPELINE PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)

        # Performance summary
        analysis = self.results.get("performance_analysis", {})
        performance_summary = analysis.get("performance_summary", {})

        print("\nComponent Performance:")
        print("-" * 40)
        for component, perf in performance_summary.items():
            status = "✓ PASS" if perf["meets_target"] else "✗ FAIL"
            print(f"{component:20} {perf['avg_processing_time_ms']:8.1f}ms "
                  f"(target: {perf['target_time_ms']}ms) {status}")

        # Bottlenecks
        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            print("\nPerformance Bottlenecks:")
            print("-" * 40)
            for bottleneck in bottlenecks:
                print(f"{bottleneck['component']:20} "
                      f"{bottleneck['slowdown_factor']:.1f}x slower than target")

        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            print("\nKey Recommendations:")
            print("-" * 40)
            high_priority = [r for r in recommendations if r["priority"] == "high"]
            for rec in high_priority[:3]:  # Show top 3 high priority
                print(f"• {rec['recommendation']}")

        print("\n" + "="*60)


async def main():
    """Main entry point for performance benchmark script"""
    parser = argparse.ArgumentParser(description="AI Pipeline Performance Benchmark")
    parser.add_argument("--sample-size", type=int, default=100, help="Number of test applications")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--component", help="Specific component to benchmark")
    parser.add_argument("--quick", action="store_true", help="Quick benchmark with smaller sample")

    args = parser.parse_args()

    try:
        benchmark = PerformanceBenchmark()

        sample_size = 20 if args.quick else args.sample_size

        if args.component:
            # Benchmark specific component
            logger.info(f"Running benchmark for component: {args.component}")
            await benchmark._generate_test_data(sample_size)

            if args.component == "opportunity_scorer":
                await benchmark._benchmark_opportunity_scorer()
            elif args.component == "summarizer":
                await benchmark._benchmark_document_summarizer()
            elif args.component == "embeddings":
                await benchmark._benchmark_embedding_service()
            elif args.component == "nlp":
                await benchmark._benchmark_nlp_processor()
            elif args.component == "market_intelligence":
                await benchmark._benchmark_market_intelligence()
            else:
                print(f"Unknown component: {args.component}")
                return 1
        else:
            # Full benchmark
            await benchmark.run_full_benchmark(sample_size, args.output)

        # Print summary
        benchmark.print_summary()

        return 0

    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Benchmark failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))