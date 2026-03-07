"""
Onchain signal collector.
Checks for new Zora creates and recent DAO deployments
where the funds recipient is a plain EOA (not a Split or multisig).
"""
import httpx

# Zora public API for recent creates
ZORA_API = "https://api.zora.co/discover/tokens"

# Known Splits factory addresses (to filter OUT contracts already using Splits)
SPLITS_FACTORIES = {
    "0x2ed6c4B5dA6378c7897AC67Ba9e43102Feb694EE".lower(),  # SplitMain v1
    "0x80f1B766817D04870f115fEBbcCADF8DBF75E017".lower(),  # SplitMain v2
}


async def collect_onchain() -> str:
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        # --- Zora recent mints ---
        try:
            resp = await client.get(
                "https://api.zora.co/discover/tokens",
                params={
                    "chain": "ZORA_MAINNET",
                    "sort_key": "CREATED",
                    "sort_direction": "DESC",
                    "limit": 30,
                },
            )

            if resp.status_code == 200:
                data = resp.json()
                tokens = data.get("results", data.get("tokens", []))

                for token in tokens[:30]:
                    name = token.get("name", "Untitled")
                    creator = token.get("creator", "")
                    recipient = (
                        token.get("fundsRecipient", "")
                        or token.get("payoutRecipient", "")
                        or ""
                    )

                    # Flag if recipient is same as creator (single EOA, no split)
                    if recipient and creator:
                        r = recipient.lower()
                        c = creator.lower()
                        if r == c and r not in SPLITS_FACTORIES:
                            results.append(
                                f"- Zora: '{name}' | Creator: {creator[:10]}... | "
                                f"Funds go to single EOA (no Split detected)"
                            )
            else:
                results.append(
                    f"[Zora API] HTTP {resp.status_code} — may need auth or updated endpoint"
                )

        except Exception as e:
            results.append(f"[Zora] Error: {e}")

        # --- Recent DAO factory deployments (Nouns Builder, Aragon, etc.) ---
        try:
            # Check Nouns Builder recent DAOs via their API
            resp = await client.get(
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
                    name = dao.get("name", "Unnamed DAO")
                    treasury = dao.get("treasury", "")
                    results.append(
                        f"- New Nouns Builder DAO: '{name}' | "
                        f"Treasury: {treasury[:10]}..."
                    )

        except Exception as e:
            results.append(f"[Nouns Builder] Error: {e}")

    if not results:
        return "[Onchain] No new signals detected."

    return "Onchain Signals:\n" + "\n".join(results)
