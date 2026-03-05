"""Generate LinkedIn post drafts from ranked trending topics."""

import logging
import random
from datetime import datetime

from trending_linkedin_tool.config import CATEGORIES, NUM_LINKEDIN_POSTS
from trending_linkedin_tool.scrapers.base import ScrapedItem

logger = logging.getLogger(__name__)

# Post templates — each is a (hook_template, body_template, cta_template) tuple.
# Placeholders: {title}, {description}, {category}, {engagement}, {source}
TEMPLATES = [
    {
        "hook": "This week's hottest trend in {category} caught my attention.",
        "body": (
            '"{title}" is generating massive buzz with {engagement}+ '
            "engagement points across platforms.\n\n"
            "{description}\n\n"
            "Here's why this matters for professionals:\n"
            "- It signals a shift in how we approach {category}\n"
            "- Early adopters will have a competitive edge\n"
            "- The community response shows real demand"
        ),
        "cta": "What's your take on this trend? Drop your thoughts below.",
    },
    {
        "hook": "Stop scrolling — {category} just had a big week.",
        "body": (
            "I've been tracking trending topics across GitHub, Dev.to, "
            "Hacker News, and Reddit.\n\n"
            'This week\'s standout: "{title}"\n\n'
            "{description}\n\n"
            "With {engagement}+ community signals, this isn't just hype — "
            "it's a direction worth paying attention to."
        ),
        "cta": "Follow me for weekly {category} trend insights. Repost if this was useful.",
    },
    {
        "hook": "The data doesn't lie. Here's what developers are talking about this week.",
        "body": (
            "After analyzing hundreds of posts across 4 platforms, "
            "one topic keeps coming up:\n\n"
            '→ "{title}"\n\n'
            "{description}\n\n"
            "Why it's trending:\n"
            "• {engagement}+ engagement on {source}\n"
            "• Aligns with the {category} movement\n"
            "• Practical applications are emerging fast"
        ),
        "cta": "Save this post for reference. What trends are you seeing in your work?",
    },
    {
        "hook": "If you work in {category}, you need to know about this.",
        "body": (
            '"{title}" just hit trending across multiple platforms.\n\n'
            "{description}\n\n"
            "This is the kind of signal that separates those who stay ahead "
            "from those who play catch-up.\n\n"
            "Key takeaway: The community ({engagement}+ signals) is voting "
            "with their attention — and this deserves yours too."
        ),
        "cta": "Agree or disagree? Let me know in the comments.",
    },
    {
        "hook": "Weekly {category} trend report — here's what's making waves.",
        "body": (
            "Every week I track what the developer community is buzzing about.\n\n"
            'Top pick this week: "{title}"\n\n'
            "{description}\n\n"
            "Platform signal: {engagement}+ engagement on {source}\n\n"
            "Whether you're a seasoned dev or just getting started, "
            "staying on top of trends like this is essential."
        ),
        "cta": "Hit follow for weekly trend updates. What would you add to this list?",
    },
]

HASHTAG_MAP = {
    "software_development": [
        "#SoftwareDevelopment", "#Programming", "#DevOps",
        "#OpenSource", "#TechTrends", "#Coding",
    ],
    "web_development": [
        "#WebDevelopment", "#Frontend", "#JavaScript",
        "#React", "#WebDev", "#FullStack",
    ],
    "ai_development": [
        "#ArtificialIntelligence", "#MachineLearning", "#AI",
        "#GenerativeAI", "#LLM", "#DeepLearning",
    ],
}


class LinkedInPostGenerator:
    """Generates LinkedIn post drafts from trending topics."""

    def __init__(self, num_posts: int | None = None):
        self.num_posts = num_posts or NUM_LINKEDIN_POSTS

    def _pick_top_items(
        self, ranked: dict[str, list[ScrapedItem]]
    ) -> list[tuple[str, ScrapedItem]]:
        """Pick the top items across all categories for posts."""
        all_items: list[tuple[str, ScrapedItem]] = []
        for cat_key, items in ranked.items():
            for item in items:
                all_items.append((cat_key, item))

        # Sort by engagement, take top N
        all_items.sort(key=lambda x: x[1].engagement, reverse=True)
        # Ensure category diversity: pick from different categories
        selected: list[tuple[str, ScrapedItem]] = []
        cats_used: set[str] = set()

        # First pass: one per category
        for cat_key, item in all_items:
            if cat_key not in cats_used and len(selected) < self.num_posts:
                selected.append((cat_key, item))
                cats_used.add(cat_key)

        # Second pass: fill remaining slots with top engagement
        for cat_key, item in all_items:
            if len(selected) >= self.num_posts:
                break
            if (cat_key, item) not in selected:
                selected.append((cat_key, item))

        return selected[: self.num_posts]

    def generate(self, ranked: dict[str, list[ScrapedItem]]) -> list[dict]:
        """Generate LinkedIn post drafts.

        Returns a list of dicts with keys: hook, body, cta, hashtags, source_item
        """
        top_items = self._pick_top_items(ranked)
        posts: list[dict] = []
        used_templates = random.sample(
            TEMPLATES, min(len(TEMPLATES), len(top_items))
        )

        for i, (cat_key, item) in enumerate(top_items):
            template = used_templates[i % len(used_templates)]
            category_label = CATEGORIES[cat_key]["label"]

            source_display = item.source.replace("_", " ").title()
            description = item.description or "A breakthrough that's reshaping the landscape."

            format_args = {
                "title": item.title,
                "description": description,
                "category": category_label,
                "engagement": f"{item.engagement:,}",
                "source": source_display,
            }

            hook = template["hook"].format(**format_args)
            body = template["body"].format(**format_args)
            cta = template["cta"].format(**format_args)

            # Pick 3-4 relevant hashtags
            hashtags = HASHTAG_MAP.get(cat_key, ["#Tech", "#Trending"])
            selected_tags = random.sample(
                hashtags, min(4, len(hashtags))
            )

            full_post = f"{hook}\n\n{body}\n\n{cta}\n\n{' '.join(selected_tags)}"

            posts.append(
                {
                    "post_number": i + 1,
                    "category": category_label,
                    "hook": hook,
                    "body": body,
                    "cta": cta,
                    "hashtags": selected_tags,
                    "full_post": full_post,
                    "source_title": item.title,
                    "source_url": item.url,
                    "engagement": item.engagement,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

        logger.info("Generated %d LinkedIn post drafts", len(posts))
        return posts
