"""
Onchain signal collector.
Checks for recent DAO deployments via Nouns Builder subgraph.
"""
import httpx


async def collect_onchain() -> str:
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        # --- Recent DAO factory deployments (Nouns Builder) ---
        try:
            resp = await client.post(
                "https://api.goldsky.com/api/public/"
                "project_clkk1ucdyf6ak38svcatie9tf/subgraphs/"
                "nouns-builder-ethereum-mainnet/1.0.0/gn",
                json={
                    "query": """
                    {
                        daos(first: 10, orderBy: createdAt, orderDirection: desc) {
                            name
                            treasury
                            createdAt
                        }
                    }
                    """
                },
            )

            if resp.status_code == 200:
                data = resp.json()
                daos = data.get("data", {}).get("daos", [])
                for dao in daos:
                    name = dao.get("name") or "Unnamed DAO"
                    treasury = dao.get("treasury") or "N/A"
                    results.append(
                        f"\n  🏛 *{name}*\n"
                        f"     Treasury: {treasury[:16]}...\n"
                        f"     Type: Nouns Builder DAO"
                    )

        except Exception as e:
            results.append(f"  [Nouns Builder] Error: {e}")

    if not results:
        return "[Onchain] No new signals detected."

    return (
        "⛓ *ONCHAIN SIGNALS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + "\n".join(results)
    )
