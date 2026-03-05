"""Scraper for Hacker News top stories."""

import logging

from trending_linkedin_tool.scrapers.base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
MAX_STORIES = 30


class HackerNewsScraper(BaseScraper):
    """Scrapes Hacker News top stories via the official Firebase API."""

    source_name = "hackernews"

    def scrape(self) -> list[ScrapedItem]:
        resp = self.fetch(HN_TOP_URL)
        if not resp:
            return []

        story_ids = resp.json()[:MAX_STORIES]
        items: list[ScrapedItem] = []

        for sid in story_ids:
            item_resp = self.fetch(HN_ITEM_URL.format(sid))
            if not item_resp:
                continue
            story = item_resp.json()
            if not story or story.get("type") != "story":
                continue

            title = story.get("title", "")
            url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
            score = story.get("score", 0)

            items.append(
                ScrapedItem(
                    title=title,
                    url=url,
                    source=self.source_name,
                    engagement=score,
                    description="",
                    tags=[],
                )
            )

        logger.info("Hacker News: scraped %d stories", len(items))
        return items
