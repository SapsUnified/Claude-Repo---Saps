"""Scraper for Reddit top posts from tech subreddits (via public JSON API)."""

import logging

from trending_linkedin_tool.scrapers.base import BaseScraper, ScrapedItem
from trending_linkedin_tool.config import REDDIT_SUBREDDITS

logger = logging.getLogger(__name__)

REDDIT_URL = "https://www.reddit.com/r/{}/top.json?t=day&limit=15"


class RedditScraper(BaseScraper):
    """Scrapes Reddit top daily posts from configured subreddits."""

    source_name = "reddit"

    def scrape(self) -> list[ScrapedItem]:
        items: list[ScrapedItem] = []

        for sub in REDDIT_SUBREDDITS:
            resp = self.fetch(REDDIT_URL.format(sub))
            if not resp:
                continue

            data = resp.json().get("data", {})
            children = data.get("children", [])

            for child in children:
                post = child.get("data", {})
                title = post.get("title", "")
                permalink = post.get("permalink", "")
                url = f"https://www.reddit.com{permalink}" if permalink else ""
                score = post.get("score", 0)
                flair = post.get("link_flair_text", "") or ""

                tags = [f"r/{sub}"]
                if flair:
                    tags.append(flair.lower())

                items.append(
                    ScrapedItem(
                        title=title,
                        url=url,
                        source=self.source_name,
                        engagement=score,
                        description=post.get("selftext", "")[:300],
                        tags=tags,
                    )
                )

            logger.info("Reddit r/%s: scraped %d posts", sub, len(children))

        logger.info("Reddit total: scraped %d posts", len(items))
        return items
