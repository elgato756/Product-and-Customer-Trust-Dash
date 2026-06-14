from collections import Counter
from typing import Iterable

from models.incident import Incident


REGION_PLAYBOOKS = {
    "Japan / APAC": {
        "profile": "Japan/APAC customer trust profile",
        "predicted_needs": [
            "localized security and privacy explanations",
            "data residency and hosting-region clarification",
            "subprocessor and cross-border transfer language",
            "customer-facing architecture diagrams or dedicated storage explanation",
        ],
        "routing_notes": "Front-load Security, Privacy, Product, and APAC GTM review. Prepare localized data handling language and avoid overclaiming residency or dedicated-storage commitments without approved evidence.",
        "team": "security_privacy_product_apac_gtm",
    },
    "EU / EEA": {
        "profile": "EU/EEA regulatory and privacy assurance profile",
        "predicted_needs": [
            "GDPR, DPA, SCC, and subprocessor documentation",
            "data retention and deletion language",
            "model/data use boundary explanation",
            "EU AI Act or regulated-sector diligence context",
        ],
        "routing_notes": "Front-load Legal, Privacy, Product, and Security review. Prepare DPA/subprocessor evidence and route broad data-use or AI Act claims before external use.",
        "team": "legal_privacy_product_security_eu",
    },
    "US / Financial Services": {
        "profile": "US financial services enterprise assurance profile",
        "predicted_needs": [
            "SOC 2 Type 2 and ISO 27001 evidence mapping",
            "CAIQ and security questionnaire artifacts",
            "encryption, access control, logging, and vulnerability management evidence",
            "dedicated storage, segregation, retention, and incident response clarification",
        ],
        "routing_notes": "Front-load Field Security, GRC, Security, Privacy, and Customer Success. Use approved answer-bank content first, then escalate architecture or dedicated-storage claims.",
        "team": "field_security_grc_security_privacy_customer_success",
    },
    "Global": {
        "profile": "Global customer trust profile",
        "predicted_needs": [
            "approved answer-bank response",
            "SOC 2 / ISO evidence path",
            "Trust Center artifact mapping",
            "claim-substantiation review for broad public statements",
        ],
        "routing_notes": "Use approved global trust artifacts where available. Escalate unsupported claims, product-specific commitments, and privacy-sensitive language.",
        "team": "grc_customer_trust_triage",
    },
}


def normalize_region(region: str | None, jurisdiction: str | None = None, content: str | None = None) -> str:
    text = " ".join([region or "", jurisdiction or "", content or ""]).lower()

    if any(token in text for token in ["japan", "jp", "tokyo", "apac", "asia"]):
        return "Japan / APAC"
    if any(token in text for token in ["eu", "eea", "gdpr", "dpa", "scc", "europe", "european"]):
        return "EU / EEA"
    if any(token in text for token in ["bank", "financial services", "finserv", "ffiec", "nydfs", "us financial"]):
        return "US / Financial Services"
    return region or jurisdiction or "Global"


def regional_context(
    region: str | None = None,
    jurisdiction: str | None = None,
    content: str | None = None,
) -> dict[str, str]:
    normalized_region = normalize_region(region, jurisdiction, content)
    playbook = REGION_PLAYBOOKS.get(normalized_region, REGION_PLAYBOOKS["Global"])

    return {
        "customer_region": normalized_region,
        "regional_request_profile": playbook["profile"],
        "predicted_regional_needs": "; ".join(playbook["predicted_needs"]),
        "regional_routing_notes": playbook["routing_notes"],
        "regional_escalation_team": playbook["team"],
    }


def summarize_regional_patterns(requests: Iterable[Incident]) -> list[dict[str, object]]:
    grouped: dict[str, list[Incident]] = {}
    for request in requests:
        region = request.customer_region or request.jurisdiction or "Global"
        grouped.setdefault(region, []).append(request)

    insights = []
    for region, items in grouped.items():
        category_counts = Counter(item.category for item in items)
        escalation_counts = Counter(item.escalation_team for item in items)
        playbook = REGION_PLAYBOOKS.get(region, REGION_PLAYBOOKS["Global"])
        insights.append(
            {
                "region": region,
                "request_count": len(items),
                "top_categories": category_counts.most_common(3),
                "recommended_review_path": escalation_counts.most_common(1)[0][0] if escalation_counts else playbook["team"],
                "predicted_needs": playbook["predicted_needs"],
                "routing_notes": playbook["routing_notes"],
            }
        )

    return sorted(insights, key=lambda item: item["request_count"], reverse=True)
