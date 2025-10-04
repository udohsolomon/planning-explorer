"""
Pydantic models for Trends Dashboard endpoints
Planning Explorer - Insights Hub Trends
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LeagueTableRow(BaseModel):
    """
    League table row representing an entity's ranking and statistics

    Used for authorities, regions, sectors, and agents leaderboards
    """
    rank: int = Field(..., ge=1, description="Ranking position (1-indexed)")
    name: str = Field(..., description="Entity name (authority, region, sector, or agent)")
    slug: str = Field(..., description="URL-safe identifier")
    total_applications: int = Field(..., ge=0, description="Total applications in period")
    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of total applications"
    )
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Approval/success rate percentage"
    )
    avg_decision_days: int = Field(
        ...,
        ge=0,
        description="Average days to decision"
    )
    trend: str = Field(
        ...,
        description="Trend indicator: 'up', 'down', or 'stable'",
        pattern="^(up|down|stable)$"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "name": "Westminster",
                "slug": "westminster",
                "total_applications": 1250,
                "percentage": 8.5,
                "success_rate": 72.3,
                "avg_decision_days": 45,
                "trend": "up"
            }
        }


class TrendsOverview(BaseModel):
    """
    Overview statistics for trends dashboard

    Provides high-level metrics for the selected period
    """
    total_applications: int = Field(
        ...,
        ge=0,
        description="Total applications in the period"
    )
    approval_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall approval rate percentage"
    )
    avg_decision_days: int = Field(
        ...,
        ge=0,
        description="Average days to decision across all applications"
    )
    active_applications: int = Field(
        ...,
        ge=0,
        description="Currently active applications (no decision)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_applications": 15000,
                "approval_rate": 68.5,
                "avg_decision_days": 52,
                "active_applications": 3200
            }
        }


class TrendsData(BaseModel):
    """
    Complete trends data including overview, monthly trend, and league table

    Used for all dashboard types: authorities, regions, sectors, agents
    """
    type: str = Field(
        ...,
        description="Dashboard type: 'authorities', 'regions', 'sectors', or 'agents'",
        pattern="^(authorities|regions|sectors|agents)$"
    )
    overview: TrendsOverview = Field(
        ...,
        description="Overview statistics for the period"
    )
    monthly_trend: List[Dict[str, Any]] = Field(
        ...,
        description="12-month trend data with totals, approvals, rejections",
        max_items=24  # Allow up to 24 months for custom date ranges
    )
    league_table: List[LeagueTableRow] = Field(
        ...,
        description="Ranked list of entities with statistics and trends",
        max_items=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "authorities",
                "overview": {
                    "total_applications": 15000,
                    "approval_rate": 68.5,
                    "avg_decision_days": 52,
                    "active_applications": 3200
                },
                "monthly_trend": [
                    {
                        "month": "2024-01",
                        "total": 1250,
                        "approved": 850,
                        "rejected": 280,
                        "pending": 120
                    },
                    {
                        "month": "2024-02",
                        "total": 1180,
                        "approved": 790,
                        "rejected": 260,
                        "pending": 130
                    }
                ],
                "league_table": [
                    {
                        "rank": 1,
                        "name": "Westminster",
                        "slug": "westminster",
                        "total_applications": 1250,
                        "percentage": 8.5,
                        "success_rate": 72.3,
                        "avg_decision_days": 45,
                        "trend": "up"
                    },
                    {
                        "rank": 2,
                        "name": "Birmingham",
                        "slug": "birmingham",
                        "total_applications": 1180,
                        "percentage": 8.0,
                        "success_rate": 65.8,
                        "avg_decision_days": 58,
                        "trend": "stable"
                    }
                ]
            }
        }


class TrendsResponse(BaseModel):
    """Trends data response wrapper"""
    success: bool = Field(..., description="Request success status")
    data: TrendsData = Field(..., description="Trends dashboard data")
    cached: bool = Field(default=False, description="Whether data was served from cache")
