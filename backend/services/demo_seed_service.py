from sqlmodel import Session

from models.incident import Incident
from services.audit_service import create_audit_event
from services.incident_service import incident_exists
from services.region_routing_service import regional_context
from services.stakeholder_review_service import build_stakeholder_review_matrix_json


DEMO_INCIDENTS = [
    {
        "source": "customer_success",
        "source_id": "demo_bank_questionnaire_001",
        "source_url": "https://example.com/customer-security-questionnaire",
        "source_community": "Customer Success / Financial Services Prospect",
        "source_type": "security_questionnaire",
        "verification_status": "approved_answer_bank_available",
        "jurisdiction": "US",
        "customer_region": "US / Financial Services",
        "customer_segment": "Large bank / regulated enterprise",
        "authority": "Enterprise Customer Diligence",
        "compliance_area": "security_questionnaire_customer_trust",
        "title": "Large bank questionnaire asks about encryption, data residency, and dedicated storage",
        "raw_content": (
            "A strategic financial services prospect submitted a security questionnaire asking for details "
            "on encryption in transit and at rest, customer data segregation, data retention, cloud hosting, "
            "and whether dedicated storage configurations are available for enterprise customers."
        ),
        "category": "security_questionnaire",
        "severity": 7,
        "confidence": 0.91,
        "summary": (
            "High-priority customer trust request with reusable answer-bank coverage for standard controls. "
            "Regional history suggests US financial services customers frequently need SOC 2, CAIQ, encryption, "
            "access control, retention, and dedicated-storage evidence paths before deal support can move quickly."
        ),
        "escalation_team": "field_security_grc_security_privacy_customer_success",
        "should_escalate": True,
    },
    {
        "source": "regional_customer_intake",
        "source_id": "demo_japan_enterprise_001",
        "source_url": "https://example.com/japan-customer-intake",
        "source_community": "Japan GTM / Enterprise Prospect",
        "source_type": "regional_customer_intake",
        "verification_status": "regional_playbook_available",
        "jurisdiction": "Japan / APAC",
        "customer_region": "Japan / APAC",
        "customer_segment": "Japan enterprise customer",
        "authority": "Regional Customer Trust Intake",
        "compliance_area": "regional_customer_trust_routing",
        "title": "Japan enterprise prospect asks about data residency, local language docs, and dedicated storage",
        "raw_content": (
            "Japan-based enterprise prospect asks whether data can be hosted or segregated regionally, whether "
            "dedicated customer storage configurations are available, whether subprocessor and cross-border transfer "
            "language is available, and whether customer-facing security documentation can be shared in a localized format."
        ),
        "category": "regional_customer_trust_routing",
        "severity": 8,
        "confidence": 0.9,
        "summary": (
            "Region-specific intake signal. Prior APAC/Japan-style requests suggest the team should front-load localized "
            "security documentation, data residency language, subprocessor/cross-border transfer language, and Product/Security "
            "review before committing to dedicated storage or hosting claims."
        ),
        "escalation_team": "security_privacy_product_apac_gtm",
        "should_escalate": True,
    },
    {
        "source": "regional_customer_intake",
        "source_id": "demo_eu_privacy_diligence_001",
        "source_url": "https://example.com/eu-customer-intake",
        "source_community": "EU GTM / Regulated Prospect",
        "source_type": "regional_customer_intake",
        "verification_status": "regional_playbook_available",
        "jurisdiction": "EU / EEA",
        "customer_region": "EU / EEA",
        "customer_segment": "EU regulated enterprise customer",
        "authority": "Regional Customer Trust Intake",
        "compliance_area": "regional_customer_trust_routing",
        "title": "EU prospect asks about DPA, subprocessors, retention, deletion, and AI/data use boundaries",
        "raw_content": (
            "EU prospect requests DPA language, subprocessor list, SCCs, retention and deletion commitments, and a clear "
            "customer-facing explanation of model/data use boundaries for a regulated product workflow."
        ),
        "category": "regional_customer_trust_routing",
        "severity": 8,
        "confidence": 0.89,
        "summary": (
            "EU/EEA request pattern detected. The workflow should front-load Privacy and Legal review, DPA/subprocessor/SCC "
            "evidence, retention/deletion language, and Product review for any AI/data use boundary claims."
        ),
        "escalation_team": "legal_privacy_product_security_eu",
        "should_escalate": True,
    },
    {
        "source": "field_security",
        "source_id": "demo_caiq_trust_center_001",
        "source_url": "https://cloudsecurityalliance.org/research/cloud-controls-matrix",
        "source_community": "Field Security / Trust Center",
        "source_type": "standardized_questionnaire_artifact",
        "verification_status": "customer_facing_artifact_candidate",
        "jurisdiction": "Global",
        "customer_region": "Global",
        "customer_segment": "Enterprise SaaS customers",
        "authority": "Cloud Security Alliance",
        "compliance_area": "caiq_trust_center_content",
        "title": "Operationalize CAIQ as reusable Trust Center artifact",
        "raw_content": (
            "The Field Security team wants to publish a completed Cloud Security Alliance CAIQ in the Trust Center "
            "to reduce repetitive customer diligence requests and support enterprise deal cycles."
        ),
        "category": "trust_center_artifact",
        "severity": 6,
        "confidence": 0.88,
        "summary": (
            "Reusable trust artifact opportunity. The CAIQ should be mapped to approved evidence sources such as "
            "SOC 2 Type 2, ISO 27001, security policies, and control owner review before publication."
        ),
        "escalation_team": "grc_field_security_legal",
        "should_escalate": False,
    },
    {
        "source": "customer_success",
        "source_id": "demo_customer_architecture_diligence_001",
        "source_url": "https://example.com/customer-architecture-diligence",
        "source_community": "Customer Success / Enterprise Architecture Review",
        "source_type": "customer_architecture_question",
        "verification_status": "requires_cross_functional_review",
        "jurisdiction": "Japan / APAC",
        "customer_region": "Japan / APAC",
        "customer_segment": "Enterprise customer with dedicated architecture questions",
        "authority": "Customer-Facing Claims Review",
        "compliance_area": "customer_architecture_diligence",
        "title": "Enterprise customer asks about dedicated storage, data segregation, and customer-specific controls",
        "raw_content": (
            "Customer Success received a follow-up from an enterprise prospect asking whether dedicated customer storage, "
            "strong data segregation, custom retention commitments, and customer-specific architecture options are available. "
            "The team needs accurate customer-facing language that explains what is standard, what is configurable, and what "
            "requires Security, Privacy, Product, or GTM review."
        ),
        "category": "customer_architecture_diligence",
        "severity": 8,
        "confidence": 0.87,
        "summary": (
            "Customer-specific architecture diligence requiring careful routing. Standard security controls can use approved "
            "answer-bank content, but dedicated storage, data segregation, retention, and customer-specific commitments should "
            "be validated by Security, Privacy, Product, and regional GTM before being stated externally."
        ),
        "escalation_team": "security_privacy_product_customer_success_apac_gtm",
        "should_escalate": True,
    },
    {
        "source": "legal_privacy",
        "source_id": "demo_privacy_policy_update_001",
        "source_url": "https://example.com/privacy-policy-review",
        "source_community": "Legal / Privacy",
        "source_type": "public_policy_update",
        "verification_status": "draft_requires_review",
        "jurisdiction": "Global",
        "customer_region": "Global",
        "customer_segment": "Public / customer-facing content",
        "authority": "External Policy Governance",
        "compliance_area": "privacy_policy_customer_facing_claims",
        "title": "Privacy policy and customer FAQ language need evidence-backed review",
        "raw_content": (
            "Legal and Privacy requested review of public-facing policy language and customer FAQ responses to ensure "
            "they accurately describe data collection, use, retention, subprocessors, customer controls, and security practices."
        ),
        "category": "privacy_policy_customer_facing_content",
        "severity": 7,
        "confidence": 0.9,
        "summary": (
            "Customer-facing policy language should be checked against internal data handling processes, approved privacy "
            "positions, and supporting control evidence before publication or reuse in customer diligence."
        ),
        "escalation_team": "legal_privacy_security_grc",
        "should_escalate": True,
    },
    {
        "source": "sales",
        "source_id": "demo_unsupported_claim_001",
        "source_url": "https://example.com/deal-desk-request",
        "source_community": "Sales / Deal Desk",
        "source_type": "customer_claim_review",
        "verification_status": "unsupported_claim_detected",
        "jurisdiction": "Global",
        "customer_region": "Global",
        "customer_segment": "Enterprise SaaS customer",
        "authority": "Customer-Facing Claims Review",
        "compliance_area": "external_claims_substantiation",
        "title": "Deal request includes broad security claim that needs review before external use",
        "raw_content": (
            "A proposed customer response says the product provides zero data retention for all customers and all product tiers. "
            "The statement may be broader than approved product behavior and requires evidence before it can be sent."
        ),
        "category": "unsupported_external_claim",
        "severity": 9,
        "confidence": 0.94,
        "summary": (
            "Potential unsupported external claim. Do not send as written. Route to Product, Security, Legal, and Privacy "
            "to confirm the accurate customer-facing position and update the answer bank if needed."
        ),
        "escalation_team": "legal_product_security_privacy",
        "should_escalate": True,
    },
    {
        "source": "trust_center",
        "source_id": "demo_soc2_evidence_mapping_001",
        "source_url": "https://example.com/soc2-type-2-report",
        "source_community": "GRC / Trust Center",
        "source_type": "evidence_mapping",
        "verification_status": "approved_evidence_available",
        "jurisdiction": "Global",
        "customer_region": "US / Financial Services",
        "customer_segment": "Regulated enterprise customers",
        "authority": "SOC 2 Type 2",
        "compliance_area": "evidence_mapping_assurance_artifact",
        "title": "Map SOC 2 Type 2 evidence to recurring customer security questions",
        "raw_content": (
            "Recurring customer questions on access reviews, change management, vulnerability management, vendor risk, "
            "and incident response can be answered using approved SOC 2 Type 2 report sections and internal evidence paths."
        ),
        "category": "evidence_mapping",
        "severity": 5,
        "confidence": 0.89,
        "summary": (
            "Good candidate for reusable content. Map recurring questions to SOC 2 Type 2 sections, approved summaries, "
            "and evidence owners to reduce one-off work while keeping responses supportable."
        ),
        "escalation_team": "grc_field_security_customer_success",
        "should_escalate": False,
    },
]


def seed_demo_incidents(session: Session):
    created = []

    for item in DEMO_INCIDENTS:
        if incident_exists(session, item["source"], item["source_id"]):
            continue

        region_info = regional_context(
            region=item.get("customer_region"),
            jurisdiction=item.get("jurisdiction"),
            content=f"{item.get('title', '')} {item.get('raw_content', '')}",
        )

        incident = Incident(
            source=item["source"],
            source_id=item["source_id"],
            source_url=item.get("source_url"),
            source_community=item.get("source_community"),
            source_type=item.get("source_type"),
            verification_status=item.get("verification_status"),
            jurisdiction=item.get("jurisdiction"),
            customer_region=region_info["customer_region"],
            customer_segment=item.get("customer_segment"),
            regional_request_profile=region_info["regional_request_profile"],
            predicted_regional_needs=region_info["predicted_regional_needs"],
            regional_routing_notes=region_info["regional_routing_notes"],
            authority=item.get("authority"),
            compliance_area=item.get("compliance_area"),
            effective_date=item.get("effective_date"),
            title=item["title"],
            raw_content=item.get("raw_content"),
            category=item["category"],
            severity=item["severity"],
            confidence=item["confidence"],
            summary=item["summary"],
            escalation_team=item["escalation_team"],
            should_escalate=item["should_escalate"],
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
            action="trust_request_seeded",
            details="Created from customer trust demo data.",
        )

        create_audit_event(
            session=session,
            incident_id=incident.id,
            action="regional_playbook_attached",
            details=(
                f"Region={incident.customer_region}. Predicted needs={incident.predicted_regional_needs}. "
                f"Routing notes={incident.regional_routing_notes}"
            ),
        )

        create_audit_event(
            session=session,
            incident_id=incident.id,
            action="stakeholder_review_matrix_generated",
            details="Generated recommended stakeholder review matrix based on request content, region, category, and escalation path.",
        )

        if incident.should_escalate:
            create_audit_event(
                session=session,
                incident_id=incident.id,
                action="review_required",
                details=(
                    f"Trust request requires cross-functional review. "
                    f"Priority={incident.severity}, confidence={incident.confidence}."
                ),
            )

        created.append(incident)

    return created
