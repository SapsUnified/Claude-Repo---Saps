"""Categorize scraped items into configured topic categories."""

import logging

from trending_linkedin_tool.config import CATEGORIES
from trending_linkedin_tool.scrapers.base import ScrapedItem

logger = logging.getLogger(__name__)


class TopicCategorizer:
    """Assigns scraped items to one or more categories based on keyword matching."""

    def __init__(self, categories: dict | None = None):
        self.categories = categories or CATEGORIES

    def categorize(
        self, items: list[ScrapedItem]
    ) -> dict[str, list[ScrapedItem]]:
        """Return a dict mapping category keys to lists of matching items."""
        result: dict[str, list[ScrapedItem]] = {
            key: [] for key in self.categories
        }

        for item in items:
            searchable = " ".join(
                [
                    item.title.lower(),
                    item.description.lower(),
                    " ".join(item.tags),
                ]
            )
            matched = False
            for cat_key, cat_info in self.categories.items():
                for keyword in cat_info["keywords"]:
                    if keyword in searchable:
                        result[cat_key].append(item)
                        matched = True
                        break  # one match per category is enough

            if not matched:
                # Put uncategorized items in software_development as a fallback
                # if they come from tech sources
                if item.source in ("github_trending", "hackernews"):
                    result["software_development"].append(item)

        for cat_key, cat_items in result.items():
            logger.info(
                "Category '%s': %d items",
                self.categories[cat_key]["label"],
                len(cat_items),
            )

        return result
