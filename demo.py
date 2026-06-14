"""One-command demo: scrape the bundled fixture -> CSV + dashboard, print a summary.

    python demo.py

Works with NO network and NO API key — it parses the offline HTML fixture in
sample_data/page.html. Use `python -m src.cli --live` to scrape the real site.
"""
from __future__ import annotations

from pathlib import Path

# Load .env if python-dotenv is installed (optional convenience).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from src.cli import DEFAULT_CSV, DEFAULT_DASHBOARD, run_pipeline


def main() -> None:
    print("=== Scraper -> Dashboard demo — OFFLINE fixture (no network needed) ===\n")

    df = run_pipeline(live=False, out=DEFAULT_CSV, dashboard=DEFAULT_DASHBOARD)

    print(df.to_string(index=False))
    print()
    print(f"Scraped {len(df)} products.")
    print(f"  Avg price:  {df['price'].mean():.2f}")
    print(f"  Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
    print()
    print(f"CSV written to:       {Path(DEFAULT_CSV).relative_to(Path.cwd()) if DEFAULT_CSV.is_relative_to(Path.cwd()) else DEFAULT_CSV}")
    print(f"Dashboard written to: {Path(DEFAULT_DASHBOARD).relative_to(Path.cwd()) if DEFAULT_DASHBOARD.is_relative_to(Path.cwd()) else DEFAULT_DASHBOARD}")
    print("\nOpen dashboard/index.html in your browser to see the chart + table.")


if __name__ == "__main__":
    main()
