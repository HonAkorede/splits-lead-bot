"""
Sends the daily lead report to Telegram.
Handles message splitting for Telegram's 4096-char limit.
"""
import httpx
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
MAX_MSG_LEN = 4000  # Leave buffer under 4096


async def send_report(report: str) -> None:
    chunks = _split_message(report)

    async with httpx.AsyncClient(timeout=30) as client:
        for i, chunk in enumerate(chunks):
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }
            resp = await client.post(f"{API_BASE}/sendMessage", json=payload)

            if resp.status_code != 200:
                # Retry without markdown if parsing fails
                payload["parse_mode"] = ""
                await client.post(f"{API_BASE}/sendMessage", json=payload)


def _split_message(text: str) -> list[str]:
    if len(text) <= MAX_MSG_LEN:
        return [text]

    chunks = []
    while text:
        if len(text) <= MAX_MSG_LEN:
            chunks.append(text)
            break

        # Try to split at a newline
        split_at = text.rfind("\n", 0, MAX_MSG_LEN)
        if split_at == -1:
            split_at = MAX_MSG_LEN

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    return chunks
