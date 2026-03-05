"""Flask web dashboard for viewing trending topics and downloading reports."""

import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, send_file, jsonify, request

from trending_linkedin_tool.config import CATEGORIES, OUTPUT_DIR
from trending_linkedin_tool.scrapers import (
    DevToScraper,
    GithubTrendingScraper,
    HackerNewsScraper,
    RedditScraper,
    TwitterScraper,
)
from trending_linkedin_tool.analyzer.categorizer import TopicCategorizer
from trending_linkedin_tool.analyzer.ranker import TopicRanker
from trending_linkedin_tool.generator.linkedin_posts import LinkedInPostGenerator
from trending_linkedin_tool.generator.twitter_posts import TwitterPostGenerator
from trending_linkedin_tool.generator.report_exporter import ReportExporter

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)

# In-memory store for the latest pipeline results
_latest_data: dict = {}
_pipeline_running = False
_pipeline_lock = threading.Lock()


def _run_pipeline(output_dir: str) -> dict:
    """Run the scraping pipeline and return results."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    scrapers = [
        GithubTrendingScraper(),
        DevToScraper(),
        HackerNewsScraper(),
        RedditScraper(),
        TwitterScraper(),
    ]

    all_items = []
    for scraper in scrapers:
        try:
            items = scraper.scrape()
            all_items.extend(items)
        except Exception:
            logger.exception("Scraper %s failed", scraper.source_name)

    if not all_items:
        return {"error": "No items scraped from any source."}

    categorizer = TopicCategorizer()
    categorized = categorizer.categorize(all_items)

    ranker = TopicRanker()
    ranked = ranker.rank(categorized)

    linkedin_generator = LinkedInPostGenerator()
    linkedin_posts = linkedin_generator.generate(ranked)

    twitter_generator = TwitterPostGenerator()
    twitter_posts = twitter_generator.generate(ranked)

    trending_report = {}
    for cat_key, items in ranked.items():
        trending_report[CATEGORIES[cat_key]["label"]] = [
            {
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "engagement": item.engagement,
                "tags": item.tags,
            }
            for item in items
        ]

    # Save downloadable files
    exporter = ReportExporter()
    excel_path = exporter.save_excel(
        output_dir, timestamp, trending_report, linkedin_posts, twitter_posts
    )
    text_path = exporter.save_text(
        output_dir, timestamp, trending_report, linkedin_posts, twitter_posts
    )

    return {
        "timestamp": timestamp,
        "trending_report": trending_report,
        "linkedin_posts": linkedin_posts,
        "twitter_posts": twitter_posts,
        "excel_path": excel_path,
        "text_path": text_path,
        "total_items": len(all_items),
    }


def _load_latest_from_disk(output_dir: str) -> dict | None:
    """Try to load the most recent report files from disk."""
    output_path = Path(output_dir)
    if not output_path.exists():
        return None

    # Find most recent Excel report
    excel_files = sorted(output_path.glob("daily_report_*.xlsx"), reverse=True)
    text_files = sorted(output_path.glob("daily_report_*.txt"), reverse=True)

    if not excel_files:
        return None

    latest_excel = excel_files[0]
    # Extract timestamp from filename: daily_report_YYYY-MM-DD.xlsx
    timestamp = latest_excel.stem.replace("daily_report_", "")

    # Read the text report to extract data for display
    text_path = text_files[0] if text_files else None
    text_content = ""
    if text_path:
        text_content = text_path.read_text(encoding="utf-8")

    return {
        "timestamp": timestamp,
        "excel_path": str(latest_excel),
        "text_path": str(text_path) if text_path else None,
        "text_content": text_content,
        "from_cache": True,
    }


# --- Routes ---


@app.route("/")
def dashboard():
    """Main dashboard page."""
    return render_template("dashboard.html", data=_latest_data)


@app.route("/api/refresh", methods=["POST"])
def refresh_data():
    """Run the pipeline and refresh data."""
    global _latest_data, _pipeline_running

    with _pipeline_lock:
        if _pipeline_running:
            return jsonify({"status": "busy", "message": "Pipeline is already running."}), 409
        _pipeline_running = True

    try:
        output_dir = app.config.get("OUTPUT_DIR", OUTPUT_DIR)
        result = _run_pipeline(output_dir)
        _latest_data = result
        return jsonify({"status": "ok", "message": "Pipeline completed.", "data": result})
    except Exception as exc:
        logger.exception("Pipeline failed")
        return jsonify({"status": "error", "message": str(exc)}), 500
    finally:
        with _pipeline_lock:
            _pipeline_running = False


@app.route("/api/data")
def get_data():
    """Return the latest data as JSON (for AJAX refresh)."""
    return jsonify(_latest_data)


@app.route("/api/status")
def get_status():
    """Return pipeline status."""
    return jsonify({
        "running": _pipeline_running,
        "has_data": bool(_latest_data),
        "timestamp": _latest_data.get("timestamp", ""),
    })


@app.route("/download/excel")
def download_excel():
    """Download the latest Excel report."""
    path = _latest_data.get("excel_path")
    if not path or not os.path.exists(path):
        return "No report available. Run the pipeline first.", 404
    return send_file(
        path,
        as_attachment=True,
        download_name=f"daily_report_{_latest_data.get('timestamp', 'latest')}.xlsx",
    )


@app.route("/download/text")
def download_text():
    """Download the latest text report."""
    path = _latest_data.get("text_path")
    if not path or not os.path.exists(path):
        return "No report available. Run the pipeline first.", 404
    return send_file(
        path,
        as_attachment=True,
        download_name=f"daily_report_{_latest_data.get('timestamp', 'latest')}.txt",
    )


def create_app(output_dir: str | None = None) -> Flask:
    """Create and configure the Flask app."""
    global _latest_data

    output_dir = output_dir or OUTPUT_DIR
    app.config["OUTPUT_DIR"] = output_dir

    # Try to load existing data from disk
    cached = _load_latest_from_disk(output_dir)
    if cached:
        _latest_data = cached
        logger.info("Loaded cached report from %s", cached.get("timestamp"))

    return app


def main():
    """Run the web dashboard server."""
    import argparse

    parser = argparse.ArgumentParser(description="Trending Topics Web Dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory for reports")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    web_app = create_app(output_dir=args.output_dir)
    print(f"\n  Trending Topics Dashboard running at http://{args.host}:{args.port}")
    print(f"  Press Ctrl+C to stop\n")
    web_app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
