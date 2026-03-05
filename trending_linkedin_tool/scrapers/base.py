"""Base scraper class with common functionality."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; TrendingTopicsScraper/1.0; "
        "+https://github.com/SapsUnified/Claude-Repo---Saps)"
    ),
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds


@dataclass
class ScrapedItem:
    """A single scraped topic/article."""

    title: str
    url: str
    source: str
    engagement: int = 0  # stars, upvotes, reactions, etc.
    description: str = ""
    tags: list[str] = field(default_factory=list)
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseScraper:
    """Base class for all scrapers."""

    source_name: str = "unknown"

    def fetch(self, url: str) -> requests.Response | None:
        """Fetch a URL with retries and backoff."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                logger.warning(
                    "Attempt %d/%d failed for %s: %s",
                    attempt, MAX_RETRIES, url, exc,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF * attempt)
        logger.error("All retries exhausted for %s", url)
        return None

    def scrape(self) -> list[ScrapedItem]:
        """Scrape and return a list of items. Override in subclasses."""
        raise NotImplementedError
