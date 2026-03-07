"""
Farcaster data collector using Neynar API.
"""
import httpx
from config import NEYNAR_API_KEY, SEARCH_KEYWORDS

NEYNAR_BASE = "https://api.neynar.com/v2/farcaster"


async def collect_farcaster() -> str:
    if not NEYNAR_API_KEY:
        return "[Farcaster] No NEYNAR_API_KEY configured — skipped."

    all_casts = []

    async with httpx.AsyncClient(timeout=30) as client:
        for keyword in SEARCH_KEYWORDS[:6]:
            try:
                resp = await client.get(
                    f"{NEYNAR_BASE}/cast/search",
                    params={"q": keyword, "limit": 15},
                    headers={
                        "accept": "application/json",
                        "x-api-key": NEYNAR_API_KEY,
                    },
                )
                data = resp.json()
                casts = data.get("result", {}).get("casts", [])

                for cast in casts:
                    author = cast.get("author", {}).get("username", "unknown")
                    text = cast.get("text", "")[:300]
                    all_casts.append(f"@{author}: {text}")

            except Exception as e:
                all_casts.append(f"[Farcaster error for '{keyword}']: {e}")

    if not all_casts:
        return "[Farcaster] No results found for current keywords."

    return "Farcaster Leads:\n" + "\n---\n".join(all_casts)
