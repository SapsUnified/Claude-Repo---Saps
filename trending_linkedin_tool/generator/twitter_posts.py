"""Generate Twitter/X post drafts from ranked trending topics."""

import logging
import random
from datetime import datetime

from trending_linkedin_tool.config import CATEGORIES, NUM_TWITTER_POSTS
from trending_linkedin_tool.scrapers.base import ScrapedItem

logger = logging.getLogger(__name__)

# Twitter templates — short, punchy, within 280 chars.
# Placeholders: {title}, {description_short}, {category}, {engagement}, {source}
TEMPLATES = [
    {
        "body": (
            "Trending in {category} today:\n\n"
            '"{title}"\n\n'
            "{engagement}+ engagement across platforms.\n\n"
            "This one's worth your attention."
        ),
    },
    {
        "body": (
            "Today's dev signal you shouldn't miss:\n\n"
            "{title}\n\n"
            "{description_short}\n\n"
            "The community is paying attention. Are you?"
        ),
    },
    {
        "body": (
            "What developers are buzzing about today:\n\n"
            "-> {title}\n\n"
            "{engagement}+ signals on {source}.\n\n"
            "Bookmark this."
        ),
    },
    {
        "body": (
            "{category} update:\n\n"
            "{title} is trending hard today.\n\n"
            "{description_short}"
        ),
    },
    {
        "body": (
            "Daily {category} trend alert:\n\n"
            '"{title}"\n\n'
            "Already at {engagement}+ engagement.\n\n"
            "Early signal. Pay attention."
        ),
    },
]

HASHTAG_MAP = {
    "software_development": [
        "#SoftwareDev", "#Programming", "#DevOps",
        "#OpenSource", "#TechTrends", "#Coding",
    ],
    "web_development": [
        "#WebDev", "#Frontend", "#JavaScript",
        "#React", "#FullStack", "#CSS",
    ],
    "ai_development": [
        "#AI", "#MachineLearning", "#LLM",
        "#GenAI", "#DeepLearning", "#Tech",
    ],
}


class TwitterPostGenerator:
    """Generates Twitter/X post drafts from trending topics."""

    MAX_TWEET_LENGTH = 280

    def __init__(self, num_posts: int | None = None):
        self.num_posts = num_posts or NUM_TWITTER_POSTS

    def _pick_top_items(
        self, ranked: dict[str, list[ScrapedItem]]
    ) -> list[tuple[str, ScrapedItem]]:
        """Pick the top items across all categories for posts."""
        all_items: list[tuple[str, ScrapedItem]] = []
        for cat_key, items in ranked.items():
            for item in items:
                all_items.append((cat_key, item))

        all_items.sort(key=lambda x: x[1].engagement, reverse=True)

        # Ensure category diversity
        selected: list[tuple[str, ScrapedItem]] = []
        cats_used: set[str] = set()

        for cat_key, item in all_items:
            if cat_key not in cats_used and len(selected) < self.num_posts:
                selected.append((cat_key, item))
                cats_used.add(cat_key)

        for cat_key, item in all_items:
            if len(selected) >= self.num_posts:
                break
            if (cat_key, item) not in selected:
                selected.append((cat_key, item))

        return selected[: self.num_posts]

    def _truncate_to_fit(self, text: str, hashtags_str: str) -> str:
        """Ensure tweet + hashtags fit within 280 characters."""
        max_body = self.MAX_TWEET_LENGTH - len(hashtags_str) - 2  # 2 for \n\n
        if len(text) > max_body:
            text = text[: max_body - 3] + "..."
        return text

    def generate(self, ranked: dict[str, list[ScrapedItem]]) -> list[dict]:
        """Generate Twitter/X post drafts."""
        top_items = self._pick_top_items(ranked)
        posts: list[dict] = []
        used_templates = random.sample(
            TEMPLATES, min(len(TEMPLATES), len(top_items))
        )

        for i, (cat_key, item) in enumerate(top_items):
            template = used_templates[i % len(used_templates)]
            category_label = CATEGORIES[cat_key]["label"]
            source_display = item.source.replace("_", " ").title()
            description = item.description or "A must-watch development."
            description_short = description[:80] + ("..." if len(description) > 80 else "")

            format_args = {
                "title": item.title[:80],
                "description_short": description_short,
                "category": category_label,
                "engagement": f"{item.engagement:,}",
                "source": source_display,
            }

            body = template["body"].format(**format_args)

            # Pick 2-3 hashtags for Twitter
            hashtags = HASHTAG_MAP.get(cat_key, ["#Tech", "#Trending"])
            selected_tags = random.sample(hashtags, min(3, len(hashtags)))
            hashtags_str = " ".join(selected_tags)

            body = self._truncate_to_fit(body, hashtags_str)
            full_tweet = f"{body}\n\n{hashtags_str}"

            posts.append(
                {
                    "post_number": i + 1,
                    "platform": "twitter",
                    "category": category_label,
                    "body": body,
                    "hashtags": selected_tags,
                    "full_post": full_tweet,
                    "char_count": len(full_tweet),
                    "source_title": item.title,
                    "source_url": item.url,
                    "engagement": item.engagement,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

        logger.info("Generated %d Twitter/X post drafts", len(posts))
        return posts
