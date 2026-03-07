import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["8733814311:AAHTM-Yk6QYUkvcIm2f6NTQUYAs7OaMrEO0"]
TELEGRAM_CHAT_ID = os.environ["5756853333"]

APIFY_API_TOKEN = os.getenv("apify_api_Z9v9sjrlUgz4vYY5572Xa4bQNmXtbh2qG1K", "")
NEYNAR_API_KEY = os.getenv("AFD07FEB-1FE5-4912-8703-1734750C19EB", "")
LUNARCRUSH_API_KEY = os.getenv("e61uvuw6rytuakn7eq9l6k82kxmmdspeu0dthxrlb", "")
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
