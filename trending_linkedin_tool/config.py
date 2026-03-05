"""Configuration for the trending topics scraper and post generator."""

# Frequency: "daily" or "weekly"
SCRAPE_FREQUENCY = "daily"

# Platforms to generate posts for
PLATFORMS = ["linkedin", "twitter"]

# Categories to track
CATEGORIES = {
    "software_development": {
        "label": "Software Development",
        "keywords": [
            "programming", "software engineering", "devops", "microservices",
            "api", "database", "testing", "ci/cd", "docker", "kubernetes",
            "rust", "go", "python", "java", "typescript", "open source",
        ],
    },
    "web_development": {
        "label": "Web Development",
        "keywords": [
            "react", "nextjs", "vue", "angular", "svelte", "tailwind",
            "node", "deno", "bun", "css", "html", "javascript", "frontend",
            "backend", "fullstack", "web performance", "pwa", "webassembly",
        ],
    },
    "ai_development": {
        "label": "AI Development & Solutions",
        "keywords": [
            "ai", "machine learning", "llm", "gpt", "claude", "gemini",
            "deep learning", "neural network", "nlp", "computer vision",
            "rag", "fine-tuning", "transformer", "agent", "automation",
            "generative ai", "prompt engineering", "embedding",
        ],
    },
}

# Number of top trending topics per category
TOP_TOPICS_PER_CATEGORY = 7

# Number of posts to generate per platform
NUM_LINKEDIN_POSTS = 5
NUM_TWITTER_POSTS = 5

# Reddit subreddits to scrape
REDDIT_SUBREDDITS = ["programming", "webdev", "artificial", "MachineLearning"]

# Output directory
OUTPUT_DIR = "output"
