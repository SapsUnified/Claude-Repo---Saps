"""Scraper for Twitter/X trending tech topics.

Uses two strategies:
1. Primary: Scrapes tech-related trending topics from Twitter's explore page
   via public endpoints (no API key needed).
2. Fallback: Searches curated tech hashtags for high-engagement tweets.

Note: For production use with higher rate limits, set the TWITTER_BEARER_TOKEN
environment variable to use the official Twitter API v2.
"""

import logging
import os

from trending_linkedin_tool.scrapers.base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)

# Curated tech search queries to find trending discussions on X
TECH_SEARCH_QUERIES = [
    "software development",
    "web development",
    "AI artificial intelligence",
    "machine learning LLM",
    "open source trending",
    "developer tools",
]

# Twitter API v2 endpoints
TWITTER_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
TWITTER_TRENDS_URL = "https://api.twitter.com/2/trends/by/woeid/{woeid}"
US_WOEID = 23424977  # United States


class TwitterScraper(BaseScraper):
    """Scrapes Twitter/X for trending tech topics.

    Supports two modes:
    - With TWITTER_BEARER_TOKEN env var: Uses official Twitter API v2
    - Without: Scrapes Twitter's public syndication/search endpoints
    """

    source_name = "twitter"

    def __init__(self):
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")

    def _scrape_via_api(self) -> list[ScrapedItem]:
        """Scrape using the official Twitter API v2 (requires bearer token)."""
        items: list[ScrapedItem] = []

        for query in TECH_SEARCH_QUERIES:
            params = (
                f"?query={query} lang:en -is:retweet&"
                f"max_results=10&"
                f"tweet.fields=public_metrics,created_at,entities&"
                f"sort_order=relevancy"
            )
            url = TWITTER_SEARCH_URL + params

            import requests
            try:
                resp = requests.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.bearer_token}",
                        "User-Agent": "TrendingTopicsScraper/1.0",
                    },
                    timeout=15,
                )
                resp.raise_for_status()
            except requests.RequestException as exc:
                logger.warning("Twitter API request failed for '%s': %s", query, exc)
                continue

            data = resp.json().get("data", [])
            for tweet in data:
                text = tweet.get("text", "")
                tweet_id = tweet.get("id", "")
                metrics = tweet.get("public_metrics", {})
                engagement = (
                    metrics.get("like_count", 0)
                    + metrics.get("retweet_count", 0) * 2
                    + metrics.get("reply_count", 0)
                )

                # Extract hashtags as tags
                entities = tweet.get("entities", {})
                hashtags = entities.get("hashtags", [])
                tags = [f"#{h['tag'].lower()}" for h in hashtags]

                tweet_url = f"https://x.com/i/status/{tweet_id}"

                items.append(
                    ScrapedItem(
                        title=text[:120],
                        url=tweet_url,
                        source=self.source_name,
                        engagement=engagement,
                        description=text,
                        tags=tags,
                    )
                )

            logger.info("Twitter API '%s': found %d tweets", query, len(data))

        return items

    def _scrape_via_syndication(self) -> list[ScrapedItem]:
        """Scrape using Twitter's public syndication API (no auth needed).

        Uses the public syndication timeline endpoint to fetch tweets
        from curated tech accounts and hashtag searches.
        """
        items: list[ScrapedItem] = []

        # Twitter syndication search endpoint (public, no auth)
        syndication_url = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{}"

        # Curated influential tech accounts to check daily
        tech_accounts = [
            "github", "veraborners", "stackblitz", "nextjs",
            "openaborni", "huggingface", "GoogleAI",
        ]

        for account in tech_accounts:
            resp = self.fetch(syndication_url.format(account))
            if not resp:
                continue

            # The syndication endpoint returns HTML with embedded tweet data
            # Parse the text content for tweet information
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")

            for tweet_div in soup.select("div.timeline-Tweet"):
                text_el = tweet_div.select_one("p.timeline-Tweet-text")
                if not text_el:
                    continue

                text = text_el.get_text(strip=True)
                link_el = tweet_div.select_one("a.timeline-Tweet-timestamp")
                tweet_url = link_el.get("href", "") if link_el else ""

                # Extract engagement from aria labels or metrics spans
                likes_el = tweet_div.select_one(
                    "span.TweetAction--heart .TweetAction-stat"
                )
                likes = 0
                if likes_el:
                    try:
                        likes = int(likes_el.get_text(strip=True).replace(",", ""))
                    except ValueError:
                        pass

                items.append(
                    ScrapedItem(
                        title=text[:120],
                        url=tweet_url,
                        source=self.source_name,
                        engagement=likes,
                        description=text,
                        tags=[f"@{account}"],
                    )
                )

            logger.info("Twitter syndication @%s: parsed tweets", account)

        return items

    def scrape(self) -> list[ScrapedItem]:
        """Scrape Twitter/X using the best available method."""
        if self.bearer_token:
            logger.info("Twitter: using official API v2 (bearer token found)")
            items = self._scrape_via_api()
        else:
            logger.info(
                "Twitter: no TWITTER_BEARER_TOKEN set, using public syndication. "
                "Set the env var for better results."
            )
            items = self._scrape_via_syndication()

        # Deduplicate by tweet URL
        seen_urls: set[str] = set()
        unique_items: list[ScrapedItem] = []
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)

        logger.info("Twitter: scraped %d unique items", len(unique_items))
        return unique_items
