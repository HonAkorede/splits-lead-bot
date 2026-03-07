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
        for keyword in SEARCH_KEYWORDS[:6]:  # Limit to avoid rate limits
            try:
                # Start Apify actor run
                run_resp = await client.post(
                    f"{APIFY_BASE}/acts/{APIFY_TWITTER_ACTOR}/runs",
                    params={"token": APIFY_API_TOKEN},
                    json={
                        "searchTerms": [keyword],
                        "maxTweets": 20,
                        "sort": "Latest",
                    },
                )
                run_data = run_resp.json()
                run_id = run_data.get("data", {}).get("id")
                if not run_id:
                    continue

                # Poll for completion (max 90s)
                for _ in range(18):
                    await asyncio.sleep(5)
                    status_resp = await client.get(
                        f"{APIFY_BASE}/actor-runs/{run_id}",
                        params={"token": APIFY_API_TOKEN},
                    )
                    status = status_resp.json().get("data", {}).get("status")
                    if status == "SUCCEEDED":
                        break
                    if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                        break
                else:
                    continue

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
                    params={"token": APIFY_API_TOKEN, "limit": 20},
                )
                items = items_resp.json()

                for tweet in items:
                    text = tweet.get("full_text") or tweet.get("text", "")
                    user = tweet.get("user", {}).get("screen_name", "unknown")
                    all_tweets.append(f"@{user}: {text[:300]}")

            except Exception as e:
                all_tweets.append(f"[Twitter error for '{keyword}']: {e}")

    if not all_tweets:
        return "[Twitter] No results found for current keywords."

    return "Twitter/X Leads:\n" + "\n---\n".join(all_tweets)
