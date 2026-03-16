"""
Farcaster data collector using Neynar API v2.
"""
import httpx
from config import NEYNAR_API_KEY, SEARCH_KEYWORDS

NEYNAR_BASE = "https://api.neynar.com/v2/farcaster"


async def collect_farcaster() -> str:
    if not NEYNAR_API_KEY:
        return "[Farcaster] No NEYNAR_API_KEY configured — skipped."

    all_casts = []
    seen_hashes = set()

    async with httpx.AsyncClient(timeout=30) as client:
        for keyword in SEARCH_KEYWORDS[:6]:
            try:
                resp = await client.get(
                    f"{NEYNAR_BASE}/cast/search",
                    params={"q": keyword, "limit": 10},
                    headers={
                        "accept": "application/json",
                        "x-api-key": NEYNAR_API_KEY,
                    },
                )

                if resp.status_code != 200:
                    continue

                data = resp.json()
                casts = data.get("result", {}).get("casts", [])

                for cast in casts:
                    cast_hash = cast.get("hash", "")
                    if cast_hash in seen_hashes:
                        continue
                    seen_hashes.add(cast_hash)

                    author = cast.get("author", {})
                    username = author.get("username") or "unknown"
                    display = author.get("display_name") or username
                    text = (cast.get("text") or "")[:200]
                    followers = author.get("follower_count", 0)

                    all_casts.append(
                        f"\n  💬 *{display}* (@{username})\n"
                        f"     Followers: {followers:,}\n"
                        f"     \"{text}\""
                    )

            except Exception as e:
                all_casts.append(f"  [Farcaster error for '{keyword}']: {e}")

    if not all_casts:
        return "[Farcaster] No results found for current keywords."

    # Deduplicate and limit
    all_casts = all_casts[:15]

    return (
        "🟣 *FARCASTER SIGNALS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(all_casts)
    )
