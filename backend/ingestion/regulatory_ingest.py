import re
from datetime import datetime

import requests


OFFICIAL_POLICY_SOURCES = [
    {
        "id": "official_nist_ai_rmf_live",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "source_community": "NIST AI Risk Management Framework",
        "jurisdiction": "US",
        "authority": "NIST",
        "compliance_area": "ai_risk_management_governance",
        "title": "NIST AI RMF official source monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "keywords": [
            "manage risks",
            "individuals, organizations, and society",
            "artificial intelligence",
            "AI Risk Management Framework",
        ],
    },
    {
        "id": "official_nist_ai_rmf_core_live",
        "url": "https://airc.nist.gov/airmf-resources/airmf/5-sec-core/",
        "source_community": "NIST AI RMF Core",
        "jurisdiction": "US",
        "authority": "NIST",
        "compliance_area": "govern_map_measure_manage",
        "title": "NIST AI RMF Core functions official source monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "keywords": [
            "GOVERN",
            "MAP",
            "MEASURE",
            "MANAGE",
            "AI risk management",
        ],
    },
    {
        "id": "official_eu_ai_act_timeline_live",
        "url": "https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act",
        "source_community": "European Commission AI Act Service Desk",
        "jurisdiction": "EU",
        "authority": "European Commission",
        "compliance_area": "ai_act_implementation_timeline",
        "title": "EU AI Act implementation timeline official source monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "keywords": [
            "02 Aug 2025",
            "general-purpose AI",
            "governance must be in place",
            "full roll-out",
            "02 Aug 2027",
        ],
    },
]


OFFICIAL_FALLBACK_SIGNALS = [
    {
        "id": "official_eu_ai_act_timeline_001",
        "source": "regulatory_monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "jurisdiction": "EU",
        "authority": "European Commission",
        "compliance_area": "ai_act_implementation_timeline",
        "effective_date": "2025-08-02",
        "source_community": "European Commission AI Act Service Desk",
        "title": "EU AI Act implementation timeline includes GPAI and governance milestones",
        "body": (
            "Official European Commission AI Act timeline materials indicate that the AI Act applies progressively. "
            "The timeline includes 02 Aug 2025 for general-purpose AI rules and governance, and full roll-out "
            "foreseen by 02 Aug 2027. This should be reviewed by legal/policy teams before operational changes."
        ),
        "url": "https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act",
        "score": 100,
    },
    {
        "id": "official_nist_ai_rmf_core_001",
        "source": "regulatory_monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "jurisdiction": "US",
        "authority": "NIST",
        "compliance_area": "govern_map_measure_manage",
        "effective_date": None,
        "source_community": "NIST AI RMF Core",
        "title": "NIST AI RMF Core organizes risk management around Govern, Map, Measure, and Manage",
        "body": (
            "Official NIST AI RMF Core materials organize AI risk management around GOVERN, MAP, MEASURE, "
            "and MANAGE. This is relevant to governance, evaluation, monitoring, and operational safety practices."
        ),
        "url": "https://airc.nist.gov/airmf-resources/airmf/5-sec-core/",
        "score": 95,
    },
    {
        "id": "official_eurlex_ai_act_reference_001",
        "source": "regulatory_monitor",
        "source_type": "official",
        "verification_status": "official_source_verified",
        "jurisdiction": "EU",
        "authority": "European Union",
        "compliance_area": "ai_act_legal_reference",
        "effective_date": None,
        "source_community": "EUR-Lex Official Journal",
        "title": "EUR-Lex official legal text for Regulation (EU) 2024/1689 should be used as source-of-truth reference",
        "body": (
            "EUR-Lex hosts the official text of Regulation (EU) 2024/1689, the Artificial Intelligence Act. "
            "Because the full legal text is lengthy and complex, this system should treat EUR-Lex as a legal "
            "reference requiring human legal/policy review, not as automatically interpreted compliance advice."
        ),
        "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng",
        "score": 100,
    },
]


NOISE_PATTERNS = [
    r"search options\?.*?table of contents",
    r"languages, formats and authentic version.*?how to verify",
    r"help print text document information.*?create an rss alert",
    r"all consolidated versions.*?collapse all",
]


def _clean_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<nav[\s\S]*?</nav>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<header[\s\S]*?</header>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<footer[\s\S]*?</footer>", " ", html, flags=re.IGNORECASE)

    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = re.sub(r"\s+", " ", text).strip()

    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def _remove_duplicate_sentences(text: str, max_sentences: int = 8) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text)
    seen = set()
    cleaned = []

    for part in parts:
        normalized = re.sub(r"\W+", " ", part.lower()).strip()

        if not normalized or normalized in seen:
            continue

        if len(normalized) < 30:
            continue

        seen.add(normalized)
        cleaned.append(part.strip())

        if len(cleaned) >= max_sentences:
            break

    return " ".join(cleaned)


def _extract_relevant_excerpt(text: str, keywords: list[str], max_chars: int = 2200) -> str:
    lowered = text.lower()
    windows = []

    for keyword in keywords:
        idx = lowered.find(keyword.lower())
        if idx != -1:
            start = max(0, idx - 350)
            end = min(len(text), idx + max_chars)
            windows.append(text[start:end])

    if not windows:
        windows.append(text[:max_chars])

    combined = " ".join(windows)
    return _remove_duplicate_sentences(combined, max_sentences=10)


def _is_bad_excerpt(excerpt: str) -> bool:
    bad_terms = [
        "search options",
        "print text",
        "document information",
        "toggle dropdown",
        "languages, formats",
        "create an rss alert",
        "my items",
    ]

    lowered = excerpt.lower()
    return any(term in lowered for term in bad_terms)


def _fetch_official_source(source: dict) -> dict | None:
    headers = {
        "User-Agent": "ai-safety-ops-dashboard/0.1 official-policy-monitor"
    }

    try:
        response = requests.get(source["url"], headers=headers, timeout=15)
        response.raise_for_status()

        text = _clean_html(response.text)
        excerpt = _extract_relevant_excerpt(text, source["keywords"])

        if not excerpt or _is_bad_excerpt(excerpt):
            print(f"Official source excerpt too noisy for {source['url']}. Using curated fallback if available.")
            return None

        return {
            "id": f'{source["id"]}_{datetime.utcnow().strftime("%Y%m%d")}',
            "source": "regulatory_monitor",
            "source_type": source["source_type"],
            "verification_status": source["verification_status"],
            "jurisdiction": source["jurisdiction"],
            "authority": source["authority"],
            "compliance_area": source["compliance_area"],
            "effective_date": None,
            "source_community": source["source_community"],
            "title": source["title"],
            "body": (
                "Official policy source fetched for monitoring. "
                "This excerpt is provided for analyst review only; "
                "do not treat model output as legal advice or a final compliance decision.\n\n"
                f"{excerpt}"
            ),
            "url": source["url"],
            "score": 100,
        }

    except Exception as error:
        print(f"Failed to fetch official policy source {source['url']}: {error}")
        return None


def fetch_regulatory_signals(limit=10, include_secondary=False):
    signals = []

    for source in OFFICIAL_POLICY_SOURCES:
        fetched = _fetch_official_source(source)
        if fetched:
            signals.append(fetched)

    # Always include curated official fallback references for stable demo quality.
    # Deduplicate by source URL so the dashboard does not get spammed.
    existing_urls = {signal["url"] for signal in signals}

    for fallback in OFFICIAL_FALLBACK_SIGNALS:
        if fallback["url"] not in existing_urls:
            signals.append(fallback)

    return signals[:limit]
