from typing import Optional

from sqlmodel import Session, select

from models.audit_log import AuditLog


def create_audit_event(
    session: Session,
    action: str,
    incident_id: Optional[int] = None,
    details: Optional[str] = None,
    actor: str = "demo_analyst",
):
    event = AuditLog(
        incident_id=incident_id,
        action=action,
        actor=actor,
        details=details,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


def list_audit_events(session: Session):
    statement = select(AuditLog).order_by(AuditLog.created_at.desc())
    return session.exec(statement).all()


def list_incident_audit_events(session: Session, incident_id: int):
    statement = (
        select(AuditLog)
        .where(AuditLog.incident_id == incident_id)
        .order_by(AuditLog.created_at.desc())
    )
    return session.exec(statement).all()
