"""
Pydantic models for Planning Explorer matching Elasticsearch schema
"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict
from pydantic import EmailStr


class ApplicationStatus(str, Enum):
    """Planning application status options"""
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    UNDER_CONSIDERATION = "under_consideration"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    APPEALED = "appealed"


class DecisionType(str, Enum):
    """Planning decision types"""
    APPROVED = "approved"
    REFUSED = "refused"
    WITHDRAWN = "withdrawn"
    SPLIT_DECISION = "split_decision"


class DevelopmentType(str, Enum):
    """Development type categories"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    CHANGE_OF_USE = "change_of_use"
    EXTENSION = "extension"
    NEW_BUILD = "new_build"


class ApplicationType(str, Enum):
    """Planning application types"""
    FULL = "full"
    OUTLINE = "outline"
    RESERVED_MATTERS = "reserved_matters"
    HOUSEHOLDER = "householder"
    MINOR = "minor"
    MAJOR = "major"
    LISTED_BUILDING = "listed_building"
    CONSERVATION_AREA = "conservation_area"
    PRE_APPLICATION = "pre_application"
    PRIOR_APPROVAL = "prior_approval"
    CERTIFICATE_LAWFUL = "certificate_lawful"
    ADVERTISEMENT = "advertisement"
    DISCHARGE_CONDITIONS = "discharge_conditions"
    NON_MATERIAL_AMENDMENT = "non_material_amendment"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingStatus(str, Enum):
    """AI processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ======== BASE MODELS ========

class GeoPoint(BaseModel):
    """Geographic point coordinates"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class Applicant(BaseModel):
    """Planning application applicant details"""
    name: str = Field(..., description="Applicant name")
    type: Optional[str] = Field(None, description="Applicant type (individual, company, etc.)")
    address: Optional[str] = Field(None, description="Applicant address")


class Agent(BaseModel):
    """Planning agent details"""
    name: Optional[str] = Field(None, description="Agent name")
    company: Optional[str] = Field(None, description="Agent company")
    contact: Optional[str] = Field(None, description="Agent contact information")


class Document(BaseModel):
    """Planning application document"""
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    type: str = Field(..., description="Document type")
    url: Optional[str] = Field(None, description="Document URL")
    upload_date: Optional[datetime] = Field(None, description="Upload date")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_extracted: Optional[str] = Field(None, description="Extracted text content")


class Consultation(BaseModel):
    """Consultation response"""
    consultee: str = Field(..., description="Name of consultee")
    response: str = Field(..., description="Response type (support, object, etc.)")
    comment: Optional[str] = Field(None, description="Consultation comment")
    date: Optional[datetime] = Field(None, description="Response date")


class PublicComments(BaseModel):
    """Public comment statistics"""
    total_comments: int = Field(0, description="Total number of comments")
    support_count: int = Field(0, description="Number of supporting comments")
    objection_count: int = Field(0, description="Number of objection comments")
    neutral_count: int = Field(0, description="Number of neutral comments")


class OpportunityBreakdown(BaseModel):
    """AI opportunity score breakdown"""
    approval_probability: float = Field(..., ge=0, le=1, description="Probability of approval")
    market_potential: float = Field(..., ge=0, le=1, description="Market potential score")
    project_viability: float = Field(..., ge=0, le=1, description="Project viability score")
    strategic_fit: float = Field(..., ge=0, le=1, description="Strategic fit score")
    timeline_score: float = Field(..., ge=0, le=1, description="Timeline score")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score")


class PredictedTimeline(BaseModel):
    """AI predicted timeline"""
    decision_weeks: Optional[int] = Field(None, description="Predicted weeks to decision")
    completion_months: Optional[int] = Field(None, description="Predicted months to completion")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")


class RiskAssessment(BaseModel):
    """AI risk assessment"""
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    mitigation_suggestions: Optional[str] = Field(None, description="Risk mitigation suggestions")


class DocumentEmbedding(BaseModel):
    """Document vector embedding"""
    document_id: str = Field(..., description="Document identifier")
    embedding: List[float] = Field(..., description="Vector embedding")
    content_type: str = Field(..., description="Content type")


class SimilarApplication(BaseModel):
    """Similar application reference"""
    application_id: str = Field(..., description="Application ID")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score")
    similarity_type: str = Field(..., description="Type of similarity")


class AIProcessing(BaseModel):
    """AI processing metadata"""
    last_processed: Optional[datetime] = Field(None, description="Last processing timestamp")
    model_version: Optional[str] = Field(None, description="AI model version")
    processing_status: ProcessingStatus = Field(ProcessingStatus.PENDING, description="Processing status")
    human_reviewed: bool = Field(False, description="Human review flag")
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    processing_duration: Optional[float] = Field(None, description="Processing duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class UserMetrics(BaseModel):
    """User engagement metrics"""
    view_count: int = Field(0, description="Number of views")
    save_count: int = Field(0, description="Number of saves")
    share_count: int = Field(0, description="Number of shares")
    last_viewed: Optional[datetime] = Field(None, description="Last view timestamp")
    popularity_score: float = Field(0.0, description="Popularity score")


class PlanningHistory(BaseModel):
    """Historical planning application"""
    reference: str = Field(..., description="Planning reference")
    decision: str = Field(..., description="Decision outcome")
    decision_date: Optional[datetime] = Field(None, description="Decision date")
    description: str = Field(..., description="Application description")


class Constraints(BaseModel):
    """Planning constraints and designations"""
    conservation_area: bool = Field(False, description="In conservation area")
    listed_building: Optional[str] = Field(None, description="Listed building grade")
    green_belt: bool = Field(False, description="In green belt")
    flood_zone: Optional[str] = Field(None, description="Flood zone designation")
    tree_preservation: bool = Field(False, description="Tree preservation order")
    article_4_direction: bool = Field(False, description="Article 4 direction")
    other_constraints: List[str] = Field(default_factory=list, description="Other constraints")


class DataSource(BaseModel):
    """Data source tracking"""
    portal_url: Optional[str] = Field(None, description="Source portal URL")
    scrape_date: Optional[datetime] = Field(None, description="Data scrape date")
    data_quality_score: float = Field(0.0, ge=0, le=1, description="Data quality score")
    completeness_score: float = Field(0.0, ge=0, le=1, description="Data completeness score")


# ======== MAIN PLANNING APPLICATION MODEL ========

class PlanningApplication(BaseModel):
    """Complete planning application model matching Elasticsearch schema"""

    # Core fields
    application_id: str = Field(..., description="Unique application identifier")
    reference: str = Field(..., description="Planning reference number")
    authority: str = Field(..., description="Planning authority")
    authority_code: Optional[str] = Field(None, description="Authority code")

    # Address and location
    address: str = Field(..., description="Site address")
    postcode: Optional[str] = Field(None, description="Site postcode")
    location: Optional[GeoPoint] = Field(None, description="Geographic coordinates")
    ward: Optional[str] = Field(None, description="Electoral ward")
    ward_name: Optional[str] = Field(None, description="Ward name from other_fields")
    parish: Optional[str] = Field(None, description="Parish")

    # Status and dates
    status: ApplicationStatus = Field(..., description="Application status")
    status_category: Optional[str] = Field(None, description="Status category")
    decision: Optional[DecisionType] = Field(None, description="Decision outcome")
    submission_date: Optional[datetime] = Field(None, description="Submission date")
    validation_date: Optional[datetime] = Field(None, description="Validation date")
    consultation_start_date: Optional[datetime] = Field(None, description="Consultation start")
    consultation_end_date: Optional[datetime] = Field(None, description="Consultation end")
    target_decision_date: Optional[datetime] = Field(None, description="Target decision date")
    decision_date: Optional[datetime] = Field(None, description="Actual decision date")
    decided_date: Optional[datetime] = Field(None, description="Decided date from other_fields")
    appeal_date: Optional[datetime] = Field(None, description="Appeal date")
    n_statutory_days: Optional[int] = Field(None, description="Number of statutory days")

    # Development details
    development_type: Optional[DevelopmentType] = Field(None, description="Type of development")
    application_type: Optional[ApplicationType] = Field(None, description="Application type")
    use_class: Optional[str] = Field(None, description="Use class")
    description: str = Field(..., description="Development description")
    proposal: Optional[str] = Field(None, description="Proposal details")

    # Project scale
    project_value: Optional[float] = Field(None, description="Project value in GBP")
    floor_area: Optional[int] = Field(None, description="Floor area in sqm")
    site_area: Optional[float] = Field(None, description="Site area in hectares")
    num_units: Optional[int] = Field(None, description="Number of units")
    num_bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    building_height: Optional[float] = Field(None, description="Building height in meters")
    parking_spaces: Optional[int] = Field(None, description="Number of parking spaces")

    # People
    applicant: Optional[Applicant] = Field(None, description="Applicant details")
    agent: Optional[Agent] = Field(None, description="Agent details")
    planning_officer: Optional[str] = Field(None, description="Planning officer")
    committee_date: Optional[datetime] = Field(None, description="Committee date")

    # URLs (for enrichment)
    url: Optional[str] = Field(None, description="Planning portal application URL")
    link: Optional[str] = Field(None, description="Alternative link/URL")
    source_url: Optional[str] = Field(None, description="Source portal URL")
    docs_url: Optional[str] = Field(None, description="Documents URL from other_fields")

    # Documents and consultations
    documents: List[Document] = Field(default_factory=list, description="Application documents")
    n_documents: Optional[int] = Field(None, description="Number of documents from other_fields")
    consultations: List[Consultation] = Field(default_factory=list, description="Consultation responses")
    public_comments: Optional[PublicComments] = Field(None, description="Public comment statistics")

    # AI enhancements
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    opportunity_score: Optional[int] = Field(None, ge=0, le=100, description="Opportunity score")
    opportunity_breakdown: Optional[OpportunityBreakdown] = Field(None, description="Opportunity breakdown")
    opportunity_rationale: Optional[str] = Field(None, description="Opportunity rationale")
    market_insights: Optional[str] = Field(None, description="Market insights")
    approval_probability: Optional[float] = Field(None, ge=0, le=1, description="Approval probability")
    predicted_timeline: Optional[PredictedTimeline] = Field(None, description="Predicted timeline")
    risk_assessment: Optional[RiskAssessment] = Field(None, description="Risk assessment")
    risk_flags: List[str] = Field(default_factory=list, description="Risk flags")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")

    # Vector embeddings (not included in API responses by default)
    description_embedding: Optional[List[float]] = Field(None, exclude=True)
    full_content_embedding: Optional[List[float]] = Field(None, exclude=True)
    summary_embedding: Optional[List[float]] = Field(None, exclude=True)
    location_embedding: Optional[List[float]] = Field(None, exclude=True)

    # Related data
    document_embeddings: List[DocumentEmbedding] = Field(default_factory=list, exclude=True)
    similar_applications: List[SimilarApplication] = Field(default_factory=list, description="Similar applications")
    planning_history: List[PlanningHistory] = Field(default_factory=list, description="Planning history")
    constraints: Optional[Constraints] = Field(None, description="Planning constraints")

    # Metadata
    ai_processing: Optional[AIProcessing] = Field(None, description="AI processing metadata")
    user_metrics: Optional[UserMetrics] = Field(None, description="User engagement metrics")
    data_source: Optional[DataSource] = Field(None, description="Data source information")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    indexed_at: Optional[datetime] = Field(None, description="Elasticsearch index timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ======== REQUEST/RESPONSE MODELS ========

class PlanningApplicationResponse(BaseModel):
    """API response model for planning applications"""

    # Essential fields for API responses
    application_id: str
    reference: str
    authority: str
    address: str
    postcode: Optional[str]
    location: Optional[GeoPoint]
    status: ApplicationStatus
    decision: Optional[DecisionType]
    submission_date: Optional[datetime]
    decision_date: Optional[datetime]
    development_type: Optional[DevelopmentType]
    application_type: Optional[ApplicationType]
    description: str
    proposal: Optional[str]

    # AI enhancements
    opportunity_score: Optional[int]
    approval_probability: Optional[float]
    ai_summary: Optional[str]
    market_insights: Optional[str]

    # Metrics
    public_comments: Optional[PublicComments]
    similar_applications: List[SimilarApplication]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlanningApplicationSummary(BaseModel):
    """Minimal planning application model for search results"""

    # Core identifiers (snake_case for consistency)
    application_id: str = Field(..., description="Application ID")
    reference: Optional[str] = Field(None, description="Planning reference")
    uid: Optional[str] = Field(None, description="Unique identifier from source")
    name: Optional[str] = Field(None, description="Application name")

    # Authority and area info
    authority: Optional[str] = Field(None, description="Planning authority")
    area_id: Optional[int] = Field(None, description="Area ID")
    area_name: Optional[str] = Field(None, description="Area name")
    scraper_name: Optional[str] = Field(None, description="Scraper name")

    # Location
    address: Optional[str] = Field(None, description="Site address")
    postcode: Optional[str] = Field(None, description="Site postcode")
    location: Optional[GeoPoint] = Field(None, description="Geographic coordinates")
    location_x: Optional[float] = Field(None, description="Longitude")
    location_y: Optional[float] = Field(None, description="Latitude")

    # Application details
    app_size: Optional[str] = Field(None, description="Application size (Small, Medium, Large)")
    app_state: Optional[str] = Field(None, description="Application state")
    app_type: Optional[str] = Field(None, description="Application type")
    status: Optional[ApplicationStatus] = Field(None, description="Application status")
    decision: Optional[DecisionType] = Field(None, description="Decision outcome")

    # Dates
    submission_date: Optional[datetime] = Field(None, description="Submission date")
    start_date: Optional[datetime] = Field(None, description="Start date")
    decided_date: Optional[datetime] = Field(None, description="Decision date")
    consulted_date: Optional[datetime] = Field(None, description="Consultation date")
    last_changed: Optional[datetime] = Field(None, description="Last changed timestamp")
    last_different: Optional[datetime] = Field(None, description="Last different timestamp")
    last_scraped: Optional[datetime] = Field(None, description="Last scraped timestamp")

    # Description and classification
    development_type: Optional[DevelopmentType] = Field(None, description="Development type")
    description: Optional[str] = Field(None, description="Development description")

    # URLs and links
    link: Optional[str] = Field(None, description="Primary link")
    url: Optional[str] = Field(None, description="Application URL")

    # Associated data
    associated_id: Optional[str] = Field(None, description="Associated application ID")
    altid: Optional[str] = Field(None, description="Alternative ID")

    # Other fields (nested object from ES)
    applicant_name: Optional[str] = Field(None, description="Applicant name")
    applicant_address: Optional[str] = Field(None, description="Applicant address")
    application_type: Optional[str] = Field(None, description="Application type from other_fields")
    case_officer: Optional[str] = Field(None, description="Case officer")
    comment_url: Optional[str] = Field(None, description="Public comment URL")
    consultation_end_date: Optional[datetime] = Field(None, description="Consultation end date")
    date_received: Optional[datetime] = Field(None, description="Date received")
    date_validated: Optional[datetime] = Field(None, description="Date validated")
    easting: Optional[float] = Field(None, description="Easting coordinate")
    northing: Optional[float] = Field(None, description="Northing coordinate")
    lat: Optional[float] = Field(None, description="Latitude from other_fields")
    lng: Optional[float] = Field(None, description="Longitude from other_fields")
    map_url: Optional[str] = Field(None, description="Map URL")
    n_documents: Optional[int] = Field(None, description="Number of documents")
    n_statutory_days: Optional[int] = Field(None, description="Number of statutory days")
    docs_url: Optional[str] = Field(None, description="Documents URL")
    ward_name: Optional[str] = Field(None, description="Ward name")
    source_url: Optional[str] = Field(None, description="Source portal URL")
    status_other_fields: Optional[str] = Field(None, description="Status from other_fields")

    # AI enhancements
    opportunity_score: Optional[int] = Field(None, description="AI opportunity score")
    approval_probability: Optional[float] = Field(None, description="Approval probability")
    similarity_score: Optional[float] = Field(None, description="Semantic similarity score")

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,  # Allow both field name and alias for input
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SearchFilters(BaseModel):
    """Search filter model"""

    authorities: Optional[List[str]] = Field(None, description="Planning authorities")
    statuses: Optional[List[ApplicationStatus]] = Field(None, description="Application statuses")
    development_types: Optional[List[DevelopmentType]] = Field(None, description="Development types")
    application_types: Optional[List[ApplicationType]] = Field(None, description="Application types")
    decisions: Optional[List[DecisionType]] = Field(None, description="Decision outcomes")

    # Date ranges
    submission_date_from: Optional[datetime] = Field(None, description="Submission date from")
    submission_date_to: Optional[datetime] = Field(None, description="Submission date to")
    decision_date_from: Optional[datetime] = Field(None, description="Decision date from")
    decision_date_to: Optional[datetime] = Field(None, description="Decision date to")

    # Numeric ranges
    opportunity_score_min: Optional[int] = Field(None, ge=0, le=100, description="Minimum opportunity score")
    opportunity_score_max: Optional[int] = Field(None, ge=0, le=100, description="Maximum opportunity score")
    approval_probability_min: Optional[float] = Field(None, ge=0, le=1, description="Minimum approval probability")
    approval_probability_max: Optional[float] = Field(None, ge=0, le=1, description="Maximum approval probability")
    project_value_min: Optional[float] = Field(None, description="Minimum project value")
    project_value_max: Optional[float] = Field(None, description="Maximum project value")

    # Geographic
    postcode: Optional[str] = Field(None, description="Postcode filter")
    ward: Optional[str] = Field(None, description="Ward filter")

    # Location radius search
    lat: Optional[float] = Field(None, description="Latitude for radius search")
    lon: Optional[float] = Field(None, description="Longitude for radius search")
    radius_km: Optional[float] = Field(None, description="Search radius in kilometers")


class SearchRequest(BaseModel):
    """Search request model"""

    query: Optional[str] = Field(None, description="Search query text")
    filters: Optional[SearchFilters] = Field(None, description="Search filters")
    sort_by: Optional[str] = Field("relevance", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Results per page")
    include_ai_fields: bool = Field(True, description="Include AI-generated fields")


class SearchResponse(BaseModel):
    """Search response model"""

    results: List[PlanningApplicationSummary]
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Results per page")
    total_pages: int = Field(..., description="Total number of pages")
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Search aggregations")
    took_ms: int = Field(..., description="Query execution time in milliseconds")

    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        total = values.get('total', 0)
        page_size = values.get('page_size', 20)
        return (total + page_size - 1) // page_size if total > 0 else 0