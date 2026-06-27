from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterestedService, Lead, LeadStatus
from app.schemas import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    MeetingSchedule,
    StatusUpdate,
)
from app.services.ai_service import update_lead_scoring
from app.services.email_service import send_status_change_notification

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    """Register a new lead with customer and service information."""
    lead = Lead(**lead_data.model_dump(), status=LeadStatus.NEW)
    update_lead_scoring(lead)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("", response_model=LeadListResponse)
def list_leads(
    name: Optional[str] = Query(None, description="Search by lead name (partial match)"),
    company: Optional[str] = Query(None, description="Search by company name (partial match)"),
    service: Optional[InterestedService] = Query(
        None, description="Filter by interested service"
    ),
    db: Session = Depends(get_db),
):
    """List all leads with optional search by name, company, or service."""
    query = db.query(Lead)

    if name:
        query = query.filter(Lead.name.ilike(f"%{name}%"))
    if company:
        query = query.filter(Lead.company_name.ilike(f"%{company}%"))
    if service:
        query = query.filter(Lead.interested_service == service)

    leads = query.order_by(Lead.created_at.desc()).all()
    return LeadListResponse(total=len(leads), leads=leads)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a single lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(
    lead_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)
):
    """Update the status of a lead. Sends email notification on change."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status.value
    lead.status = status_update.status
    update_lead_scoring(lead, [query.description for query in lead.queries])
    db.commit()
    db.refresh(lead)

    send_status_change_notification(
        recipient_email=lead.email,
        lead_name=lead.name,
        old_status=old_status,
        new_status=lead.status.value,
    )
    return lead


@router.patch("/{lead_id}/meeting", response_model=LeadResponse)
def schedule_meeting(
    lead_id: int, meeting: MeetingSchedule, db: Session = Depends(get_db)
):
    """Schedule a meeting for a lead. Automatically sets status to Meeting Scheduled."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status.value
    lead.meeting_date = meeting.meeting_date
    lead.meeting_time = meeting.meeting_time
    lead.status = LeadStatus.MEETING_SCHEDULED
    update_lead_scoring(lead, [query.description for query in lead.queries])
    db.commit()
    db.refresh(lead)

    if old_status != lead.status.value:
        send_status_change_notification(
            recipient_email=lead.email,
            lead_name=lead.name,
            old_status=old_status,
            new_status=lead.status.value,
        )
    return lead
