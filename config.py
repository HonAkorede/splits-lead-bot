import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
NEYNAR_API_KEY = os.getenv("NEYNAR_API_KEY", "")
LUNARCRUSH_API_KEY = os.getenv("LUNARCRUSH_API_KEY", "")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")

CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", "0 9 * * *")

# Keywords to search across all social platforms
SEARCH_KEYWORDS = [
    "split revenue onchain",
    "pay contributors onchain",
    "treasury split",
    "onchain payroll",
    "multisig payroll frustrating",
    "split mint revenue",
    "revenue sharing DAO",
    "how do we split this onchain",
    "contributor payouts crypto",
    "split royalties onchain",
    "gnosis safe payroll",
    "waterfall payments crypto",
]
