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
            data = resp.json()
            coins = data.get("data", [])

            for coin in coins:
                name = coin.get("name", "Unknown")
                symbol = coin.get("symbol", "?")
                galaxy_score = coin.get("galaxy_score", 0)
                alt_rank = coin.get("alt_rank", 0)
                categories = coin.get("categories", "")

                # Skip pure L1s and major tokens — we want projects
                if symbol in ("BTC", "ETH", "SOL", "BNB", "USDT", "USDC"):
                    continue

                results.append(
                    f"- {name} ({symbol}) | Galaxy Score: {galaxy_score} | "
                    f"Alt Rank: {alt_rank} | Categories: {categories}"
                )

            results = results[:15]

        except Exception as e:
            return f"[LunarCrush] Error: {e}"

    if not results:
        return "[LunarCrush] No trending projects found."

    return "LunarCrush Trending Projects:\n" + "\n".join(results)
