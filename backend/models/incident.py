from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    source: str
    source_id: str
    source_url: Optional[str] = None
    source_community: Optional[str] = None

    source_type: Optional[str] = None
    verification_status: Optional[str] = None
    jurisdiction: Optional[str] = None
    customer_region: Optional[str] = None
    customer_segment: Optional[str] = None
    regional_request_profile: Optional[str] = None
    predicted_regional_needs: Optional[str] = None
    regional_routing_notes: Optional[str] = None
    stakeholder_review_matrix: Optional[str] = None
    authority: Optional[str] = None
    compliance_area: Optional[str] = None
    effective_date: Optional[str] = None

    title: str
    raw_content: Optional[str] = None

    category: str
    severity: int
    confidence: float
    summary: str
    escalation_team: str
    should_escalate: bool = False

    status: str = "open"
    analyst_notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
