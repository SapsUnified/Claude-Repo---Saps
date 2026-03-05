#!/usr/bin/env python3
"""
Trending Topics Scraper & Social Post Recommender

Scrapes GitHub Trending, Dev.to, Hacker News, Reddit, and Twitter/X for daily
trending topics in Software Development, Web Development, and AI.
Generates 5 ready-to-post drafts each for LinkedIn and Twitter/X.

Usage:
    python -m trending_linkedin_tool.main [--output-dir OUTPUT_DIR]
"""

import argparse
import logging
import os
from datetime import datetime

from trending_linkedin_tool.config import CATEGORIES, OUTPUT_DIR
from trending_linkedin_tool.scrapers import (
    DevToScraper,
    GithubTrendingScraper,
    HackerNewsScraper,
    RedditScraper,
    TwitterScraper,
)
from trending_linkedin_tool.analyzer.categorizer import TopicCategorizer
from trending_linkedin_tool.analyzer.ranker import TopicRanker
from trending_linkedin_tool.generator.linkedin_posts import LinkedInPostGenerator
from trending_linkedin_tool.generator.twitter_posts import TwitterPostGenerator
from trending_linkedin_tool.generator.report_exporter import ReportExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run(output_dir: str | None = None):
    """Run the full pipeline: scrape → categorize → rank → generate posts."""
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    # --- Step 1: Scrape all sources ---
    logger.info("=" * 60)
    logger.info("STEP 1: Scraping daily trending topics from all sources")
    logger.info("=" * 60)

    scrapers = [
        GithubTrendingScraper(),
        DevToScraper(),
        HackerNewsScraper(),
        RedditScraper(),
        TwitterScraper(),
    ]

    all_items = []
    for scraper in scrapers:
        try:
            items = scraper.scrape()
            all_items.extend(items)
        except Exception:
            logger.exception("Scraper %s failed", scraper.source_name)

    logger.info("Total scraped items: %d", len(all_items))

    if not all_items:
        logger.error("No items scraped. Exiting.")
        return

    # --- Step 2: Categorize ---
    logger.info("=" * 60)
    logger.info("STEP 2: Categorizing topics")
    logger.info("=" * 60)

    categorizer = TopicCategorizer()
    categorized = categorizer.categorize(all_items)

    # --- Step 3: Rank ---
    logger.info("=" * 60)
    logger.info("STEP 3: Ranking topics by engagement")
    logger.info("=" * 60)

    ranker = TopicRanker()
    ranked = ranker.rank(categorized)

    # --- Step 4: Generate posts for LinkedIn and Twitter ---
    logger.info("=" * 60)
    logger.info("STEP 4: Generating LinkedIn and Twitter/X post drafts")
    logger.info("=" * 60)

    linkedin_generator = LinkedInPostGenerator()
    linkedin_posts = linkedin_generator.generate(ranked)

    twitter_generator = TwitterPostGenerator()
    twitter_posts = twitter_generator.generate(ranked)

    # --- Step 5: Save outputs as Excel and text ---
    logger.info("=" * 60)
    logger.info("STEP 5: Saving results (Excel + text)")
    logger.info("=" * 60)

    # Build trending report dict for export
    trending_report = {}
    for cat_key, items in ranked.items():
        trending_report[CATEGORIES[cat_key]["label"]] = [
            {
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "engagement": item.engagement,
                "tags": item.tags,
            }
            for item in items
        ]

    exporter = ReportExporter()

    # Save Excel report (.xlsx)
    excel_path = exporter.save_excel(
        output_dir, timestamp, trending_report, linkedin_posts, twitter_posts
    )

    # Save plain-text report (.txt)
    text_path = exporter.save_text(
        output_dir, timestamp, trending_report, linkedin_posts, twitter_posts
    )

    # Print summary to console
    print("\n" + "=" * 60)
    print("  DAILY TRENDING TOPICS REPORT")
    print(f"  Generated: {timestamp}")
    print("=" * 60)

    for cat_label, items_data in trending_report.items():
        print(f"\n  {cat_label}")
        print("-" * 40)
        for i, item in enumerate(items_data, 1):
            print(f"  {i}. {item['title']}")
            print(f"     Engagement: {item['engagement']:,} | Source: {item['source']}")

    print("\n" + "=" * 60)
    print("  LINKEDIN POST RECOMMENDATIONS")
    print("=" * 60)

    for post in linkedin_posts:
        print(f"\n--- Post #{post['post_number']} ({post['category']}) ---")
        print(post["full_post"])
        print(f"\nSource: {post['source_url']}")
        print()

    print("\n" + "=" * 60)
    print("  TWITTER/X POST RECOMMENDATIONS")
    print("=" * 60)

    for post in twitter_posts:
        print(f"\n--- Tweet #{post['post_number']} ({post['category']}) [{post['char_count']} chars] ---")
        print(post["full_post"])
        print(f"\nSource: {post['source_url']}")
        print()

    print(f"\nReports saved to:")
    print(f"  Excel: {excel_path}")
    print(f"  Text:  {text_path}")
    return {
        "trending_report": trending_report,
        "linkedin_posts": linkedin_posts,
        "twitter_posts": twitter_posts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scrape daily trending dev topics and generate LinkedIn + Twitter posts"
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Directory to save output files (default: {OUTPUT_DIR})",
    )
    args = parser.parse_args()
    run(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
