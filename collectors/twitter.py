"""
Twitter/X data collector using Apify's Twitter scraper.
Falls back to empty results if no API token is configured.
"""
import httpx
import asyncio
from config import APIFY_API_TOKEN, SEARCH_KEYWORDS

APIFY_TWITTER_ACTOR = "apidojo/tweet-scraper"
APIFY_BASE = "https://api.apify.com/v2"


async def collect_twitter() -> str:
    if not APIFY_API_TOKEN:
        return "[Twitter] No APIFY_API_TOKEN configured — skipped."

    all_tweets = []

    async with httpx.AsyncClient(timeout=120) as client:
        for keyword in SEARCH_KEYWORDS[:4]:  # Limit to avoid rate limits
            try:
                # Start Apify actor run
                run_resp = await client.post(
                    f"{APIFY_BASE}/acts/{APIFY_TWITTER_ACTOR}/runs",
                    params={"token": APIFY_API_TOKEN},
                    json={
                        "searchTerms": [keyword],
                        "maxTweets": 10,
                        "sort": "Latest",
                    },
                )
                run_data = run_resp.json()
                run_id = run_data.get("data", {}).get("id")
                if not run_id:
                    continue

                # Poll for completion (max 60s)
                status = None
                for _ in range(12):
                    await asyncio.sleep(5)
                    status_resp = await client.get(
                        f"{APIFY_BASE}/actor-runs/{run_id}",
                        params={"token": APIFY_API_TOKEN},
                    )
                    status = status_resp.json().get("data", {}).get("status")
                    if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                        break

                if status != "SUCCEEDED":
                    continue

                # Fetch results
                dataset_id = (
                    status_resp.json()
                    .get("data", {})
                    .get("defaultDatasetId")
                )
                items_resp = await client.get(
                    f"{APIFY_BASE}/datasets/{dataset_id}/items",
                    params={"token": APIFY_API_TOKEN, "limit": 10},
                )
                items = items_resp.json()

                for tweet in items:
                    text = (tweet.get("full_text") or tweet.get("text") or "")[:200]
                    user = tweet.get("user", {}).get("screen_name") or "unknown"
                    name = tweet.get("user", {}).get("name") or user
                    followers = tweet.get("user", {}).get("followers_count", 0)

                    all_tweets.append(
                        f"\n  🐦 *{name}* (@{user})\n"
                        f"     Followers: {followers:,}\n"
                        f"     \"{text}\""
                    )

            except Exception as e:
                all_tweets.append(f"  [Twitter error for '{keyword}']: {e}")

    if not all_tweets:
        return "[Twitter] No results found for current keywords."

    all_tweets = all_tweets[:15]

    return (
        "🐦 *TWITTER/X SIGNALS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(all_tweets)
    )
