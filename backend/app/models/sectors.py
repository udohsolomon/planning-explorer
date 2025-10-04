"""
Pydantic models for Sector Statistics endpoints
Planning Explorer - Sector Intelligence
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentStats(BaseModel):
    """
    Agent/consultant statistics for sector analysis

    Tracks performance metrics for planning agents and consultants
    working in a specific sector.
    """
    agent_name: str = Field(..., description="Agent or consultant name")
    applications_count: int = Field(..., ge=0, description="Number of applications submitted")
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Approval success rate percentage"
    )
    avg_decision_days: int = Field(
        ...,
        ge=0,
        description="Average days to decision for this agent's applications"
    )


class SectorStats(BaseModel):
    """
    Sector statistics model for industry-specific analytics

    Provides comprehensive statistics for a specific planning sector
    (e.g., residential, commercial, retail) with optional regional filtering.

    Uses Elasticsearch aggregations on app_type field and description
    keyword matching to classify applications by sector.
    """
    sector_name: str = Field(..., description="Human-readable sector name")
    sector_slug: str = Field(..., description="URL-safe sector identifier")
    region: Optional[str] = Field(None, description="UK region filter (e.g., 'london', 'south-east')")
    total_applications: int = Field(
        ...,
        ge=0,
        description="Total applications in sector (last 12 months)"
    )
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall approval rate percentage"
    )
    avg_application_value: Optional[float] = Field(
        None,
        ge=0.0,
        description="Average application value (if available in data)"
    )
    avg_decision_days: int = Field(
        ...,
        ge=0,
        description="Average days to decision for sector"
    )
    top_region: Dict[str, Any] = Field(
        ...,
        description="Most active region for this sector",
        example={"name": "London", "count": 1250, "percentage": 35.5}
    )
    top_authority: Dict[str, Any] = Field(
        ...,
        description="Most active planning authority for this sector",
        example={"name": "Westminster", "count": 420, "percentage": 12.0}
    )
    monthly_trend: List[Dict[str, Any]] = Field(
        ...,
        description="Monthly application trend (last 12 months)",
        example=[{
            "month": "2024-01",
            "total": 320,
            "approved": 245,
            "rejected": 50,
            "pending": 25
        }]
    )
    regional_breakdown: List[Dict[str, Any]] = Field(
        ...,
        description="Applications breakdown by all UK regions",
        example=[{
            "region": "London",
            "count": 1250,
            "percentage": 35.5,
            "approval_rate": 72.3
        }]
    )
    top_authorities: List[Dict[str, Any]] = Field(
        ...,
        description="Top 10 planning authorities for this sector",
        max_items=10,
        example=[{
            "authority": "Westminster",
            "count": 420,
            "percentage": 12.0,
            "approval_rate": 68.5,
            "avg_decision_days": 72
        }]
    )
    top_agents: List[AgentStats] = Field(
        ...,
        description="Top 10 agents/consultants in this sector",
        max_items=10
    )
    recent_applications: List[str] = Field(
        ...,
        max_items=10,
        description="Recent application IDs in this sector"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SectorStatsResponse(BaseModel):
    """Sector statistics response wrapper"""
    success: bool = Field(..., description="Request success status")
    data: SectorStats = Field(..., description="Sector statistics data")
    cached: bool = Field(default=False, description="Whether data was served from cache")
