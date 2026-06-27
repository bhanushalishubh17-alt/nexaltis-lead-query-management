from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead, LeadStatus
from app.models import Query as QueryModel
from app.schemas import QueryCreate, QueryListResponse, QueryResponse, StatusUpdate
from app.services.ai_service import analyze_query, update_lead_scoring
from app.services.email_service import send_status_change_notification

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post("", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
def create_query(query_data: QueryCreate, db: Session = Depends(get_db)):
    """Store a new customer query, optionally linked to an existing lead."""
    lead = None
    if query_data.lead_id is not None:
        lead = db.query(Lead).filter(Lead.id == query_data.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Linked lead not found")

    analysis = analyze_query(
        description=query_data.description,
        customer_name=query_data.customer_name,
        service=lead.interested_service if lead else None,
    )
    query = QueryModel(
        customer_name=query_data.customer_name,
        description=query_data.description,
        lead_id=query_data.lead_id,
        status=LeadStatus.NEW,
        category=analysis.category,
        intent=analysis.intent,
        summary=analysis.summary,
        suggested_response=analysis.suggested_response,
        ai_provider=analysis.ai_provider,
    )
    db.add(query)

    if lead:
        query_descriptions = [item.description for item in lead.queries]
        query_descriptions.append(query.description)
        update_lead_scoring(lead, query_descriptions)

    db.commit()
    db.refresh(query)
    return query


@router.get("", response_model=QueryListResponse)
def list_queries(
    customer_name: Optional[str] = Query(
        None, description="Search by customer name (partial match)"
    ),
    status_filter: Optional[LeadStatus] = Query(
        None, alias="status", description="Filter by query status"
    ),
    db: Session = Depends(get_db),
):
    """List all customer queries with optional filters."""
    query = db.query(QueryModel)

    if customer_name:
        query = query.filter(QueryModel.customer_name.ilike(f"%{customer_name}%"))
    if status_filter:
        query = query.filter(QueryModel.status == status_filter)

    queries = query.order_by(QueryModel.query_date.desc()).all()
    return QueryListResponse(total=len(queries), queries=queries)


@router.get("/{query_id}", response_model=QueryResponse)
def get_query(query_id: int, db: Session = Depends(get_db)):
    """Get a single query by ID."""
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query


@router.patch("/{query_id}/status", response_model=QueryResponse)
def update_query_status(
    query_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)
):
    """Update the status of a customer query."""
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    old_status = query.status.value
    query.status = status_update.status
    db.commit()
    db.refresh(query)

    if query.lead_id:
        lead = db.query(Lead).filter(Lead.id == query.lead_id).first()
        if lead:
            lead.status = status_update.status
            update_lead_scoring(lead, [item.description for item in lead.queries])
            db.commit()
            send_status_change_notification(
                recipient_email=lead.email,
                lead_name=lead.name,
                old_status=old_status,
                new_status=query.status.value,
            )

    return query
