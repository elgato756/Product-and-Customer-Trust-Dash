import json
import os
from typing import Any


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data)


def fallback_analysis(reason: str, title: str = "", body: str = "") -> str:
    content = f"{title} {body}".lower()

    category = "customer_trust_request"
    severity = 5
    review_team = "grc_customer_trust_triage"

    evidence = [
        "Request was ingested successfully.",
        "Fallback classification was used because AI classification could not complete.",
    ]

    next_steps = [
        "Review the request against approved answer-bank content.",
        "Map the response to approved evidence before sending externally.",
        "Escalate to the recommended stakeholder group if the request is sensitive or non-standard.",
    ]

    if any(term in content for term in ["dpa", "scc", "gdpr", "privacy", "retention", "deletion", "subprocessor"]):
        category = "privacy_legal_review"
        severity = 8
        review_team = "legal_privacy_grc"
        evidence.append("Potential privacy/legal terms detected.")

    elif any(term in content for term in ["architecture", "encryption", "access control", "storage", "s3", "segregation"]):
        category = "security_architecture_review"
        severity = 7
        review_team = "security_field_security_grc"
        evidence.append("Technical security or architecture topic detected.")

    elif any(term in content for term in ["soc 2", "iso 27001", "caiq", "questionnaire", "trust center"]):
        category = "questionnaire_evidence_request"
        severity = 6
        review_team = "grc_customer_trust_field_security"
        evidence.append("Customer diligence or evidence request detected.")

    elif any(term in content for term in ["guarantee", "always", "never", "all customer data", "unsupported claim"]):
        category = "unsupported_external_claim_risk"
        severity = 9
        review_team = "legal_security_privacy_grc"
        evidence.append("Potential unsupported external claim language detected.")

    return _json({
        "is_relevant": True,
        "category": category,
        "severity": severity,
        "confidence": 0.72,
        "evidence": evidence,
        "missing_context": [
            reason,
            "Human review is required before sending customer-facing responses.",
        ],
        "human_review_recommended": severity >= 7,
        "recommended_review_team": review_team,
        "analyst_summary": (
            "Customer trust request ingested successfully. Review approved evidence, "
            "regional context, and stakeholder routing before responding externally."
        ),
        "suggested_next_steps": next_steps,
    })


def classify_content(title: str, body: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return fallback_analysis("OPENAI_API_KEY is missing from backend/.env.", title, body)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are classifying a customer trust / enterprise assurance request.

Classify the request for:
- severity from 1-10
- category
- recommended review path
- brief summary
- rationale
- whether human review is required
- confidence from 0-1

Focus on customer trust, security questionnaires, evidence mapping, regional routing,
stakeholder review, and unsupported external claims.

Title: {title}

Body:
{body}

Return JSON only.
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        raw = json.loads(response.choices[0].message.content or "{}")

        return _json({
            "is_relevant": raw.get("is_relevant", True),
            "category": raw.get("category", "customer_trust_request"),
            "severity": int(raw.get("severity", 7)),
            "confidence": float(raw.get("confidence", 0.85)),
            "evidence": raw.get("evidence", ["AI-assisted classification completed."]),
            "missing_context": raw.get("missing_context", []),
            "human_review_recommended": raw.get("human_review_recommended", True),
            "recommended_review_team": raw.get("recommended_review_team", "grc_customer_trust_security_privacy"),
            "analyst_summary": raw.get("analyst_summary", "Customer trust request requiring review."),
            "suggested_next_steps": raw.get("suggested_next_steps", ["Review evidence before external response."]),
        })

    except Exception as error:
        return fallback_analysis(str(error), title, body)
