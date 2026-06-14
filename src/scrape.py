"""Scrape: fetch a books.toscrape.com listing and parse it into list[dict].

Two modes, mirroring the demo/CI split used across the portfolio:
- OFFLINE (default): parse the bundled `sample_data/page.html` fixture. No network.
- LIVE (`--live`): fetch the real catalogue pages over HTTP.

The parser targets the real books.toscrape.com markup, so the same code path
handles both the fixture and the live site:

    <article class="product_pod">
      <p class="star-rating Three">...</p>
      <h3><a title="A Light in the Attic">...</a></h3>
      <p class="price_color">£51.77</p>
      <p class="instock availability"> In stock </p>
    </article>
"""
from __future__ import annotations

import time
from pathlib import Path

import requests
from selectolax.parser import HTMLParser

# Default live target. Override with the TARGET_URL env var or the --live flag.
BASE_URL = "https://books.toscrape.com/catalogue/page-{n}.html"
FIXTURE = Path(__file__).parent.parent / "sample_data" / "page.html"

# A polite, identifiable User-Agent. Real clients should keep this honest.
HEADERS = {"User-Agent": "PortfolioScraperDemo/1.0 (+https://github.com/your-org)"}


def parse_html(html: str) -> list[dict]:
    """Parse listing HTML into a list of raw product dicts (strings, uncleaned).

    Cleaning (price -> float, rating word -> int) happens in src/clean.py so the
    scraping and cleaning concerns stay independent and individually testable.
    """
    tree = HTMLParser(html)
    products: list[dict] = []

    for pod in tree.css("article.product_pod"):
        title_node = pod.css_first("h3 a")
        # The full title lives in the `title` attribute (the visible text is truncated).
        title = title_node.attributes.get("title", "") if title_node else ""

        price_node = pod.css_first("p.price_color")
        price = price_node.text(strip=True) if price_node else ""

        avail_node = pod.css_first("p.instock.availability")
        availability = avail_node.text(strip=True) if avail_node else ""

        # Rating is encoded as a second class, e.g. "star-rating Three".
        rating_node = pod.css_first("p.star-rating")
        rating = ""
        if rating_node:
            classes = (rating_node.attributes.get("class") or "").split()
            rating = next((c for c in classes if c != "star-rating"), "")

        products.append(
            {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
            }
        )

    return products


def scrape_fixture(path: str | Path = FIXTURE) -> list[dict]:
    """OFFLINE mode: parse the bundled HTML fixture. Used by demo.py and tests."""
    html = Path(path).read_text(encoding="utf-8")
    return parse_html(html)


def scrape_live(pages: int = 3, base_url: str = BASE_URL, delay: float = 1.0) -> list[dict]:
    """LIVE mode: fetch the first `pages` catalogue pages over HTTP.

    A small delay between requests keeps us polite (see CUSTOMIZE.md on rate limits).
    """
    products: list[dict] = []
    for n in range(1, pages + 1):
        url = base_url.format(n=n)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        products.extend(parse_html(resp.text))
        if n < pages:
            time.sleep(delay)  # be a good citizen
    return products


def scrape(live: bool = False, pages: int = 3) -> list[dict]:
    """Entry point used by the CLI: dispatch to live or offline scraping."""
    return scrape_live(pages=pages) if live else scrape_fixture()
