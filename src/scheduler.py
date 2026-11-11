"""
Scheduler & Main Entry Point for Weekly Finance & Agentic AI Intelligence Digest.

Supports immediate execution (--now), dry-run previewing (--dry-run),
and APScheduler weekly automation every Saturday at 09:00 AM IST (Asia/Kolkata).
"""

import argparse
from datetime import datetime
import logging
import os
import sys
import time

from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("FinanceMainScheduler")

# Import internal modules safely
try:
    from src.fetcher import FinanceNewsFetcher
    from src.synthesizer import FinanceNewsSynthesizer
    from src.mailer import FinanceDigestMailer
except ImportError:
    from fetcher import FinanceNewsFetcher
    from synthesizer import FinanceNewsSynthesizer
    from mailer import FinanceDigestMailer


def run_pipeline(dry_run: bool = False, hours_lookback: int = 168, max_stories: int = 10) -> bool:
    """Executes the complete weekly ingestion, synthesis, and delivery pipeline."""
    tz_name = os.getenv("TIMEZONE", "Asia/Kolkata")
    local_tz = pytz.timezone(tz_name)
    now_local = datetime.now(local_tz)
    date_str = now_local.strftime("%B %d, %Y")

    logger.info(f"=== STARTING WEEKLY FINANCE & AGENTIC AI BRIEFING PIPELINE [{date_str}] ===")
    logger.info(f"Configuration: Lookback={hours_lookback}h (7 days), Max Stories={max_stories}, Timezone={tz_name}")

    # Step 1: Ingestion & Deduplication
    logger.info("Step 1/3: Ingesting & deduplicating financial feeds across past 7 days...")
    fetcher = FinanceNewsFetcher(hours_lookback=hours_lookback)
    items = fetcher.fetch_all()
    logger.info(f"Pipeline step 1 complete: Ingested & deduplicated {len(items)} items.")

    # Step 2: Financial AI Synthesis & Filtering
    logger.info("Step 2/3: Synthesizing executive briefing via AI reasoning engine...")
    synthesizer = FinanceNewsSynthesizer(max_stories=max_stories)
    digest_content = synthesizer.synthesize(items, date_str)
    logger.info(
        f"Pipeline step 2 complete: Synthesized briefing with {len(digest_content.top_breakthroughs)} core stories and "
        f"{len(digest_content.notable_initiatives)} notable launches."
    )

    # Step 3: Formatting & Delivery
    logger.info("Step 3/3: Formatting executive briefing and executing delivery...")
    mailer = FinanceDigestMailer()
    success = mailer.send_digest(digest_content, dry_run=dry_run)
    if success:
        logger.info(f"=== WEEKLY FINANCE BRIEFING COMPLETED SUCCESSFULLY [{date_str}] ===")
    else:
        logger.warning(f"=== WEEKLY FINANCE BRIEFING COMPLETED WITH WARNINGS/FALLBACKS [{date_str}] ===")

    return success


def start_scheduler():
    """Configures and runs APScheduler for weekly execution every Saturday at 09:00 AM IST."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    tz_name = os.getenv("TIMEZONE", "Asia/Kolkata")
    local_tz = pytz.timezone(tz_name)

    scheduler = BlockingScheduler(timezone=local_tz)

    # Schedule: Every Saturday at 09:00 AM IST
    cron_trigger = CronTrigger(day_of_week="sat", hour=9, minute=0, timezone=local_tz)
    job = scheduler.add_job(
        run_pipeline,
        trigger=cron_trigger,
        kwargs={"dry_run": False, "hours_lookback": 168, "max_stories": 10},
        id="weekly_finance_ai_briefing",
        name="Weekly Finance & Agentic AI Briefing",
        replace_existing=True,
    )

    logger.info("======================================================================")
    logger.info(f"APScheduler initialized for Weekly Finance AI Briefing.")
    logger.info(f"Target Schedule: Every Saturday at 09:00 AM ({tz_name})")
    if job.next_run_time:
        logger.info(f"Next Scheduled Run: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("Scheduler running in foreground... Press Ctrl+C to terminate.")
    logger.info("======================================================================")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler gracefully stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Weekly Finance & Agentic AI Intelligence Digest (Every Saturday 09:00 AM IST)"
    )
    parser.add_argument("--now", action="store_true", help="Run full pipeline immediately")
    parser.add_argument("--schedule", action="store_true", help="Start background scheduler for weekly Saturday 09:00 AM execution")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline and write HTML/text output to output/ without sending email")
    parser.add_argument("--hours", type=int, default=168, help="Lookback window in hours (default: 168 = 7 days)")
    parser.add_argument("--max-stories", type=int, default=10, help="Maximum number of curated stories in digest (default: 10)")

    args = parser.parse_args()

    if args.schedule:
        start_scheduler()
    elif args.now or args.dry_run:
        run_pipeline(dry_run=args.dry_run, hours_lookback=args.hours, max_stories=args.max_stories)
    else:
        # Default action: run immediately in dry-run mode
        logger.info("No explicit flag provided. Running immediate pipeline in dry-run mode...")
        run_pipeline(dry_run=True, hours_lookback=args.hours, max_stories=args.max_stories)


if __name__ == "__main__":
    main()

