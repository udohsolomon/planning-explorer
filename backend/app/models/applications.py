"""
Pydantic models for Applications List endpoints
Content Discovery - Phase 1 Week 1
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ApplicationPreview(BaseModel):
    """
    Application preview model for list views
    Matches ApplicationsTable component requirements
    """
    application_id: str = Field(..., description="Unique application identifier")
    reference: str = Field(..., description="Planning reference number")
    address: str = Field(..., description="Site address")
    postcode: Optional[str] = Field(None, description="Site postcode")
    status: str = Field(..., description="Application status")
    app_type: Optional[str] = Field(None, description="Application type")
    start_date: Optional[datetime] = Field(None, description="Application start date")
    decided_date: Optional[datetime] = Field(None, description="Decision date")
    decision_days: Optional[int] = Field(None, description="Days to decision")
    opportunity_score: Optional[int] = Field(None, ge=0, le=100, description="AI opportunity score")
    description: Optional[str] = Field(None, description="Application description")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ApplicationListData(BaseModel):
    """Applications list data container"""
    total: int = Field(..., description="Total number of applications")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Results per page")
    applications: List[ApplicationPreview] = Field(..., description="Application previews")


class ApplicationListResponse(BaseModel):
    """Applications list response wrapper"""
    success: bool = Field(..., description="Request success status")
    data: ApplicationListData = Field(..., description="Applications list data")
