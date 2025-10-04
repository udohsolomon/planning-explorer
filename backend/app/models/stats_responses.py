"""
Pydantic Response Models for Content Discovery Stats API
Phase 1 Week 2-3 - Backend Engineer Deliverable

Master Orchestrator: content-discovery-implementation-plan.md
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class MonthlyDataPoint(BaseModel):
    """Single month's data in trend"""
    month: str = Field(..., description="Month in YYYY-MM format")
    total: int = Field(..., description="Total applications")
    permitted: Optional[int] = Field(None, description="Permitted applications")
    approved: Optional[int] = Field(None, description="Approved applications (alternative)")
    rejected: int = Field(0, description="Rejected applications")
    pending: int = Field(0, description="Pending applications")


class SectorBreakdown(BaseModel):
    """Sector statistics breakdown"""
    sector: str = Field(..., description="Sector/use class name")
    count: int = Field(..., description="Number of applications")
    percentage: float = Field(..., description="Percentage of total")


class AuthorityStatsResponse(BaseModel):
    """Authority page statistics response"""
    authority_name: str = Field(..., description="Authority display name")
    authority_slug: Optional[str] = Field(None, description="URL slug")

    # Core metrics
    total_applications_12m: int = Field(..., description="Total last 12 months")
    total_applications_all_time: int = Field(..., description="All-time total")
    approval_rate: float = Field(..., description="Approval rate percentage")
    avg_decision_days: float = Field(..., description="Average decision time in days")
    active_applications: int = Field(..., description="Currently active applications")

    # Breakdowns
    top_sectors: List[SectorBreakdown] = Field(..., description="Top 3 sectors by volume")
    status_breakdown: Dict[str, int] = Field(..., description="Applications by status")
    monthly_trend: List[MonthlyDataPoint] = Field(..., description="12-month trend data")

    # Metadata
    last_updated: Optional[datetime] = Field(None, description="Cache timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "authority_name": "Poole",
                "authority_slug": "poole",
                "total_applications_12m": 1247,
                "total_applications_all_time": 15892,
                "approval_rate": 78.5,
                "avg_decision_days": 42,
                "active_applications": 156,
                "top_sectors": [
                    {"sector": "Householder", "count": 487, "percentage": 39.1},
                    {"sector": "Full", "count": 312, "percentage": 25.0},
                    {"sector": "Listed Building Consent", "count": 128, "percentage": 10.3}
                ],
                "status_breakdown": {
                    "Permitted": 978,
                    "Rejected": 123,
                    "Undecided": 146
                },
                "monthly_trend": []
            }
        }


class AuthorityBreakdown(BaseModel):
    """Authority coverage statistics (for multi-authority locations)"""
    authority: str = Field(..., description="Authority name")
    count: int = Field(..., description="Number of applications")
    avg_decision_days: float = Field(..., description="Average decision days")
    approval_rate: float = Field(..., description="Approval rate percentage")


class LocationStatsResponse(BaseModel):
    """Location page statistics response"""
    location_name: str = Field(..., description="Location display name")
    location_slug: Optional[str] = Field(None, description="URL slug")
    location_type: Optional[str] = Field(None, description="city, town, postcode, region")

    # Core metrics
    total_applications_this_year: int = Field(..., description="Total this year")
    total_applications_all_time: int = Field(..., description="All-time total")
    approval_rate: float = Field(..., description="Approval rate percentage")
    avg_decision_days: float = Field(..., description="Average decision time")

    # Geographic context
    multi_authority: bool = Field(..., description="Spans multiple authorities")
    authority_coverage: List[AuthorityBreakdown] = Field(..., description="Authority breakdown")

    # Breakdowns
    top_sectors: List[SectorBreakdown] = Field(..., description="Top 3 sectors")
    sector_distribution: List[SectorBreakdown] = Field(..., description="Full sector breakdown")
    status_breakdown: Dict[str, int] = Field(..., description="Applications by status")
    monthly_trend: List[MonthlyDataPoint] = Field(..., description="12-month trend")

    # Map data
    heatmap_data: Optional[List[Dict]] = Field(None, description="Geohash grid for heatmap")

    # AI-generated summary (if available)
    ai_summary: Optional[str] = Field(None, description="AI-generated location insights")

    # Metadata
    last_updated: Optional[datetime] = Field(None, description="Cache timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "location_name": "Manchester",
                "location_slug": "manchester",
                "location_type": "city",
                "total_applications_this_year": 3456,
                "total_applications_all_time": 42891,
                "approval_rate": 81.2,
                "avg_decision_days": 38,
                "multi_authority": False,
                "authority_coverage": [
                    {
                        "authority": "Manchester City Council",
                        "count": 3456,
                        "avg_decision_days": 38,
                        "approval_rate": 81.2
                    }
                ],
                "top_sectors": [],
                "sector_distribution": [],
                "status_breakdown": {},
                "monthly_trend": [],
                "heatmap_data": None
            }
        }


class MapMarker(BaseModel):
    """Map marker for location page"""
    application_id: str = Field(..., description="Application UID")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    address: str = Field(..., description="Application address")
    status: str = Field(..., description="Application status")
    opportunity_score: Optional[int] = Field(None, description="AI opportunity score")
    app_type: Optional[str] = Field(None, description="Application type")


class LocationApplicationsResponse(BaseModel):
    """Location applications list with distance sorting"""
    total: int = Field(..., description="Total matching applications")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Results per page")
    applications: List[Dict] = Field(..., description="Application results")

    # Freemium preview limit
    preview_limit: int = Field(3, description="Free tier preview limit")
    requires_upgrade: bool = Field(False, description="Pro subscription required")


class SectorStatsResponse(BaseModel):
    """Sector page statistics response (Phase 2)"""
    sector_name: str = Field(..., description="Sector display name")
    sector_slug: str = Field(..., description="URL slug")

    # UK-wide metrics
    uk_volume: int = Field(..., description="Total UK applications")
    approval_rate: float = Field(..., description="Sector approval rate")
    avg_project_value: Optional[float] = Field(None, description="Average project value")

    # Top performers
    top_authorities: List[AuthorityBreakdown] = Field(..., description="Top 5 authorities")
    top_agents: Optional[List[Dict]] = Field(None, description="Top agents (Pro feature)")

    # Trend data
    trend_data: List[MonthlyDataPoint] = Field(..., description="24-month trend")
    growth_forecast: Optional[str] = Field(None, description="AI growth prediction")

    # AI insights (long-form content 1500-3000 words)
    ai_insights: Optional[str] = Field(None, description="Sector intelligence content")

    class Config:
        json_schema_extra = {
            "example": {
                "sector_name": "Residential",
                "sector_slug": "residential",
                "uk_volume": 125789,
                "approval_rate": 76.8,
                "avg_project_value": None,
                "top_authorities": [],
                "top_agents": None,
                "trend_data": [],
                "growth_forecast": None,
                "ai_insights": None
            }
        }


class TrendsDashboardResponse(BaseModel):
    """Insights Hub dashboard response (Phase 2)"""
    dashboard_type: str = Field(..., description="authorities|regions|sectors|agents")
    date_range: str = Field(..., description="Date range filter")
    data: Dict = Field(..., description="Dashboard-specific data")
    last_updated: datetime = Field(..., description="Data freshness")


class StatsHealthResponse(BaseModel):
    """Stats service health check"""
    status: str = Field(..., description="Service status")
    cache_size: int = Field(..., description="Current cache entries")
    cache_maxsize: int = Field(..., description="Max cache capacity")
    cache_ttl: int = Field(..., description="Cache TTL in seconds")
