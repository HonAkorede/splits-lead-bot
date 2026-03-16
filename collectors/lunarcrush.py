"""
LunarCrush collector — trending projects by social velocity.
"""
import httpx
from config import LUNARCRUSH_API_KEY

LUNARCRUSH_BASE = "https://lunarcrush.com/api4/public"


async def collect_lunarcrush() -> str:
    if not LUNARCRUSH_API_KEY:
        return "[LunarCrush] No LUNARCRUSH_API_KEY configured — skipped."

    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{LUNARCRUSH_BASE}/coins/list/v2",
                headers={"Authorization": f"Bearer {LUNARCRUSH_API_KEY}"},
                params={"sort": "galaxy_score", "limit": 30},
            )

            if resp.status_code != 200:
                return f"[LunarCrush] API returned HTTP {resp.status_code}. Key may be invalid or API changed."

            data = resp.json()
            coins = data.get("data", [])

            # Skip major tokens
            skip = {"BTC", "ETH", "SOL", "BNB", "USDT", "USDC", "XRP", "ADA", "DOGE", "AVAX"}

            for coin in coins:
                name = coin.get("name") or "Unknown"
                symbol = coin.get("symbol") or "?"
                galaxy_score = coin.get("galaxy_score", 0)
                alt_rank = coin.get("alt_rank", 0)
                categories = coin.get("categories") or ""

                if symbol in skip:
                    continue

                results.append(
                    f"\n  ⭐ *{name}* ({symbol})\n"
                    f"     Galaxy Score: {galaxy_score} | Alt Rank: #{alt_rank}\n"
                    f"     Categories: {categories}"
                )

            results = results[:12]

        except Exception as e:
            return f"[LunarCrush] Error: {e}"

    if not results:
        return "[LunarCrush] No trending projects found."

    return (
        "🌙 *LUNARCRUSH TRENDING*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(results)
    )
