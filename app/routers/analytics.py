from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterestedService, Lead, LeadStatus
from app.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """Lead analytics: totals, conversions, and breakdowns by status and service."""
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    converted_leads = (
        db.query(func.count(Lead.id))
        .filter(Lead.status == LeadStatus.CONVERTED)
        .scalar()
        or 0
    )
    conversion_rate = (
        round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0.0
    )

    status_counts = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )
    leads_by_status = {status.value: count for status, count in status_counts}

    for status in LeadStatus:
        if status.value not in leads_by_status:
            leads_by_status[status.value] = 0

    service_counts = (
        db.query(Lead.interested_service, func.count(Lead.id))
        .group_by(Lead.interested_service)
        .all()
    )
    leads_by_service = {service.value: count for service, count in service_counts}

    for service in InterestedService:
        if service.value not in leads_by_service:
            leads_by_service[service.value] = 0

    return AnalyticsResponse(
        total_leads=total_leads,
        converted_leads=converted_leads,
        conversion_rate=conversion_rate,
        leads_by_status=leads_by_status,
        leads_by_service=leads_by_service,
    )
