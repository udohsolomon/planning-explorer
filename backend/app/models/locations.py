"""
Pydantic models for Location Statistics endpoints
Planning Explorer - Geospatial Statistics
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class LocationStats(BaseModel):
    """
    Location statistics model for geospatial aggregations

    Uses Elasticsearch geo_distance queries to aggregate planning applications
    within a specified radius of a location center point.
    """
    location_name: str = Field(..., description="Human-readable location name")
    location_slug: str = Field(..., description="URL-safe location identifier")
    center_coords: Dict[str, float] = Field(
        ...,
        description="Center point coordinates",
        example={"lat": 51.5074, "lng": -0.1278}
    )
    radius_km: int = Field(
        ...,
        ge=1,
        le=50,
        description="Search radius in kilometers"
    )
    total_applications: int = Field(
        ...,
        description="Total applications within radius (last 12 months)"
    )
    total_applications_all_time: int = Field(
        ...,
        description="Total applications within radius (all time)"
    )
    active_applications: int = Field(
        ...,
        description="Active applications without decision date"
    )
    approval_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Approval rate percentage"
    )
    avg_decision_days: int = Field(
        ...,
        ge=0,
        description="Average days to decision"
    )
    top_sector: Dict[str, Any] = Field(
        ...,
        description="Top application sector/type",
        example={"name": "Residential", "count": 245, "percentage": 45.2}
    )
    top_authority: Dict[str, Any] = Field(
        ...,
        description="Top planning authority in area",
        example={"name": "Westminster", "count": 180, "percentage": 33.2}
    )
    monthly_trend: List[Dict[str, Any]] = Field(
        ...,
        description="Monthly application trend (last 12 months)",
        example=[{
            "month": "2024-01",
            "total": 42,
            "approved": 28,
            "rejected": 10,
            "pending": 4
        }]
    )
    status_breakdown: Dict[str, int] = Field(
        ...,
        description="Applications by status",
        example={"Permitted": 180, "Rejected": 45, "Pending": 87}
    )
    recent_applications: List[str] = Field(
        ...,
        max_items=10,
        description="List of recent application IDs"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LocationStatsResponse(BaseModel):
    """Location statistics response wrapper"""
    success: bool = Field(..., description="Request success status")
    data: LocationStats = Field(..., description="Location statistics data")
    cached: bool = Field(default=False, description="Whether data was served from cache")
