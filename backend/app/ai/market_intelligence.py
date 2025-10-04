"""
Market Intelligence Engine for Planning Applications

This module provides comprehensive market analysis, trend identification,
competitive landscape insights, and opportunity assessment for UK planning
and property development market.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
from collections import defaultdict, Counter

from app.core.ai_config import ai_config
from app.models.planning import PlanningApplication

logger = logging.getLogger(__name__)


class TrendDirection(str, Enum):
    """Direction of market trends"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class MarketSegment(str, Enum):
    """Market segments for analysis"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    RETAIL = "retail"
    OFFICE = "office"


class AnalysisPeriod(str, Enum):
    """Time periods for analysis"""
    LAST_MONTH = "last_month"
    LAST_QUARTER = "last_quarter"
    LAST_YEAR = "last_year"
    LAST_2_YEARS = "last_2_years"
    ALL_TIME = "all_time"


@dataclass
class TrendAnalysis:
    """Analysis of market trends"""
    metric: str
    trend_direction: TrendDirection
    change_percentage: float
    confidence_score: float
    data_points: List[Dict[str, Any]]
    forecast: Optional[Dict[str, Any]]
    insights: List[str]


@dataclass
class MarketMetrics:
    """Key market metrics for a segment"""
    total_applications: int
    approval_rate: float
    average_processing_time: float
    application_volume_trend: TrendDirection
    approval_rate_trend: TrendDirection
    dominant_development_types: List[Dict[str, Any]]
    authority_performance: Dict[str, Any]
    geographical_distribution: Dict[str, Any]


@dataclass
class CompetitiveAnalysis:
    """Competitive landscape analysis"""
    market_leaders: List[Dict[str, Any]]
    market_concentration: float
    opportunity_gaps: List[Dict[str, Any]]
    competitive_intensity: str
    barriers_to_entry: List[str]
    success_factors: List[str]


@dataclass
class MarketOpportunity:
    """Identified market opportunity"""
    opportunity_id: str
    title: str
    description: str
    market_size: Dict[str, Any]
    growth_potential: float
    competition_level: str
    barriers: List[str]
    success_probability: float
    recommendations: List[str]
    supporting_data: Dict[str, Any]


@dataclass
class MarketIntelligenceReport:
    """Comprehensive market intelligence report"""
    analysis_period: AnalysisPeriod
    market_overview: Dict[str, Any]
    trend_analyses: List[TrendAnalysis]
    market_metrics: Dict[MarketSegment, MarketMetrics]
    competitive_analysis: CompetitiveAnalysis
    opportunities: List[MarketOpportunity]
    risks: List[Dict[str, Any]]
    recommendations: List[str]
    data_quality_score: float
    generated_at: datetime


class MarketIntelligenceEngine:
    """
    Comprehensive market intelligence engine for planning applications.

    Provides trend analysis, competitive insights, opportunity identification,
    and strategic market intelligence for property professionals.
    """

    def __init__(self):
        self.config = ai_config
        self._initialize_analysis_framework()

    def _initialize_analysis_framework(self) -> None:
        """Initialize analysis framework and metrics"""
        self.key_metrics = [
            "application_volume",
            "approval_rate",
            "processing_time",
            "market_concentration",
            "geographic_spread",
            "value_density"
        ]

        self.trend_indicators = {
            "volume": ["total_applications", "monthly_submissions"],
            "approval": ["approval_rate", "success_patterns"],
            "timing": ["processing_time", "decision_speed"],
            "market": ["competition", "opportunity_density"]
        }

        # Market benchmarks (would be populated from real data)
        self.benchmarks = {
            "approval_rate": {"excellent": 0.85, "good": 0.75, "average": 0.65, "poor": 0.50},
            "processing_time": {"fast": 8, "average": 12, "slow": 16, "very_slow": 24},
            "market_concentration": {"consolidated": 0.8, "competitive": 0.5, "fragmented": 0.3}
        }

    async def generate_market_intelligence(
        self,
        applications: List[PlanningApplication],
        analysis_period: AnalysisPeriod = AnalysisPeriod.LAST_YEAR,
        focus_segments: Optional[List[MarketSegment]] = None,
        geographical_scope: Optional[str] = None
    ) -> MarketIntelligenceReport:
        """
        Generate comprehensive market intelligence report.

        Args:
            applications: List of planning applications for analysis
            analysis_period: Time period for analysis
            focus_segments: Specific market segments to analyze
            geographical_scope: Geographic area to focus on

        Returns:
            MarketIntelligenceReport with comprehensive analysis
        """
        start_time = time.time()

        try:
            # Filter applications by period and scope
            filtered_apps = self._filter_applications(
                applications, analysis_period, geographical_scope
            )

            if len(filtered_apps) < 10:
                logger.warning(f"Limited data available: only {len(filtered_apps)} applications")

            # Generate market overview
            market_overview = await self._generate_market_overview(filtered_apps)

            # Perform trend analysis
            trend_analyses = await self._analyze_trends(filtered_apps, analysis_period)

            # Calculate market metrics by segment
            market_metrics = await self._calculate_market_metrics(
                filtered_apps, focus_segments or list(MarketSegment)
            )

            # Perform competitive analysis
            competitive_analysis = await self._analyze_competition(filtered_apps)

            # Identify opportunities
            opportunities = await self._identify_opportunities(
                filtered_apps, market_metrics, trend_analyses
            )

            # Assess risks
            risks = await self._assess_market_risks(filtered_apps, trend_analyses)

            # Generate strategic recommendations
            recommendations = await self._generate_recommendations(
                market_metrics, opportunities, risks, trend_analyses
            )

            # Calculate data quality score
            data_quality_score = self._calculate_data_quality_score(filtered_apps)

            report = MarketIntelligenceReport(
                analysis_period=analysis_period,
                market_overview=market_overview,
                trend_analyses=trend_analyses,
                market_metrics=market_metrics,
                competitive_analysis=competitive_analysis,
                opportunities=opportunities,
                risks=risks,
                recommendations=recommendations,
                data_quality_score=data_quality_score,
                generated_at=datetime.utcnow()
            )

            processing_time = time.time() - start_time
            logger.info(f"Generated market intelligence report in {processing_time:.2f}s for {len(filtered_apps)} applications")

            return report

        except Exception as e:
            logger.error(f"Error generating market intelligence: {str(e)}")
            return self._generate_fallback_report(applications, analysis_period)

    def _filter_applications(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod,
        geographical_scope: Optional[str]
    ) -> List[PlanningApplication]:
        """Filter applications by time period and geographical scope"""
        now = datetime.utcnow()

        # Calculate date threshold
        if period == AnalysisPeriod.LAST_MONTH:
            threshold = now - timedelta(days=30)
        elif period == AnalysisPeriod.LAST_QUARTER:
            threshold = now - timedelta(days=90)
        elif period == AnalysisPeriod.LAST_YEAR:
            threshold = now - timedelta(days=365)
        elif period == AnalysisPeriod.LAST_2_YEARS:
            threshold = now - timedelta(days=730)
        else:  # ALL_TIME
            threshold = datetime.min

        filtered = []
        for app in applications:
            # Filter by date
            if app.date_received and app.date_received >= threshold:
                # Filter by geography if specified
                if geographical_scope:
                    if (geographical_scope.lower() in (app.address or "").lower() or
                        geographical_scope.lower() in (app.authority or "").lower()):
                        filtered.append(app)
                else:
                    filtered.append(app)

        return filtered

    async def _generate_market_overview(self, applications: List[PlanningApplication]) -> Dict[str, Any]:
        """Generate high-level market overview"""
        if not applications:
            return {"total_applications": 0, "status": "insufficient_data"}

        # Calculate basic statistics
        total_apps = len(applications)
        approved_apps = len([app for app in applications if app.status == "approved"])
        refused_apps = len([app for app in applications if app.status == "refused"])
        pending_apps = len([app for app in applications if app.status in ["submitted", "validated", "pending"]])

        # Development type distribution
        dev_types = Counter(app.development_type for app in applications if app.development_type)

        # Authority distribution
        authorities = Counter(app.authority for app in applications if app.authority)

        # Processing times (for decided applications)
        processing_times = []
        for app in applications:
            if app.date_received and app.decision_date:
                days = (app.decision_date - app.date_received).days
                if days > 0:
                    processing_times.append(days)

        avg_processing_time = np.mean(processing_times) if processing_times else None

        return {
            "total_applications": total_apps,
            "approval_rate": approved_apps / max(1, approved_apps + refused_apps),
            "pending_applications": pending_apps,
            "average_processing_time_days": avg_processing_time,
            "development_type_distribution": dict(dev_types.most_common(10)),
            "authority_distribution": dict(authorities.most_common(10)),
            "market_activity_level": self._classify_activity_level(total_apps),
            "data_completeness": self._assess_data_completeness(applications)
        }

    def _classify_activity_level(self, total_applications: int) -> str:
        """Classify market activity level"""
        if total_applications > 1000:
            return "very_high"
        elif total_applications > 500:
            return "high"
        elif total_applications > 100:
            return "moderate"
        elif total_applications > 20:
            return "low"
        else:
            return "very_low"

    def _assess_data_completeness(self, applications: List[PlanningApplication]) -> float:
        """Assess completeness of application data"""
        if not applications:
            return 0.0

        required_fields = ["id", "description", "development_type", "status", "authority", "address"]
        total_score = 0

        for app in applications:
            field_score = 0
            for field in required_fields:
                if hasattr(app, field) and getattr(app, field):
                    field_score += 1
            total_score += field_score / len(required_fields)

        return total_score / len(applications)

    async def _analyze_trends(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> List[TrendAnalysis]:
        """Analyze market trends across different metrics"""
        trends = []

        # Application volume trend
        volume_trend = await self._analyze_volume_trend(applications, period)
        trends.append(volume_trend)

        # Approval rate trend
        approval_trend = await self._analyze_approval_trend(applications, period)
        trends.append(approval_trend)

        # Processing time trend
        processing_trend = await self._analyze_processing_time_trend(applications, period)
        trends.append(processing_trend)

        # Development type trends
        dev_type_trends = await self._analyze_development_type_trends(applications, period)
        trends.extend(dev_type_trends)

        return trends

    async def _analyze_volume_trend(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> TrendAnalysis:
        """Analyze application volume trends"""
        # Group applications by month
        monthly_counts = defaultdict(int)
        for app in applications:
            if app.date_received:
                month_key = app.date_received.strftime("%Y-%m")
                monthly_counts[month_key] += 1

        # Convert to time series
        sorted_months = sorted(monthly_counts.keys())
        counts = [monthly_counts[month] for month in sorted_months]

        if len(counts) < 2:
            return TrendAnalysis(
                metric="application_volume",
                trend_direction=TrendDirection.STABLE,
                change_percentage=0.0,
                confidence_score=0.2,
                data_points=[],
                forecast=None,
                insights=["Insufficient data for trend analysis"]
            )

        # Calculate trend
        trend_direction, change_percentage = self._calculate_trend(counts)

        data_points = [
            {"period": month, "value": monthly_counts[month]}
            for month in sorted_months
        ]

        insights = []
        if abs(change_percentage) > 20:
            insights.append(f"Significant {'increase' if change_percentage > 0 else 'decrease'} in application volume")
        if len(set(counts)) == 1:
            insights.append("Application volume has remained constant")

        return TrendAnalysis(
            metric="application_volume",
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            confidence_score=self._calculate_trend_confidence(counts),
            data_points=data_points,
            forecast=self._generate_simple_forecast(counts),
            insights=insights
        )

    async def _analyze_approval_trend(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> TrendAnalysis:
        """Analyze approval rate trends"""
        # Group by month and calculate approval rates
        monthly_data = defaultdict(lambda: {"approved": 0, "total": 0})

        for app in applications:
            if app.date_received and app.status in ["approved", "refused"]:
                month_key = app.date_received.strftime("%Y-%m")
                monthly_data[month_key]["total"] += 1
                if app.status == "approved":
                    monthly_data[month_key]["approved"] += 1

        # Calculate approval rates
        sorted_months = sorted(monthly_data.keys())
        approval_rates = []
        for month in sorted_months:
            data = monthly_data[month]
            if data["total"] > 0:
                rate = data["approved"] / data["total"]
                approval_rates.append(rate)

        if len(approval_rates) < 2:
            return TrendAnalysis(
                metric="approval_rate",
                trend_direction=TrendDirection.STABLE,
                change_percentage=0.0,
                confidence_score=0.2,
                data_points=[],
                forecast=None,
                insights=["Insufficient data for approval rate trend analysis"]
            )

        trend_direction, change_percentage = self._calculate_trend(approval_rates)

        data_points = [
            {
                "period": month,
                "value": monthly_data[month]["approved"] / max(1, monthly_data[month]["total"])
            }
            for month in sorted_months if monthly_data[month]["total"] > 0
        ]

        return TrendAnalysis(
            metric="approval_rate",
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            confidence_score=self._calculate_trend_confidence(approval_rates),
            data_points=data_points,
            forecast=None,
            insights=self._generate_approval_insights(approval_rates, change_percentage)
        )

    async def _analyze_processing_time_trend(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> TrendAnalysis:
        """Analyze processing time trends"""
        monthly_times = defaultdict(list)

        for app in applications:
            if app.date_received and app.decision_date:
                processing_days = (app.decision_date - app.date_received).days
                if processing_days > 0:
                    month_key = app.date_received.strftime("%Y-%m")
                    monthly_times[month_key].append(processing_days)

        # Calculate average processing times per month
        sorted_months = sorted(monthly_times.keys())
        avg_times = []
        for month in sorted_months:
            if monthly_times[month]:
                avg_time = np.mean(monthly_times[month])
                avg_times.append(avg_time)

        if len(avg_times) < 2:
            return TrendAnalysis(
                metric="processing_time",
                trend_direction=TrendDirection.STABLE,
                change_percentage=0.0,
                confidence_score=0.2,
                data_points=[],
                forecast=None,
                insights=["Insufficient data for processing time trend analysis"]
            )

        trend_direction, change_percentage = self._calculate_trend(avg_times)

        data_points = [
            {
                "period": month,
                "value": np.mean(monthly_times[month]) if monthly_times[month] else 0
            }
            for month in sorted_months if monthly_times[month]
        ]

        return TrendAnalysis(
            metric="processing_time",
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            confidence_score=self._calculate_trend_confidence(avg_times),
            data_points=data_points,
            forecast=None,
            insights=self._generate_processing_time_insights(avg_times, change_percentage)
        )

    async def _analyze_development_type_trends(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> List[TrendAnalysis]:
        """Analyze trends for different development types"""
        trends = []

        # Get major development types
        dev_type_counts = Counter(app.development_type for app in applications if app.development_type)
        major_types = [dtype for dtype, count in dev_type_counts.most_common(5) if count >= 10]

        for dev_type in major_types:
            # Filter applications for this development type
            type_apps = [app for app in applications if app.development_type == dev_type]

            # Analyze volume trend for this type
            monthly_counts = defaultdict(int)
            for app in type_apps:
                if app.date_received:
                    month_key = app.date_received.strftime("%Y-%m")
                    monthly_counts[month_key] += 1

            counts = list(monthly_counts.values())
            if len(counts) >= 2:
                trend_direction, change_percentage = self._calculate_trend(counts)

                trends.append(TrendAnalysis(
                    metric=f"{dev_type}_volume",
                    trend_direction=trend_direction,
                    change_percentage=change_percentage,
                    confidence_score=self._calculate_trend_confidence(counts),
                    data_points=[
                        {"period": month, "value": count}
                        for month, count in sorted(monthly_counts.items())
                    ],
                    forecast=None,
                    insights=[f"{dev_type.title()} applications showing {trend_direction.value} trend"]
                ))

        return trends

    def _calculate_trend(self, values: List[float]) -> Tuple[TrendDirection, float]:
        """Calculate trend direction and percentage change"""
        if len(values) < 2:
            return TrendDirection.STABLE, 0.0

        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        # Calculate percentage change from first to last
        first_val = values[0]
        last_val = values[-1]

        if first_val == 0:
            change_percentage = 0.0
        else:
            change_percentage = ((last_val - first_val) / first_val) * 100

        # Determine trend direction
        if abs(slope) < 0.1 and abs(change_percentage) < 5:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Check for volatility
        if len(values) > 3:
            volatility = np.std(values) / max(np.mean(values), 1)
            if volatility > 0.5:
                direction = TrendDirection.VOLATILE

        return direction, change_percentage

    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence score for trend analysis"""
        if len(values) < 2:
            return 0.1

        # Base confidence on data points and consistency
        data_points_factor = min(1.0, len(values) / 12)  # Full confidence with 12+ months

        # Consistency factor (lower variance = higher confidence)
        if len(values) > 1:
            cv = np.std(values) / max(np.mean(values), 1)  # Coefficient of variation
            consistency_factor = max(0.3, 1.0 - cv)
        else:
            consistency_factor = 0.5

        return min(1.0, data_points_factor * consistency_factor)

    def _generate_simple_forecast(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Generate simple forecast based on trend"""
        if len(values) < 3:
            return None

        # Simple linear extrapolation
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        next_value = slope * len(values) + intercept

        return {
            "next_period_estimate": max(0, round(next_value)),
            "method": "linear_extrapolation",
            "confidence": "low"
        }

    def _generate_approval_insights(self, approval_rates: List[float], change_percentage: float) -> List[str]:
        """Generate insights for approval rate trends"""
        insights = []

        avg_rate = np.mean(approval_rates)

        if avg_rate > 0.8:
            insights.append("High approval rate indicates favorable planning environment")
        elif avg_rate < 0.5:
            insights.append("Low approval rate suggests challenging planning conditions")

        if abs(change_percentage) > 10:
            direction = "improving" if change_percentage > 0 else "declining"
            insights.append(f"Approval rates are {direction} significantly")

        return insights

    def _generate_processing_time_insights(self, processing_times: List[float], change_percentage: float) -> List[str]:
        """Generate insights for processing time trends"""
        insights = []

        avg_time = np.mean(processing_times)

        if avg_time < 10:
            insights.append("Fast processing times indicate efficient planning authority")
        elif avg_time > 20:
            insights.append("Slow processing times may impact development timelines")

        if change_percentage < -15:
            insights.append("Processing times are improving significantly")
        elif change_percentage > 15:
            insights.append("Processing times are increasing - potential delays ahead")

        return insights

    async def _calculate_market_metrics(
        self,
        applications: List[PlanningApplication],
        segments: List[MarketSegment]
    ) -> Dict[MarketSegment, MarketMetrics]:
        """Calculate market metrics for each segment"""
        metrics = {}

        for segment in segments:
            segment_apps = self._filter_by_segment(applications, segment)

            if not segment_apps:
                continue

            # Calculate metrics
            total_apps = len(segment_apps)

            decided_apps = [app for app in segment_apps if app.status in ["approved", "refused"]]
            approval_rate = len([app for app in decided_apps if app.status == "approved"]) / max(1, len(decided_apps))

            # Processing times
            processing_times = []
            for app in segment_apps:
                if app.date_received and app.decision_date:
                    days = (app.decision_date - app.date_received).days
                    if days > 0:
                        processing_times.append(days)

            avg_processing_time = np.mean(processing_times) if processing_times else 0

            # Development type distribution
            dev_types = Counter(app.development_type for app in segment_apps if app.development_type)
            dominant_types = [
                {"type": dtype, "count": count, "percentage": count/total_apps}
                for dtype, count in dev_types.most_common(5)
            ]

            # Authority performance
            authorities = Counter(app.authority for app in segment_apps if app.authority)
            authority_performance = {
                "total_authorities": len(authorities),
                "most_active": authorities.most_common(1)[0] if authorities else None,
                "distribution": dict(authorities.most_common(5))
            }

            # Geographic distribution (simplified)
            geographical_distribution = {
                "total_locations": len(set(app.address for app in segment_apps if app.address)),
                "concentration": "distributed"  # Would calculate actual geographic concentration
            }

            # Trends
            volume_trend = self._calculate_segment_trend(segment_apps, "volume")
            approval_trend = self._calculate_segment_trend(segment_apps, "approval")

            metrics[segment] = MarketMetrics(
                total_applications=total_apps,
                approval_rate=approval_rate,
                average_processing_time=avg_processing_time,
                application_volume_trend=volume_trend,
                approval_rate_trend=approval_trend,
                dominant_development_types=dominant_types,
                authority_performance=authority_performance,
                geographical_distribution=geographical_distribution
            )

        return metrics

    def _filter_by_segment(self, applications: List[PlanningApplication], segment: MarketSegment) -> List[PlanningApplication]:
        """Filter applications by market segment"""
        segment_keywords = {
            MarketSegment.RESIDENTIAL: ["residential", "housing", "dwelling", "home", "flat", "apartment"],
            MarketSegment.COMMERCIAL: ["commercial", "business", "retail", "shop", "store"],
            MarketSegment.INDUSTRIAL: ["industrial", "warehouse", "manufacturing", "factory"],
            MarketSegment.MIXED_USE: ["mixed", "mixed use", "mixed-use"],
            MarketSegment.RETAIL: ["retail", "shop", "store", "shopping"],
            MarketSegment.OFFICE: ["office", "workplace", "business premises"]
        }

        keywords = segment_keywords.get(segment, [])
        filtered = []

        for app in applications:
            dev_type = (app.development_type or "").lower()
            description = (app.description or "").lower()

            if any(keyword in dev_type or keyword in description for keyword in keywords):
                filtered.append(app)

        return filtered

    def _calculate_segment_trend(self, applications: List[PlanningApplication], metric: str) -> TrendDirection:
        """Calculate trend for a specific segment and metric"""
        if len(applications) < 10:
            return TrendDirection.STABLE

        # Simple trend calculation
        recent_apps = [app for app in applications if app.date_received and
                      app.date_received > datetime.utcnow() - timedelta(days=180)]
        older_apps = [app for app in applications if app.date_received and
                     app.date_received <= datetime.utcnow() - timedelta(days=180)]

        if metric == "volume":
            recent_rate = len(recent_apps) / 6  # Per month
            older_rate = len(older_apps) / max(6, len(older_apps) / 30)  # Rough monthly rate

            if recent_rate > older_rate * 1.1:
                return TrendDirection.INCREASING
            elif recent_rate < older_rate * 0.9:
                return TrendDirection.DECREASING
            else:
                return TrendDirection.STABLE

        elif metric == "approval":
            recent_approved = len([app for app in recent_apps if app.status == "approved"])
            recent_total = len([app for app in recent_apps if app.status in ["approved", "refused"]])

            older_approved = len([app for app in older_apps if app.status == "approved"])
            older_total = len([app for app in older_apps if app.status in ["approved", "refused"]])

            if recent_total > 0 and older_total > 0:
                recent_rate = recent_approved / recent_total
                older_rate = older_approved / older_total

                if recent_rate > older_rate + 0.05:
                    return TrendDirection.INCREASING
                elif recent_rate < older_rate - 0.05:
                    return TrendDirection.DECREASING

        return TrendDirection.STABLE

    async def _analyze_competition(self, applications: List[PlanningApplication]) -> CompetitiveAnalysis:
        """Analyze competitive landscape"""
        # Analyze by applicant/agent (simplified)
        applicants = Counter(app.applicant for app in applications if hasattr(app, 'applicant') and app.applicant)
        agents = Counter(app.agent for app in applications if hasattr(app, 'agent') and app.agent)

        # Market leaders (by application count)
        market_leaders = []
        for entity, count in (applicants + agents).most_common(10):
            success_rate = 0.7  # Would calculate actual success rate
            market_leaders.append({
                "name": entity,
                "applications": count,
                "market_share": count / len(applications),
                "success_rate": success_rate
            })

        # Calculate market concentration (HHI)
        total_apps = len(applications)
        market_shares = [count / total_apps for count in applicants.values()]
        hhi = sum(share ** 2 for share in market_shares)

        # Opportunity gaps (areas with low competition)
        opportunity_gaps = [
            {
                "area": "Small residential developments",
                "opportunity_level": "high",
                "reasoning": "Fragmented market with many small players"
            }
        ]

        # Competitive intensity
        if hhi > 0.25:
            intensity = "high"
        elif hhi > 0.15:
            intensity = "moderate"
        else:
            intensity = "low"

        return CompetitiveAnalysis(
            market_leaders=market_leaders,
            market_concentration=hhi,
            opportunity_gaps=opportunity_gaps,
            competitive_intensity=intensity,
            barriers_to_entry=[
                "Planning expertise required",
                "Local knowledge important",
                "Capital requirements for major developments"
            ],
            success_factors=[
                "Strong planning consultant relationships",
                "Local authority engagement",
                "Community consultation skills",
                "Technical expertise"
            ]
        )

    async def _identify_opportunities(
        self,
        applications: List[PlanningApplication],
        market_metrics: Dict[MarketSegment, MarketMetrics],
        trends: List[TrendAnalysis]
    ) -> List[MarketOpportunity]:
        """Identify market opportunities"""
        opportunities = []

        # High approval rate opportunities
        for segment, metrics in market_metrics.items():
            if metrics.approval_rate > 0.8 and metrics.total_applications > 20:
                opportunities.append(MarketOpportunity(
                    opportunity_id=f"high_approval_{segment.value}",
                    title=f"High Success Rate in {segment.value.title()} Segment",
                    description=f"The {segment.value} segment shows a {metrics.approval_rate:.0%} approval rate",
                    market_size={"applications_per_year": metrics.total_applications * 12},
                    growth_potential=0.8 if metrics.application_volume_trend == TrendDirection.INCREASING else 0.6,
                    competition_level="moderate",
                    barriers=["Planning expertise", "Local knowledge"],
                    success_probability=metrics.approval_rate,
                    recommendations=[
                        f"Focus on {segment.value} developments",
                        "Build expertise in high-success areas",
                        "Develop relationships with successful authorities"
                    ],
                    supporting_data={"approval_rate": metrics.approval_rate, "total_applications": metrics.total_applications}
                ))

        # Growth trend opportunities
        growing_trends = [t for t in trends if t.trend_direction == TrendDirection.INCREASING and t.change_percentage > 15]
        for trend in growing_trends:
            if "volume" in trend.metric:
                opportunities.append(MarketOpportunity(
                    opportunity_id=f"growth_{trend.metric}",
                    title=f"Growing Market in {trend.metric.replace('_', ' ').title()}",
                    description=f"Strong growth trend with {trend.change_percentage:.1f}% increase",
                    market_size={"growth_rate": trend.change_percentage},
                    growth_potential=0.9,
                    competition_level="increasing",
                    barriers=["First mover advantage diminishing"],
                    success_probability=0.7,
                    recommendations=[
                        "Enter market quickly to capture growth",
                        "Scale operations to meet demand",
                        "Invest in capacity building"
                    ],
                    supporting_data={"trend_direction": trend.trend_direction.value, "change_percentage": trend.change_percentage}
                ))

        return opportunities[:5]  # Limit to top 5 opportunities

    async def _assess_market_risks(
        self,
        applications: List[PlanningApplication],
        trends: List[TrendAnalysis]
    ) -> List[Dict[str, Any]]:
        """Assess market risks"""
        risks = []

        # Declining trends
        declining_trends = [t for t in trends if t.trend_direction == TrendDirection.DECREASING]
        for trend in declining_trends:
            risks.append({
                "risk_type": "market_decline",
                "title": f"Declining {trend.metric.replace('_', ' ').title()}",
                "severity": "high" if abs(trend.change_percentage) > 20 else "medium",
                "probability": trend.confidence_score,
                "impact": f"{abs(trend.change_percentage):.1f}% decline",
                "mitigation": [
                    "Diversify into growing segments",
                    "Improve operational efficiency",
                    "Focus on high-success areas"
                ]
            })

        # Low approval rates
        low_approval_authorities = Counter()
        refused_apps = [app for app in applications if app.status == "refused"]
        for app in refused_apps:
            if app.authority:
                low_approval_authorities[app.authority] += 1

        if low_approval_authorities:
            risks.append({
                "risk_type": "approval_difficulty",
                "title": "Challenging Planning Authorities",
                "severity": "medium",
                "probability": 0.7,
                "impact": "Reduced success rates",
                "authorities": dict(low_approval_authorities.most_common(3)),
                "mitigation": [
                    "Avoid high-risk authorities",
                    "Invest in pre-application consultation",
                    "Develop authority-specific strategies"
                ]
            })

        return risks

    async def _generate_recommendations(
        self,
        market_metrics: Dict[MarketSegment, MarketMetrics],
        opportunities: List[MarketOpportunity],
        risks: List[Dict[str, Any]],
        trends: List[TrendAnalysis]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []

        # Market entry recommendations
        best_segments = sorted(
            market_metrics.items(),
            key=lambda x: x[1].approval_rate * x[1].total_applications,
            reverse=True
        )

        if best_segments:
            top_segment = best_segments[0]
            recommendations.append(
                f"Focus on {top_segment[0].value} segment with {top_segment[1].approval_rate:.0%} approval rate"
            )

        # Growth recommendations
        growing_segments = [
            segment for segment, metrics in market_metrics.items()
            if metrics.application_volume_trend == TrendDirection.INCREASING
        ]

        if growing_segments:
            recommendations.append(
                f"Capitalize on growth in {', '.join(s.value for s in growing_segments[:2])} segments"
            )

        # Risk mitigation
        high_risks = [r for r in risks if r.get("severity") == "high"]
        if high_risks:
            recommendations.append("Implement risk mitigation strategies for identified high-severity risks")

        # Opportunity capture
        if opportunities:
            recommendations.append(f"Prioritize {len(opportunities)} identified market opportunities")

        # Operational recommendations
        recommendations.extend([
            "Develop strong relationships with high-performing planning authorities",
            "Invest in pre-application consultation for complex projects",
            "Monitor market trends monthly for strategic adjustments"
        ])

        return recommendations[:7]  # Limit to top 7 recommendations

    def _calculate_data_quality_score(self, applications: List[PlanningApplication]) -> float:
        """Calculate overall data quality score"""
        if not applications:
            return 0.0

        quality_factors = []

        # Completeness
        completeness = self._assess_data_completeness(applications)
        quality_factors.append(completeness)

        # Recency
        recent_count = len([
            app for app in applications
            if app.date_received and app.date_received > datetime.utcnow() - timedelta(days=365)
        ])
        recency_score = recent_count / len(applications)
        quality_factors.append(recency_score)

        # Decision status coverage
        decided_apps = len([app for app in applications if app.status in ["approved", "refused"]])
        decision_coverage = decided_apps / len(applications)
        quality_factors.append(decision_coverage)

        return np.mean(quality_factors)

    def _generate_fallback_report(
        self,
        applications: List[PlanningApplication],
        period: AnalysisPeriod
    ) -> MarketIntelligenceReport:
        """Generate fallback report when analysis fails"""
        logger.warning("Generating fallback market intelligence report")

        return MarketIntelligenceReport(
            analysis_period=period,
            market_overview={"total_applications": len(applications), "status": "limited_analysis"},
            trend_analyses=[],
            market_metrics={},
            competitive_analysis=CompetitiveAnalysis(
                market_leaders=[],
                market_concentration=0.5,
                opportunity_gaps=[],
                competitive_intensity="unknown",
                barriers_to_entry=[],
                success_factors=[]
            ),
            opportunities=[],
            risks=[{"risk_type": "data_limitation", "title": "Limited data available for analysis"}],
            recommendations=["Improve data collection for comprehensive analysis"],
            data_quality_score=0.3,
            generated_at=datetime.utcnow()
        )