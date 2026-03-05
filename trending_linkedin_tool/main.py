#!/usr/bin/env python3
"""
Trending Topics Scraper & LinkedIn Post Recommender

Scrapes GitHub Trending, Dev.to, Hacker News, and Reddit for weekly
trending topics in Software Development, Web Development, and AI.
Generates 5 ready-to-post LinkedIn drafts from the top trends.

Usage:
    python -m trending_linkedin_tool.main [--output-dir OUTPUT_DIR]
"""

import argparse
import json
import logging
import os
from datetime import datetime

from trending_linkedin_tool.config import CATEGORIES, OUTPUT_DIR
from trending_linkedin_tool.scrapers import (
    DevToScraper,
    GithubTrendingScraper,
    HackerNewsScraper,
    RedditScraper,
)
from trending_linkedin_tool.analyzer.categorizer import TopicCategorizer
from trending_linkedin_tool.analyzer.ranker import TopicRanker
from trending_linkedin_tool.generator.linkedin_posts import LinkedInPostGenerator

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
    logger.info("STEP 1: Scraping trending topics from all sources")
    logger.info("=" * 60)

    scrapers = [
        GithubTrendingScraper(),
        DevToScraper(),
        HackerNewsScraper(),
        RedditScraper(),
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

    # --- Step 4: Generate LinkedIn posts ---
    logger.info("=" * 60)
    logger.info("STEP 4: Generating LinkedIn post drafts")
    logger.info("=" * 60)

    generator = LinkedInPostGenerator()
    posts = generator.generate(ranked)

    # --- Step 5: Save outputs ---
    logger.info("=" * 60)
    logger.info("STEP 5: Saving results")
    logger.info("=" * 60)

    # Save trending topics report
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

    report_path = os.path.join(output_dir, f"trending_topics_{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(trending_report, f, indent=2, ensure_ascii=False)
    logger.info("Trending topics saved to: %s", report_path)

    # Save LinkedIn posts
    posts_path = os.path.join(output_dir, f"linkedin_posts_{timestamp}.json")
    with open(posts_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    logger.info("LinkedIn posts saved to: %s", posts_path)

    # Print summary to console
    print("\n" + "=" * 60)
    print("  WEEKLY TRENDING TOPICS REPORT")
    print(f"  Generated: {timestamp}")
    print("=" * 60)

    for cat_label, items_data in trending_report.items():
        print(f"\n📌 {cat_label}")
        print("-" * 40)
        for i, item in enumerate(items_data, 1):
            print(f"  {i}. {item['title']}")
            print(f"     Engagement: {item['engagement']:,} | Source: {item['source']}")

    print("\n" + "=" * 60)
    print("  LINKEDIN POST RECOMMENDATIONS")
    print("=" * 60)

    for post in posts:
        print(f"\n--- Post #{post['post_number']} ({post['category']}) ---")
        print(post["full_post"])
        print(f"\nSource: {post['source_url']}")
        print()

    print(f"\nFull results saved to: {output_dir}/")
    return {"trending_report": trending_report, "linkedin_posts": posts}


def main():
    parser = argparse.ArgumentParser(
        description="Scrape trending dev topics and generate LinkedIn posts"
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
