import enum
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    MEETING_SCHEDULED = "Meeting Scheduled"
    PROPOSAL_SENT = "Proposal Sent"
    CONVERTED = "Converted"
    CLOSED = "Closed"


class InterestedService(str, enum.Enum):
    AI_CHATBOT = "AI Chatbot"
    WEBSITE_DEVELOPMENT = "Website Development"
    MOBILE_APP_DEVELOPMENT = "Mobile App Development"
    DATA_ANALYTICS = "Data Analytics"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    interested_service: Mapped[InterestedService] = mapped_column(
        Enum(InterestedService), nullable=False, index=True
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    lead_score: Mapped[int] = mapped_column(default=0, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="Cold", nullable=False)
    meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    meeting_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    queries: Mapped[list["Query"]] = relationship(
        "Query", back_populates="lead", cascade="all, delete-orphan"
    )


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    query_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_provider: Mapped[str] = mapped_column(String(50), default="rule_based", nullable=False)

    lead: Mapped["Lead | None"] = relationship("Lead", back_populates="queries")
