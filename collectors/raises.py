"""
DeFiLlama raises collector — finds projects that just raised funding.
These are prime Splits leads: they have money, are building, and likely
need revenue/payment splitting infrastructure.
"""
import httpx
from datetime import datetime, timedelta

RAISES_URL = "https://api.llama.fi/raises"


async def collect_raises() -> str:
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(RAISES_URL)
            raises = resp.json().get("raises", [])

            # Only raises from the last 14 days
            cutoff = (datetime.utcnow() - timedelta(days=14)).timestamp()

            # Categories most likely to need Splits
            target_categories = {
                "defi", "nft", "gaming", "dao", "social",
                "creator", "music", "media", "marketplace",
            }

            for r in raises:
                ts = r.get("date", 0)
                if ts < cutoff:
                    continue

                name = r.get("name") or "Unknown"
                amount = r.get("amount")
                round_type = r.get("round") or "Unknown"
                category = r.get("category") or ""
                category_group = r.get("categoryGroup") or ""
                chains = r.get("chains") or []
                sector = r.get("sector") or ""
                source = r.get("source") or ""
                lead_investors = r.get("leadInvestors") or []
                other_investors = r.get("otherInvestors") or []

                # Prioritize categories relevant to Splits
                combined = (category + " " + category_group + " " + sector).lower()
                is_target = any(t in combined for t in target_categories)

                amount_str = f"${amount}M" if amount else "Undisclosed"
                chains_str = ", ".join(chains[:3]) if chains else "N/A"
                date_str = datetime.fromtimestamp(ts).strftime("%b %d")

                # Investors
                all_investors = lead_investors + other_investors
                investors_str = ", ".join(all_investors[:3]) if all_investors else "N/A"

                entry = (
                    f"\n  🏗 *{name}*\n"
                    f"     Round: {round_type} — {amount_str}\n"
                    f"     Date: {date_str}\n"
                    f"     Chain(s): {chains_str}\n"
                    f"     Investors: {investors_str}\n"
                    f"     What: {sector[:100]}\n"
                    f"     Source: {source}"
                )

                if is_target:
                    results.insert(0, entry)
                else:
                    results.append(entry)

            results = results[:15]

        except Exception as e:
            return f"[Raises] Error: {e}"

    if not results:
        return "[Raises] No recent funding rounds found."

    return (
        "🚀 *RECENT FUNDING ROUNDS (last 14 days)*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(results)
    )
