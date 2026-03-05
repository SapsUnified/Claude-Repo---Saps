#!/usr/bin/env python3
"""
Autopilot Scheduler — Runs the trending topics pipeline on a daily schedule.

Usage:
    # Run once immediately, then daily at 9 AM
    python -m trending_linkedin_tool.scheduler

    # Run at a custom time daily
    python -m trending_linkedin_tool.scheduler --time 14:00

    # Run immediately without scheduling
    python -m trending_linkedin_tool.scheduler --once
"""

import argparse
import logging
import signal
import time

import schedule

from trending_linkedin_tool.main import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Graceful shutdown flag
_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    logger.info("Received signal %s — shutting down gracefully", signum)
    _shutdown = True


def run_job():
    """Execute the full scraping pipeline."""
    logger.info("=" * 60)
    logger.info("AUTOPILOT: Starting scheduled daily pipeline run")
    logger.info("=" * 60)
    try:
        run()
        logger.info("AUTOPILOT: Pipeline completed successfully")
    except Exception:
        logger.exception("AUTOPILOT: Pipeline failed")


def start_scheduler(run_time: str = "09:00", run_now: bool = True):
    """Start the autopilot scheduler.

    Args:
        run_time: Time to run daily in HH:MM format (24-hour).
        run_now: If True, run the pipeline immediately before starting the schedule.
    """
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if run_now:
        logger.info("AUTOPILOT: Running initial pipeline immediately")
        run_job()

    # Schedule daily run
    schedule.every().day.at(run_time).do(run_job)
    logger.info("AUTOPILOT: Scheduled to run daily at %s", run_time)
    logger.info("AUTOPILOT: Waiting for next scheduled run... (Ctrl+C to stop)")

    while not _shutdown:
        schedule.run_pending()
        time.sleep(30)

    logger.info("AUTOPILOT: Scheduler stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Daily autopilot scheduler for trending topics pipeline"
    )
    parser.add_argument(
        "--time",
        default="09:00",
        dest="run_time",
        help="Time to run daily in HH:MM 24-hour format (default: 09:00)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the pipeline once immediately and exit (no scheduling)",
    )
    parser.add_argument(
        "--no-initial-run",
        action="store_true",
        help="Skip the initial immediate run; only run on schedule",
    )
    args = parser.parse_args()

    if args.once:
        run_job()
        return

    start_scheduler(
        run_time=args.run_time,
        run_now=not args.no_initial_run,
    )


if __name__ == "__main__":
    main()
