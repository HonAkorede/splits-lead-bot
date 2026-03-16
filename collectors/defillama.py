"""
DeFiLlama collector — finds NEW and small protocols generating fees
that likely have no payout infrastructure yet.
Includes links to project pages on DeFiLlama.
"""
import httpx
from datetime import datetime, timedelta

DEFILLAMA_FEES = "https://api.llama.fi/overview/fees"
DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"


async def collect_defillama() -> str:
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Get all protocols to check launch dates + get links
            proto_resp = await client.get(DEFILLAMA_PROTOCOLS)
            all_protos = proto_resp.json()

            # Build maps: name -> listedAt, name -> links
            proto_info = {}
            for p in all_protos:
                name = (p.get("name") or "").lower()
                if name:
                    proto_info[name] = {
                        "listed_at": p.get("listedAt", 0),
                        "url": p.get("url") or "",
                        "twitter": p.get("twitter") or "",
                        "slug": p.get("slug") or "",
                    }

            # Get protocols with fees
            fees_resp = await client.get(DEFILLAMA_FEES)
            fees_data = fees_resp.json()
            protocols = fees_data.get("protocols", [])

            cutoff_90d = (datetime.utcnow() - timedelta(days=90)).timestamp()
            cutoff_30d = (datetime.utcnow() - timedelta(days=30)).timestamp()

            scored = []
            for p in protocols:
                total_fees_24h = p.get("total24h") or 0
                name = p.get("name") or "Unknown"
                category = p.get("category") or ""
                chains = p.get("chains") or []

                info = proto_info.get(name.lower(), {})
                launch_ts = info.get("listed_at", 0)
                website = info.get("url", "")
                twitter = info.get("twitter", "")
                slug = info.get("slug", "")

                if total_fees_24h < 50 or total_fees_24h > 500000:
                    continue

                # Score: newer + smaller = better lead
                score = 0
                if launch_ts > cutoff_30d:
                    score += 3
                elif launch_ts > cutoff_90d:
                    score += 2
                if total_fees_24h < 10000:
                    score += 2
                elif total_fees_24h < 50000:
                    score += 1

                age_label = ""
                if launch_ts > cutoff_30d:
                    age_label = "🆕 NEW (<30 days)"
                elif launch_ts > cutoff_90d:
                    age_label = "📅 Recent (<90 days)"

                # Build links line
                links = []
                if website:
                    links.append(f"🌐 {website}")
                if twitter:
                    tw = twitter.replace("https://twitter.com/", "").replace("https://x.com/", "").strip("/")
                    links.append(f"🐦 x.com/{tw}")
                if slug:
                    links.append(f"📊 defillama.com/protocol/{slug}")
                links_str = " | ".join(links) if links else "No links"

                entry = (
                    f"\n  📦 *{name}*\n"
                    f"     Category: {category}\n"
                    f"     Chain(s): {', '.join(chains[:3])}\n"
                    f"     24h Fees: ${total_fees_24h:,.0f}\n"
                    f"     {age_label}\n"
                    f"     {links_str}"
                ) if age_label else (
                    f"\n  📦 *{name}*\n"
                    f"     Category: {category}\n"
                    f"     Chain(s): {', '.join(chains[:3])}\n"
                    f"     24h Fees: ${total_fees_24h:,.0f}\n"
                    f"     {links_str}"
                )

                scored.append((score, entry))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = [entry for _, entry in scored[:15]]

        except Exception as e:
            return f"[DeFiLlama] Error fetching data: {e}"

    if not results:
        return "[DeFiLlama] No new fee-generating protocols found."

    return (
        "💰 *UNDER-THE-RADAR PROTOCOLS (generating fees)*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(results)
    )
