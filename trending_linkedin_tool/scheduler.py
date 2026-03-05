#!/usr/bin/env python3
"""
Autopilot Scheduler — Runs the trending topics pipeline on a weekly schedule.

Usage:
    # Run once immediately, then weekly every Monday at 9 AM
    python -m trending_linkedin_tool.scheduler

    # Run only on a custom schedule
    python -m trending_linkedin_tool.scheduler --day monday --time 09:00

    # Run immediately without scheduling
    python -m trending_linkedin_tool.scheduler --once
"""

import argparse
import logging
import signal
import sys
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
    logger.info("AUTOPILOT: Starting scheduled pipeline run")
    logger.info("=" * 60)
    try:
        run()
        logger.info("AUTOPILOT: Pipeline completed successfully")
    except Exception:
        logger.exception("AUTOPILOT: Pipeline failed")


def start_scheduler(day: str = "monday", run_time: str = "09:00", run_now: bool = True):
    """Start the autopilot scheduler.

    Args:
        day: Day of the week to run (e.g., 'monday', 'wednesday').
        run_time: Time to run in HH:MM format (24-hour).
        run_now: If True, run the pipeline immediately before starting the schedule.
    """
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if run_now:
        logger.info("AUTOPILOT: Running initial pipeline immediately")
        run_job()

    # Schedule weekly run
    day_methods = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
    }

    scheduler_fn = day_methods.get(day.lower())
    if not scheduler_fn:
        logger.error("Invalid day: %s. Use a weekday name.", day)
        sys.exit(1)

    scheduler_fn.at(run_time).do(run_job)
    logger.info(
        "AUTOPILOT: Scheduled to run every %s at %s",
        day.capitalize(), run_time,
    )
    logger.info("AUTOPILOT: Waiting for next scheduled run... (Ctrl+C to stop)")

    while not _shutdown:
        schedule.run_pending()
        time.sleep(30)

    logger.info("AUTOPILOT: Scheduler stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Autopilot scheduler for trending topics pipeline"
    )
    parser.add_argument(
        "--day",
        default="monday",
        help="Day of the week to run (default: monday)",
    )
    parser.add_argument(
        "--time",
        default="09:00",
        dest="run_time",
        help="Time to run in HH:MM 24-hour format (default: 09:00)",
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
        day=args.day,
        run_time=args.run_time,
        run_now=not args.no_initial_run,
    )


if __name__ == "__main__":
    main()
