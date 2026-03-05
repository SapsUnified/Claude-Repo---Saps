# Trending Topics Scraper & LinkedIn Post Recommender

A Python tool that scrapes weekly trending topics from developer platforms and generates ready-to-post LinkedIn drafts.

## What It Does

1. **Scrapes** 4 platforms: GitHub Trending, Dev.to, Hacker News, Reddit
2. **Categorizes** topics into: Software Development, Web Development, AI Development & Solutions
3. **Ranks** by engagement with cross-platform boosting
4. **Generates** 5 LinkedIn post drafts with hooks, insights, CTAs, and hashtags

## Quick Start

```bash
# Install dependencies
pip install -r trending_linkedin_tool/requirements.txt

# Run the tool
python -m trending_linkedin_tool

# Custom output directory
python -m trending_linkedin_tool --output-dir my_reports
```

## Output

The tool generates two files in the `output/` directory:

- `trending_topics_YYYY-MM-DD.json` — Top trending topics per category
- `linkedin_posts_YYYY-MM-DD.json` — 5 LinkedIn post drafts

Plus a formatted console summary.

## Project Structure

```
trending_linkedin_tool/
├── scrapers/
│   ├── base.py               # Base scraper with retry logic
│   ├── github_trending.py    # GitHub Trending repos (weekly)
│   ├── devto_scraper.py      # Dev.to top articles (7-day)
│   ├── hackernews_scraper.py # Hacker News top stories
│   └── reddit_scraper.py     # Reddit tech subreddits (weekly)
├── analyzer/
│   ├── categorizer.py        # Keyword-based topic categorization
│   └── ranker.py             # Engagement ranking + dedup
├── generator/
│   └── linkedin_posts.py     # LinkedIn post draft generator
├── config.py                 # Categories, keywords, settings
├── main.py                   # Pipeline entry point
└── requirements.txt          # Python dependencies
```

## Configuration

Edit `config.py` to:
- Add/modify topic **categories** and **keywords**
- Change the number of **top topics** per category
- Change the number of **LinkedIn posts** generated
- Add/remove **Reddit subreddits**

## Scheduling (Optional)

To run weekly, add a cron job:

```bash
# Every Monday at 9 AM
0 9 * * 1 cd /path/to/repo && python -m trending_linkedin_tool
```

## Requirements

- Python 3.10+
- `requests`, `beautifulsoup4`, `feedparser`, `schedule`, `jinja2`, `python-dotenv`
