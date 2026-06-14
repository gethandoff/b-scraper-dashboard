"""Command-line interface: run the full scrape -> clean -> dashboard pipeline.

    python -m src.cli                      # offline (parses the bundled fixture)
    python -m src.cli --live               # scrape the real books.toscrape.com
    python -m src.cli --out data/products.csv
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .clean import clean, write_csv
from .dashboard import render_dashboard
from .scrape import scrape

ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "data" / "products.csv"
DEFAULT_DASHBOARD = ROOT / "dashboard" / "index.html"


def run_pipeline(live: bool, out: str | Path, dashboard: str | Path, pages: int = 3):
    """Scrape -> clean -> write CSV -> render dashboard. Returns the DataFrame."""
    products = scrape(live=live, pages=pages)
    df = clean(products)
    write_csv(df, out)
    render_dashboard(df, dashboard)
    return df


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scrape a site into a clean CSV + static HTML dashboard."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Scrape the real site over HTTP (default: parse the offline fixture).",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_CSV),
        help=f"CSV output path (default: {DEFAULT_CSV}).",
    )
    parser.add_argument(
        "--dashboard",
        default=str(DEFAULT_DASHBOARD),
        help=f"Dashboard HTML output path (default: {DEFAULT_DASHBOARD}).",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Number of catalogue pages to scrape in --live mode (default: 3).",
    )
    args = parser.parse_args(argv)

    # Optional TARGET_URL override (documented in .env.example) for live mode.
    if args.live and os.environ.get("TARGET_URL"):
        from . import scrape as scrape_mod

        scrape_mod.BASE_URL = os.environ["TARGET_URL"]

    df = run_pipeline(args.live, args.out, args.dashboard, pages=args.pages)

    mode = "LIVE" if args.live else "OFFLINE fixture"
    print(f"[{mode}] Scraped {len(df)} products.", file=sys.stderr)
    print(f"Wrote CSV -> {args.out}", file=sys.stderr)
    print(f"Wrote dashboard -> {args.dashboard}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
