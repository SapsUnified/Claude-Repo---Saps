# CLAUDE.md — AI Assistant Guide for Claude-Repo---Saps

## Repository Overview

This is the **Claude-Repo---Saps** repository owned by **SapsUnified**. It contains a Python-based **Trending Topics Scraper & Social Post Recommender** tool that runs daily and generates posts for LinkedIn and Twitter/X.

- **Primary branch:** `master`
- **Remote:** `origin` (GitHub via SapsUnified organization)
- **Language:** Python 3.10+
- **Key dependencies:** `requests`, `beautifulsoup4`, `feedparser`, `schedule`
- **Frequency:** Daily (autopilot)

## Repository Structure

```
Claude-Repo---Saps/
├── CLAUDE.md                        # This file — AI assistant guidelines
├── README.md                        # Project description
├── .gitignore                       # Git ignore rules
├── Dockerfile                       # Container image definition
├── docker-compose.yml               # Docker Compose for autopilot mode
├── .github/workflows/
│   └── daily-trends.yml             # GitHub Actions daily automation
└── trending_linkedin_tool/          # Main application package
    ├── __init__.py
    ├── __main__.py                  # python -m entry point
    ├── main.py                      # Pipeline orchestrator
    ├── scheduler.py                 # Autopilot scheduler (daily cron)
    ├── config.py                    # Categories, keywords, settings
    ├── requirements.txt             # Python dependencies
    ├── README.md                    # Tool-specific documentation
    ├── scrapers/                    # Data collection layer
    │   ├── __init__.py
    │   ├── base.py                  # Base scraper + ScrapedItem dataclass
    │   ├── github_trending.py       # GitHub Trending (daily repos)
    │   ├── devto_scraper.py         # Dev.to top articles (daily)
    │   ├── hackernews_scraper.py    # Hacker News top stories (Firebase API)
    │   ├── reddit_scraper.py        # Reddit tech subreddits (daily top)
    │   └── twitter_scraper.py       # Twitter/X trending tech topics
    ├── analyzer/                    # Processing layer
    │   ├── __init__.py
    │   ├── categorizer.py           # Keyword-based topic categorization
    │   └── ranker.py                # Engagement ranking + deduplication
    └── generator/                   # Output layer
        ├── __init__.py
        ├── linkedin_posts.py        # LinkedIn post draft generator
        └── twitter_posts.py         # Twitter/X post draft generator (280 chars)
```

## Development Workflow

### Branching

- The default branch is `master`.
- Feature branches should follow the pattern: `feature/<description>`
- Bug fix branches: `fix/<description>`
- Claude-assisted branches use: `claude/<description>-<session-id>`

### Commits

- Write clear, descriptive commit messages.
- Use imperative mood (e.g., "Add feature" not "Added feature").
- Keep commits focused — one logical change per commit.

### Pull Requests

- PRs should target `master`.
- Include a summary of changes and testing done.

## Build & Run

```bash
# Install dependencies
pip install -r trending_linkedin_tool/requirements.txt

# Run the tool
python -m trending_linkedin_tool

# Run with custom output directory
python -m trending_linkedin_tool --output-dir my_reports
```

### Pipeline Flow

1. **Scrape** — Collects daily data from GitHub Trending, Dev.to, Hacker News, Reddit, Twitter/X
2. **Categorize** — Assigns topics to Software Dev / Web Dev / AI Dev categories
3. **Rank** — Sorts by engagement, deduplicates, boosts cross-platform items
4. **Generate** — Creates 5 LinkedIn + 5 Twitter/X post drafts with hooks, CTAs, and hashtags
5. **Output** — Saves JSON reports to `output/` directory

## Testing

No test framework is set up yet. When tests are added:
- Document the test runner and commands here.
- Ensure all tests pass before pushing.

## Code Style & Conventions

General guidelines:

- Keep code simple and readable.
- Avoid over-engineering — solve the problem at hand.
- Don't add unused imports, dead code, or speculative abstractions.

## Deployment / Autopilot

The tool supports 4 deployment modes:

1. **Built-in scheduler** — `python -m trending_linkedin_tool.scheduler` (runs daily in-process)
2. **Docker** — `docker compose up -d` (containerized autopilot with restart policy)
3. **GitHub Actions** — `.github/workflows/daily-trends.yml` (serverless, every day 9 AM UTC)
4. **System cron** — Standard crontab entry

### Environment Variables

- `TWITTER_BEARER_TOKEN` — (Optional) Twitter API v2 bearer token for better X data

## CI/CD

GitHub Actions workflow (`.github/workflows/daily-trends.yml`) runs the pipeline daily, uploads artifacts, and commits results to the repo.

## Key Guidelines for AI Assistants

1. **Read before writing.** Always read existing files before modifying them.
2. **Minimal changes.** Only change what is necessary to fulfill the request.
3. **No speculation.** Don't add features, error handling, or abstractions that weren't requested.
4. **Preserve intent.** Respect existing patterns and conventions in the codebase.
5. **Test your work.** Run any available tests/linters before considering work complete.
6. **Don't create unnecessary files.** Prefer editing existing files over creating new ones.
7. **Security first.** Never commit secrets, credentials, or `.env` files.
8. **Keep this file updated.** When the project structure or tooling changes significantly, update CLAUDE.md to reflect the current state.
