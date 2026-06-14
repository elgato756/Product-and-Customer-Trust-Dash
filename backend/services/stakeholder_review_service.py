import json
from typing import Any


def _text_blob(*values: Any) -> str:
    return " ".join(str(value or "") for value in values).lower()


def _row(
    stakeholder: str,
    status: str,
    review_focus: str,
    trigger: str,
    suggested_next_step: str,
) -> dict[str, str]:
    return {
        "stakeholder": stakeholder,
        "status": status,
        "review_focus": review_focus,
        "trigger": trigger,
        "suggested_next_step": suggested_next_step,
    }


def build_stakeholder_review_matrix(
    *,
    title: str = "",
    raw_content: str = "",
    category: str = "",
    verification_status: str = "",
    escalation_team: str = "",
    customer_region: str = "",
    customer_segment: str = "",
    regional_routing_notes: str = "",
    should_escalate: bool = False,
) -> list[dict[str, str]]:
    """Create a demo review matrix for a customer trust request.

    The matrix is intentionally deterministic so the demo can run without an AI key.
    It mirrors the JD requirement: decide what can be answered from approved content,
    what needs stakeholder review, and what should not be claimed externally.
    """
    text = _text_blob(
        title,
        raw_content,
        category,
        verification_status,
        escalation_team,
        customer_region,
        customer_segment,
        regional_routing_notes,
    )

    rows: list[dict[str, str]] = []

    rows.append(
        _row(
            "GRC / Customer Trust",
            "Required",
            "Own intake, triage, evidence mapping, answer-bank reuse, and final response packaging.",
            "Every customer trust request requires a named GRC / Customer Trust owner.",
            "Map the request to approved artifacts, document missing evidence, and coordinate stakeholder review before response finalization.",
        )
    )

    security_terms = [
        "security",
        "encryption",
        "access control",
        "logging",
        "vulnerability",
        "incident response",
        "architecture",
        "dedicated storage",
        "segregation",
        "cloud",
        "hosting",
        "s3",
    ]
    privacy_terms = [
        "privacy",
        "data handling",
        "retention",
        "deletion",
        "subprocessor",
        "cross-border",
        "cross border",
        "data residency",
        "gdpr",
        "dpa",
        "scc",
        "model/data",
        "data use",
    ]
    legal_terms = [
        "legal",
        "dpa",
        "scc",
        "privacy policy",
        "public policy",
        "unsupported claim",
        "external claim",
        "contract",
        "customer-facing claim",
        "broad security claim",
    ]
    product_terms = [
        "product",
        "available",
        "configurable",
        "dedicated storage",
        "data segregation",
        "zero data retention",
        "product tiers",
        "customer-specific",
        "feature",
        "capability",
    ]
    field_security_terms = [
        "questionnaire",
        "caiq",
        "soc 2",
        "iso 27001",
        "evidence",
        "control",
        "bank",
        "financial services",
        "regulated enterprise",
    ]
    regional_terms = [
        "japan",
        "apac",
        "eu",
        "eea",
        "us financial",
        "bank",
        "regional",
        "localized",
    ]
    gtm_terms = [
        "deal",
        "sales",
        "customer success",
        "csm",
        "gtm",
        "prospect",
        "customer call",
        "high-priority deal",
    ]

    needs_security = any(term in text for term in security_terms) or "security" in escalation_team
    needs_privacy = any(term in text for term in privacy_terms) or "privacy" in escalation_team
    needs_legal = any(term in text for term in legal_terms) or "legal" in escalation_team
    needs_product = any(term in text for term in product_terms) or "product" in escalation_team
    needs_field_security = any(term in text for term in field_security_terms) or "field_security" in escalation_team
    needs_regional = any(term in text for term in regional_terms) or bool(customer_region and customer_region != "Global")
    needs_gtm = any(term in text for term in gtm_terms) or any(term in escalation_team for term in ["gtm", "customer_success"])

    if needs_field_security:
        rows.append(
            _row(
                "Field Security",
                "Required",
                "Validate customer-facing technical response quality, questionnaire coverage, and enterprise assurance narrative.",
                "Questionnaire, CAIQ, SOC 2/ISO evidence, regulated customer, or deal-support signal detected.",
                "Confirm which questions can use approved answer-bank content and which require deeper evidence owner review.",
            )
        )

    if needs_security:
        rows.append(
            _row(
                "Security",
                "Required",
                "Review control evidence, architecture statements, encryption/access-control language, and security claim accuracy.",
                "Security architecture, dedicated storage, encryption, logging, vulnerability, or control evidence question detected.",
                "Validate the evidence path and approve any technical language before it is reused externally.",
            )
        )

    if needs_privacy:
        rows.append(
            _row(
                "Privacy",
                "Required",
                "Review data handling, retention/deletion, subprocessors, cross-border transfer, and privacy representation accuracy.",
                "Privacy, GDPR/DPA/SCC, data residency, retention, deletion, or subprocessor topic detected.",
                "Confirm approved privacy language and identify whether DPA, SCC, or subprocessor artifacts should be attached.",
            )
        )

    if needs_legal:
        rows.append(
            _row(
                "Legal",
                "Required",
                "Review customer-facing legal posture, public policy language, contractual wording, and unsupported external claims.",
                "External claim, DPA/SCC, privacy policy, contractual, or broad public statement detected.",
                "Approve or narrow the language before it is sent externally; block unsupported claims until evidence is confirmed.",
            )
        )

    if needs_product:
        rows.append(
            _row(
                "Product",
                "Conditional",
                "Confirm product capability boundaries, configurable options, product-tier behavior, and customer-specific commitments.",
                "Product capability, dedicated storage, zero retention, customer-specific controls, or configurable feature claim detected.",
                "Confirm the accurate product position and update approved customer-facing language if needed.",
            )
        )

    if needs_regional:
        rows.append(
            _row(
                "Regional GTM / Local Team",
                "Conditional",
                "Validate regional customer context, localization needs, and region-specific diligence patterns.",
                "Regional playbook attached based on customer region, jurisdiction, or historical request pattern.",
                "Front-load region-specific artifacts and coordinate localized customer communication where appropriate.",
            )
        )

    if needs_gtm:
        rows.append(
            _row(
                "GTM / Customer Success",
                "Informational",
                "Coordinate customer communication, deal context, response timing, and follow-up expectations.",
                "Sales, CSM, prospect, customer call, or high-priority deal-support context detected.",
                "Use approved language from the answer bank and route follow-up questions back through the review owner.",
            )
        )

    if should_escalate and len(rows) == 1:
        rows.append(
            _row(
                "Cross-Functional Review",
                "Required",
                "Confirm the right stakeholder owners before a customer-facing response is finalized.",
                "The classifier recommended human review but no specific stakeholder trigger was detected.",
                "Assign reviewers based on the customer question, evidence source, and external claim risk.",
            )
        )

    return rows


def build_stakeholder_review_matrix_json(**kwargs: Any) -> str:
    return json.dumps(build_stakeholder_review_matrix(**kwargs))
