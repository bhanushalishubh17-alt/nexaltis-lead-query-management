from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import InterestedService, LeadStatus


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=255)
    interested_service: InterestedService


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    company_name: str
    interested_service: InterestedService
    status: LeadStatus
    lead_score: int
    priority: str
    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    total: int
    leads: list[LeadResponse]


class StatusUpdate(BaseModel):
    status: LeadStatus


class MeetingSchedule(BaseModel):
    meeting_date: date
    meeting_time: time


class QueryCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    lead_id: Optional[int] = None


class QueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: Optional[int] = None
    customer_name: str
    description: str
    query_date: datetime
    status: LeadStatus
    category: Optional[str] = None
    intent: Optional[str] = None
    summary: Optional[str] = None
    suggested_response: Optional[str] = None
    ai_provider: str = "rule_based"


class QueryListResponse(BaseModel):
    total: int
    queries: list[QueryResponse]


class AnalyticsResponse(BaseModel):
    total_leads: int
    converted_leads: int
    conversion_rate: float
    leads_by_status: dict[str, int]
    leads_by_service: dict[str, int]


class QueryAnalysisRequest(BaseModel):
    customer_name: Optional[str] = None
    description: str = Field(..., min_length=1)
    service: Optional[InterestedService] = None


class QueryAnalysisResponse(BaseModel):
    category: str
    intent: str
    summary: str
    suggested_response: str
    lead_score: int
    priority: str
    ai_provider: str


class LeadScoringResponse(BaseModel):
    lead_id: int
    lead_score: int
    priority: str
