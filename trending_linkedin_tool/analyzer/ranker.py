"""Rank topics by engagement and cross-platform presence."""

import logging
from collections import defaultdict

from trending_linkedin_tool.config import TOP_TOPICS_PER_CATEGORY
from trending_linkedin_tool.scrapers.base import ScrapedItem

logger = logging.getLogger(__name__)


class TopicRanker:
    """Ranks items within each category by a composite score."""

    def __init__(self, top_n: int | None = None):
        self.top_n = top_n or TOP_TOPICS_PER_CATEGORY

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Rough normalization for dedup purposes."""
        return title.lower().strip()

    def _deduplicate(self, items: list[ScrapedItem]) -> list[ScrapedItem]:
        """Merge duplicates: keep highest engagement, combine sources."""
        seen: dict[str, ScrapedItem] = {}
        source_counts: defaultdict[str, set[str]] = defaultdict(set)

        for item in items:
            norm = self._normalize_title(item.title)
            source_counts[norm].add(item.source)
            if norm not in seen or item.engagement > seen[norm].engagement:
                seen[norm] = item

        # Boost items appearing on multiple platforms
        for norm, item in seen.items():
            platform_count = len(source_counts[norm])
            if platform_count > 1:
                item.engagement = int(
                    item.engagement * (1 + 0.25 * platform_count)
                )

        return list(seen.values())

    def rank(
        self, categorized: dict[str, list[ScrapedItem]]
    ) -> dict[str, list[ScrapedItem]]:
        """Return top-N items per category, sorted by engagement descending."""
        ranked: dict[str, list[ScrapedItem]] = {}

        for cat_key, items in categorized.items():
            deduped = self._deduplicate(items)
            sorted_items = sorted(
                deduped, key=lambda x: x.engagement, reverse=True
            )
            ranked[cat_key] = sorted_items[: self.top_n]
            logger.info(
                "Category '%s': top %d of %d items",
                cat_key, len(ranked[cat_key]), len(deduped),
            )

        return ranked
