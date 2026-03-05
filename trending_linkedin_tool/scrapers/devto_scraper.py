"""Scraper for Dev.to top articles (past day)."""

import logging

from trending_linkedin_tool.scrapers.base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)

DEVTO_API_URL = "https://dev.to/api/articles?top=1&per_page=30"


class DevToScraper(BaseScraper):
    """Scrapes Dev.to top articles from the past day via their public API."""

    source_name = "devto"

    def scrape(self) -> list[ScrapedItem]:
        resp = self.fetch(DEVTO_API_URL)
        if not resp:
            return []

        articles = resp.json()
        items: list[ScrapedItem] = []

        for article in articles:
            tags = [t.strip().lower() for t in article.get("tag_list", [])]
            items.append(
                ScrapedItem(
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    source=self.source_name,
                    engagement=article.get("positive_reactions_count", 0),
                    description=article.get("description", ""),
                    tags=tags,
                )
            )

        logger.info("Dev.to: scraped %d articles", len(items))
        return items
