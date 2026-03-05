"""Scraper for GitHub Trending repositories."""

import logging

from bs4 import BeautifulSoup

from trending_linkedin_tool.scrapers.base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)

GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"


class GithubTrendingScraper(BaseScraper):
    """Scrapes GitHub's daily trending repositories page."""

    source_name = "github_trending"

    def scrape(self) -> list[ScrapedItem]:
        resp = self.fetch(GITHUB_TRENDING_URL)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items: list[ScrapedItem] = []

        for article in soup.select("article.Box-row"):
            # Repository name
            h2 = article.select_one("h2 a")
            if not h2:
                continue
            repo_path = h2.get("href", "").strip("/")
            title = repo_path.replace("/", " / ")
            url = f"https://github.com/{repo_path}"

            # Description
            p = article.select_one("p")
            description = p.get_text(strip=True) if p else ""

            # Stars this week
            engagement = 0
            stars_span = article.select("span.d-inline-block.float-sm-right")
            if stars_span:
                stars_text = stars_span[0].get_text(strip=True)
                stars_text = stars_text.replace(",", "").split()[0]
                try:
                    engagement = int(stars_text)
                except ValueError:
                    pass

            # Language tag
            tags = []
            lang_span = article.select_one(
                "span[itemprop='programmingLanguage']"
            )
            if lang_span:
                tags.append(lang_span.get_text(strip=True).lower())

            items.append(
                ScrapedItem(
                    title=title,
                    url=url,
                    source=self.source_name,
                    engagement=engagement,
                    description=description,
                    tags=tags,
                )
            )

        logger.info("GitHub Trending: scraped %d repos", len(items))
        return items
