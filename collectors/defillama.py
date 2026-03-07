"""
DeFiLlama collector — finds new protocols generating fees
that likely have no payout infrastructure.
"""
import httpx
from datetime import datetime, timedelta

DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"
DEFILLAMA_FEES = "https://api.llama.fi/overview/fees"


async def collect_defillama() -> str:
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Get protocols with fees
            fees_resp = await client.get(DEFILLAMA_FEES)
            fees_data = fees_resp.json()
            protocols = fees_data.get("protocols", [])

            # Filter: recently listed, generating meaningful fees
            cutoff = datetime.utcnow() - timedelta(days=30)

            for p in protocols:
                # Check if protocol is relatively new or small
                total_fees_24h = p.get("total24h") or 0
                name = p.get("name", "Unknown")
                category = p.get("category", "")
                chains = p.get("chains", [])

                # We want protocols generating $1k-$500k daily fees
                # (big enough to need infra, small enough to not have it)
                if 1000 <= total_fees_24h <= 500000:
                    results.append(
                        f"- {name} | Category: {category} | "
                        f"Chains: {', '.join(chains[:3])} | "
                        f"24h Fees: ${total_fees_24h:,.0f}"
                    )

            # Cap at top 20 by relevance
            results = results[:20]

        except Exception as e:
            return f"[DeFiLlama] Error fetching data: {e}"

    if not results:
        return "[DeFiLlama] No new fee-generating protocols found."

    return (
        "DeFiLlama New/Mid-Size Protocols Generating Fees:\n"
        + "\n".join(results)
    )
