import os
import requests
from dotenv import load_dotenv

load_dotenv()

X_SEARCH_QUERIES = [
    '"ChatGPT jailbreak"',
    '"AI scam"',
    '"AI phishing"',
    '"deepfake fraud"',
    '"AI regulation"',
]

DEMO_X_SIGNALS = [
    {
        "id": "x_demo_jailbreak_001",
        "source": "x",
        "source_community": "X / AI safety chatter",
        "title": "Viral thread claims a new jailbreak prompt bypasses safeguards",
        "body": "A high-engagement post claims users are sharing a prompt chain that bypasses model refusals. Needs validation before escalation.",
        "url": "https://x.com/",
        "score": 240,
    },
    {
        "id": "x_demo_deepfake_001",
        "source": "x",
        "source_community": "X / fraud monitoring",
        "title": "Posts report increased deepfake impersonation scams",
        "body": "Multiple posts describe AI-generated voice/video impersonation scams targeting customer support and payment workflows.",
        "url": "https://x.com/",
        "score": 180,
    },
    {
        "id": "x_demo_policy_001",
        "source": "x",
        "source_community": "X / policy discussion",
        "title": "Policy commentators discuss new AI transparency requirements",
        "body": "A cluster of posts discusses transparency, provenance, and disclosure obligations for AI-generated content.",
        "url": "https://x.com/",
        "score": 130,
    },
]


def fetch_x_signals(limit=10):
    bearer_token = os.getenv("X_BEARER_TOKEN")

    if not bearer_token:
        print("X_BEARER_TOKEN missing. Using demo X fallback signals.")
        return DEMO_X_SIGNALS[:limit]

    headers = {
        "Authorization": f"Bearer {bearer_token}",
    }

    signals = []

    for query in X_SEARCH_QUERIES:
        url = "https://api.x.com/2/tweets/search/recent"
        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": 10,
            "tweet.fields": "created_at,public_metrics,author_id",
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("data", []):
                metrics = item.get("public_metrics", {})
                tweet_id = item.get("id")

                signals.append({
                    "id": f"x_{tweet_id}",
                    "source": "x",
                    "source_community": "X recent search",
                    "title": item.get("text", "")[:120],
                    "body": item.get("text", ""),
                    "url": f"https://x.com/i/web/status/{tweet_id}",
                    "score": metrics.get("like_count", 0) + metrics.get("retweet_count", 0),
                })

        except Exception as e:
            print(f"Failed to fetch X query {query}: {e}")

    if not signals:
        print("X fetch failed or returned no posts. Using demo X fallback signals.")
        return DEMO_X_SIGNALS[:limit]

    return signals[:limit]
