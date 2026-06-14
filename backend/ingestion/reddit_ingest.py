import requests

SUBREDDITS = [
    "ChatGPT",
    "OpenAI",
    "LocalLLaMA",
    "artificial",
    "singularity",
]

DEMO_POSTS = [
    {
        "id": "demo_jailbreak_001",
        "subreddit": "ChatGPT",
        "title": "Users sharing a new jailbreak prompt that bypasses model refusals",
        "body": "Several users are discussing a new prompt format that allegedly bypasses safety guardrails and produces restricted instructions.",
        "url": "https://www.reddit.com/r/ChatGPT/",
        "score": 128,
    },
    {
        "id": "demo_fraud_001",
        "subreddit": "OpenAI",
        "title": "AI-generated phishing kits are getting easier to create",
        "body": "A discussion claims that people are using AI tools to generate more convincing phishing emails and fake support flows.",
        "url": "https://www.reddit.com/r/OpenAI/",
        "score": 84,
    },
    {
        "id": "demo_regulatory_001",
        "subreddit": "artificial",
        "title": "New AI regulation may require additional transparency documentation",
        "body": "Commenters are discussing new compliance obligations for AI companies operating in regulated markets.",
        "url": "https://www.reddit.com/r/artificial/",
        "score": 61,
    },
]

def fetch_reddit_posts(limit=10):
    posts = []

    headers = {
        "User-Agent": "Mozilla/5.0 ai-safety-ops-dashboard/0.1"
    }

    for subreddit_name in SUBREDDITS:
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit={limit}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            for child in data.get("data", {}).get("children", []):
                item = child.get("data", {})

                posts.append({
                    "id": item.get("id"),
                    "subreddit": subreddit_name,
                    "title": item.get("title", ""),
                    "body": item.get("selftext", ""),
                    "url": f"https://www.reddit.com{item.get('permalink', '')}",
                    "score": item.get("score", 0),
                })

        except Exception as e:
            print(f"Failed to fetch r/{subreddit_name}: {e}")

    if not posts:
        print("Reddit fetch failed or returned no posts. Using demo fallback posts.")
        return DEMO_POSTS

    return posts
