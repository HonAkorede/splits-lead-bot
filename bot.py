"""
Main bot entrypoint.
Collects data from all sources, analyzes via Claude, sends to Telegram.
Can run as a one-shot or on a daily schedule.
"""
import asyncio
import sys
from datetime import datetime

from collectors import (
    collect_twitter,
    collect_farcaster,
    collect_defillama,
    collect_lunarcrush,
    collect_onchain,
)
from analyzer import analyze_leads
from telegram_sender import send_report


async def run_pipeline() -> None:
    print(f"[{datetime.utcnow().isoformat()}] Starting lead collection...")

    # Run all collectors in parallel
    results = await asyncio.gather(
        collect_twitter(),
        collect_farcaster(),
        collect_defillama(),
        collect_lunarcrush(),
        collect_onchain(),
        return_exceptions=True,
    )

    # Combine results into a single data block
    sections = []
    source_names = ["Twitter/X", "Farcaster", "DeFiLlama", "LunarCrush", "Onchain"]
    for name, result in zip(source_names, results):
        if isinstance(result, Exception):
            sections.append(f"[{name}] Collection error: {result}")
        else:
            sections.append(result)

    collected_data = "\n\n".join(sections)
    print(f"Collected {len(collected_data)} chars of raw data.")

    # Check if we have any real data (not all skipped/errored)
    has_data = any(
        not isinstance(r, Exception) and "skipped" not in r.lower()
        for r in results
    )

    if not has_data:
        summary = (
            "⚠️ *Splits Lead Bot — No Data Sources Active*\n\n"
            "All collectors returned empty. Check your API keys in `.env`:\n"
            "- APIFY_API_TOKEN (Twitter)\n"
            "- NEYNAR_API_KEY (Farcaster)\n"
            "- LUNARCRUSH_API_KEY (LunarCrush)\n\n"
            "DeFiLlama and Onchain collectors don't need keys — "
            "if those also failed, check network connectivity."
        )
        await send_report(summary)
        print("Sent 'no data' alert to Telegram.")
        return

    # Analyze with Claude
    print("Analyzing leads with Claude...")
    report = await analyze_leads(collected_data)

    # Add header
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    header = f"📊 *Splits Lead Intelligence — {date_str}*\n\n"
    full_report = header + report

    # Send to Telegram
    await send_report(full_report)
    print(f"Report sent to Telegram ({len(full_report)} chars).")


def main():
    if "--schedule" in sys.argv:
        _run_scheduled()
    else:
        asyncio.run(run_pipeline())


def _run_scheduled():
    from apscheduler.schedulers.blocking import BlockingScheduler
    from config import CRON_SCHEDULE

    parts = CRON_SCHEDULE.split()
    scheduler = BlockingScheduler()
    scheduler.add_job(
        lambda: asyncio.run(run_pipeline()),
        "cron",
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
    )
    print(f"Scheduler started. Cron: {CRON_SCHEDULE}")
    print("Press Ctrl+C to exit.")

    # Run once immediately on startup
    asyncio.run(run_pipeline())

    scheduler.start()


if __name__ == "__main__":
    main()
