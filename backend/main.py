import json
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session

from ai.classifier import classify_content
from db.database import create_db_and_tables, get_session
from ingestion.reddit_ingest import fetch_reddit_posts
from ingestion.regulatory_ingest import fetch_regulatory_signals
from ingestion.x_ingest import fetch_x_signals
from models.audit_log import AuditLog
from models.incident import Incident
from services.demo_seed_service import seed_demo_incidents
from services.region_routing_service import regional_context, summarize_regional_patterns
from services.stakeholder_review_service import build_stakeholder_review_matrix_json
from services.audit_service import (
    create_audit_event,
    list_audit_events,
    list_incident_audit_events,
)
from services.incident_service import (
    create_incident_from_reddit_post,
    create_incident_from_signal,
    list_incidents,
    update_incident_status,
)
from services.slack_service import send_slack_alert

load_dotenv()

app = FastAPI(title="AI Customer Trust & Enterprise Assurance Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IncidentUpdate(BaseModel):
    status: str
    analyst_notes: str | None = None


class CustomerTrustIngest(BaseModel):
    customer_name: str = "Demo Customer"
    customer_region: str = "Global"
    customer_segment: str | None = None
    source_type: str = "customer_trust_request"
    title: str
    body: str


def escalation_threshold() -> int:
    try:
        return int(os.getenv("ESCALATION_SEVERITY_THRESHOLD", "8"))
    except Exception:
        return 8


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "ai-customer-trust-assurance-workflow",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-customer-trust-assurance-workflow",
        "escalation_severity_threshold": escalation_threshold(),
    }


@app.post("/scan/reddit")
def scan_reddit(session: Session = Depends(get_session)):
    posts = fetch_reddit_posts(limit=5)
    created_incidents = []
    threshold = escalation_threshold()

    for post in posts:
        analysis = classify_content(
            title=post["title"],
            body=post.get("body", ""),
        )

        incident = create_incident_from_reddit_post(
            session=session,
            post=post,
            analysis=analysis,
        )

        if incident:
            created_incidents.append(incident)

            create_audit_event(
                session=session,
                incident_id=incident.id,
                action="trust_request_created",
                details="Created from Reddit scan. Optional external monitoring import.",
            )

            if incident.should_escalate or incident.severity >= threshold:
                send_slack_alert(incident)
                create_audit_event(
                    session=session,
                    incident_id=incident.id,
                    action="auto_escalation_recommended",
                    details=(
                        f"Imported item met escalation criteria. "
                        f"Severity={incident.severity}, threshold={threshold}."
                    ),
                )

    return {
        "source": "reddit",
        "created": len(created_incidents),
        "incidents": created_incidents,
    }


@app.post("/scan/regulatory")
def scan_regulatory(session: Session = Depends(get_session)):
    signals = fetch_regulatory_signals(limit=10)
    created_incidents = []
    threshold = escalation_threshold()

    for signal in signals:
        analysis = classify_content(
            title=signal["title"],
            body=signal.get("body", ""),
        )

        incident = create_incident_from_signal(
            session=session,
            signal=signal,
            analysis=analysis,
        )

        if incident:
            created_incidents.append(incident)

            create_audit_event(
                session=session,
                incident_id=incident.id,
                action="trust_request_created",
                details="Created from regulatory scan. Optional external monitoring import.",
            )

            if incident.should_escalate or incident.severity >= threshold:
                send_slack_alert(incident)
                create_audit_event(
                    session=session,
                    incident_id=incident.id,
                    action="auto_escalation_recommended",
                    details=(
                        f"Regulatory item met escalation criteria. "
                        f"Severity={incident.severity}, threshold={threshold}."
                    ),
                )

    return {
        "source": "regulatory_monitor",
        "created": len(created_incidents),
        "incidents": created_incidents,
    }


@app.post("/scan/x")
def scan_x(session: Session = Depends(get_session)):
    signals = fetch_x_signals(limit=10)
    created_incidents = []
    threshold = escalation_threshold()

    for signal in signals:
        analysis = classify_content(
            title=signal["title"],
            body=signal.get("body", ""),
        )

        incident = create_incident_from_signal(
            session=session,
            signal=signal,
            analysis=analysis,
        )

        if incident:
            created_incidents.append(incident)

            create_audit_event(
                session=session,
                incident_id=incident.id,
                action="trust_request_created",
                details="Created from X scan. Optional external monitoring import.",
            )

            if incident.should_escalate or incident.severity >= threshold:
                send_slack_alert(incident)
                create_audit_event(
                    session=session,
                    incident_id=incident.id,
                    action="auto_escalation_recommended",
                    details=(
                        f"X item met escalation criteria. "
                        f"Severity={incident.severity}, threshold={threshold}."
                    ),
                )

    return {
        "source": "x",
        "created": len(created_incidents),
        "incidents": created_incidents,
    }


@app.get("/region-insights")
def get_region_insights(session: Session = Depends(get_session)):
    requests = list_incidents(session)
    return {
        "insights": summarize_regional_patterns(requests),
        "message": (
            "Regional insights are generated from the local request history and demo playbooks. "
            "They are intended to front-load likely evidence needs and routing paths for human review."
        ),
    }


@app.post("/customer-requests/ingest", response_model=Incident)
def ingest_customer_request(
    payload: CustomerTrustIngest,
    session: Session = Depends(get_session),
):
    region_info = regional_context(
        region=payload.customer_region,
        jurisdiction=payload.customer_region,
        content=f"{payload.title} {payload.body}",
    )

    analysis = classify_content(title=payload.title, body=payload.body)

    signal = {
        "source": "customer_intake",
        "id": f"manual_{payload.customer_name.lower().replace(' ', '_')}_{payload.customer_region.lower().replace(' ', '_').replace('/', '_')}",
        "url": "https://example.com/customer-intake",
        "source_community": f"Customer Intake / {payload.customer_name}",
        "source_type": payload.source_type,
        "verification_status": "regional_intake_routed",
        "jurisdiction": payload.customer_region,
        "customer_region": region_info["customer_region"],
        "customer_segment": payload.customer_segment,
        "authority": "Regional Customer Trust Intake",
        "compliance_area": "regional_customer_trust_routing",
        "title": payload.title,
        "body": payload.body,
    }

    incident = create_incident_from_signal(session=session, signal=signal, analysis=analysis)

    if not incident:
        raise HTTPException(
            status_code=409,
            detail="A matching customer trust request already exists for this demo customer and region.",
        )

    incident.stakeholder_review_matrix = build_stakeholder_review_matrix_json(
        title=incident.title,
        raw_content=incident.raw_content or "",
        category=incident.category,
        verification_status=incident.verification_status or "",
        escalation_team=incident.escalation_team,
        customer_region=incident.customer_region or "",
        customer_segment=incident.customer_segment or "",
        regional_routing_notes=incident.regional_routing_notes or "",
        should_escalate=incident.should_escalate,
    )
    session.add(incident)
    session.commit()
    session.refresh(incident)

    create_audit_event(
        session=session,
        incident_id=incident.id,
        action="regional_intake_routed",
        details=(
            f"Region={incident.customer_region}. Predicted needs={incident.predicted_regional_needs}. "
            f"Routing notes={incident.regional_routing_notes}"
        ),
    )

    create_audit_event(
        session=session,
        incident_id=incident.id,
        action="stakeholder_review_matrix_generated",
        details="Generated recommended stakeholder review matrix for Legal, Privacy, Security, Product, GTM, and Customer Trust routing.",
    )

    return incident


@app.get("/customer-requests", response_model=list[Incident])
def get_incidents(session: Session = Depends(get_session)):
    return list_incidents(session)


@app.get("/customer-requests/{incident_id}", response_model=Incident)
def get_incident(incident_id: int, session: Session = Depends(get_session)):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Trust request not found")

    return incident


@app.get("/customer-requests/{incident_id}/review-matrix")
def get_incident_review_matrix(
    incident_id: int,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Trust request not found")

    matrix_json = incident.stakeholder_review_matrix or build_stakeholder_review_matrix_json(
        title=incident.title,
        raw_content=incident.raw_content or "",
        category=incident.category,
        verification_status=incident.verification_status or "",
        escalation_team=incident.escalation_team,
        customer_region=incident.customer_region or "",
        customer_segment=incident.customer_segment or "",
        regional_routing_notes=incident.regional_routing_notes or "",
        should_escalate=incident.should_escalate,
    )

    return {"matrix": json.loads(matrix_json)}


@app.patch("/customer-requests/{incident_id}", response_model=Incident)
def patch_incident(
    incident_id: int,
    payload: IncidentUpdate,
    session: Session = Depends(get_session),
):
    existing = session.get(Incident, incident_id)

    if not existing:
        raise HTTPException(status_code=404, detail="Trust request not found")

    previous_status = existing.status

    incident = update_incident_status(
        session=session,
        incident_id=incident_id,
        status=payload.status,
        analyst_notes=payload.analyst_notes,
    )

    if previous_status != payload.status:
        create_audit_event(
            session=session,
            incident_id=incident_id,
            action="status_updated",
            details=f"Status changed from {previous_status} to {payload.status}.",
        )

    if payload.analyst_notes is not None:
        create_audit_event(
            session=session,
            incident_id=incident_id,
            action="analyst_notes_saved",
            details="Analyst notes were updated.",
        )

    return incident


@app.post("/customer-requests/{incident_id}/escalate")
def escalate_incident(
    incident_id: int,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Trust request not found")

    result = send_slack_alert(incident)

    previous_status = incident.status
    incident.status = "escalated"
    session.add(incident)
    session.commit()
    session.refresh(incident)

    create_audit_event(
        session=session,
        incident_id=incident_id,
        action="manual_escalation",
        details=f"Status changed from {previous_status} to escalated.",
    )

    return {
        "incident": incident,
        "slack": result,
    }



@app.post("/demo/seed")
def seed_demo_data(session: Session = Depends(get_session)):
    created = seed_demo_incidents(session)

    return {
        "created": len(created),
        "incidents": created,
    }


@app.post("/demo/reset")
def reset_demo_data(session: Session = Depends(get_session)):
    # Delete child audit rows first, then customer trust request records.
    from sqlmodel import delete
    from models.audit_log import AuditLog

    session.exec(delete(AuditLog))
    session.exec(delete(Incident))
    session.commit()

    return {
        "status": "reset_complete",
        "message": "All local trust requests and audit events were deleted.",
    }


@app.get("/audit", response_model=list[AuditLog])
def get_audit_events(session: Session = Depends(get_session)):
    return list_audit_events(session)


@app.get("/customer-requests/{incident_id}/audit", response_model=list[AuditLog])
def get_incident_audit_events(
    incident_id: int,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Trust request not found")

    return list_incident_audit_events(session, incident_id)
