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

## Autopilot Deployment

### Option 1: Built-in Scheduler

```bash
# Run now + schedule weekly every Monday at 9 AM
python -m trending_linkedin_tool.scheduler

# Custom day and time
python -m trending_linkedin_tool.scheduler --day wednesday --time 14:00

# Run once and exit (no scheduling)
python -m trending_linkedin_tool.scheduler --once

# Skip initial run, only run on schedule
python -m trending_linkedin_tool.scheduler --no-initial-run
```

### Option 2: Docker (Recommended for Production)

```bash
# Build and run with docker-compose (runs autopilot scheduler)
docker compose up -d

# View logs
docker compose logs -f

# Run once via Docker
docker run --rm -v $(pwd)/output:/app/output trending-linkedin python -m trending_linkedin_tool --once
```

### Option 3: GitHub Actions (Serverless)

The repository includes a `.github/workflows/weekly-trends.yml` workflow that:
- Runs every Monday at 9 AM UTC automatically
- Can be triggered manually from the Actions tab
- Saves results as downloadable artifacts (retained 90 days)
- Commits results back to the repository

### Option 4: System Cron

```bash
# Every Monday at 9 AM
0 9 * * 1 cd /path/to/repo && python -m trending_linkedin_tool
```

## Requirements

- Python 3.10+
- `requests`, `beautifulsoup4`, `feedparser`, `schedule`, `jinja2`, `python-dotenv`
