import os
from typing import Any

import requests
from dotenv import load_dotenv

from models.incident import Incident

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_alert(incident: Incident) -> dict[str, Any]:
    if not SLACK_WEBHOOK_URL:
        return {"sent": False, "reason": "SLACK_WEBHOOK_URL missing"}

    message = {
        "text": (
            "🚨 Emerging AI Risk Signal\n\n"
            f"*Category:* {incident.category}\n"
            f"*Severity:* {incident.severity}/10\n"
            f"*Confidence:* {incident.confidence:.2f}\n"
            f"*Recommended Review Team:* {incident.recommended_review_team}\n\n"
            f"*Analyst Summary:* {incident.analyst_summary}\n\n"
            f"*Suggested Next Steps:* {incident.suggested_next_steps}\n\n"
            f"*Source:* {incident.source_url or 'N/A'}\n\n"
            "Note: This is an analyst-assist triage signal, not an automated enforcement decision."
        )
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message, timeout=10)

    return {
        "sent": response.status_code == 200,
        "status_code": response.status_code,
        "response": response.text[:500],
    }
