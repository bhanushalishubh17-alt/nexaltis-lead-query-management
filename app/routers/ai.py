from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.models import Query as QueryModel
from app.schemas import LeadScoringResponse, QueryAnalysisRequest, QueryAnalysisResponse, QueryResponse
from app.services.ai_service import analyze_query, update_lead_scoring

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/analyze-query", response_model=QueryAnalysisResponse)
def analyze_customer_query(payload: QueryAnalysisRequest):
    """Analyze raw query text for category, intent, summary, suggested response, and priority."""
    analysis = analyze_query(
        description=payload.description,
        customer_name=payload.customer_name,
        service=payload.service,
    )
    return QueryAnalysisResponse(**analysis.__dict__)


@router.post("/queries/{query_id}/analyze", response_model=QueryResponse)
def analyze_existing_query(query_id: int, db: Session = Depends(get_db)):
    """Re-run AI/NLP analysis for an existing stored query and save the result."""
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    lead = db.query(Lead).filter(Lead.id == query.lead_id).first() if query.lead_id else None
    analysis = analyze_query(
        description=query.description,
        customer_name=query.customer_name,
        service=lead.interested_service if lead else None,
    )

    query.category = analysis.category
    query.intent = analysis.intent
    query.summary = analysis.summary
    query.suggested_response = analysis.suggested_response
    query.ai_provider = analysis.ai_provider

    if lead:
        update_lead_scoring(lead, [item.description for item in lead.queries])

    db.commit()
    db.refresh(query)
    return query


@router.post("/leads/{lead_id}/score", response_model=LeadScoringResponse)
def score_existing_lead(lead_id: int, db: Session = Depends(get_db)):
    """Recalculate lead score and priority from the latest lead and query data."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_lead_scoring(lead, [query.description for query in lead.queries])
    db.commit()
    db.refresh(lead)
    return LeadScoringResponse(
        lead_id=lead.id,
        lead_score=lead.lead_score,
        priority=lead.priority,
    )
