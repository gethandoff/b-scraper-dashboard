"""Clean: raw scraped dicts -> a tidy pandas DataFrame -> CSV.

Cleaning rules:
- price "£51.77" -> 51.77 (float)
- rating "Three" -> 3 (int 1-5)
- availability / title -> whitespace-stripped strings
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# Maps the star-rating words used on books.toscrape.com to integers.
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(raw: str) -> float:
    """'£51.77' (or '$51.77', 'USD 51.77') -> 51.77. Returns 0.0 if no number found."""
    match = re.search(r"\d+(?:\.\d+)?", str(raw))
    return float(match.group()) if match else 0.0


def parse_rating(raw: str) -> int:
    """'Three' -> 3. Falls back to a digit if present, else 0."""
    word = str(raw).strip().title()
    if word in RATING_WORDS:
        return RATING_WORDS[word]
    match = re.search(r"[1-5]", word)
    return int(match.group()) if match else 0


def clean(products: list[dict]) -> pd.DataFrame:
    """Turn the scraper's raw dicts into a cleaned, typed DataFrame."""
    df = pd.DataFrame(products, columns=["title", "price", "availability", "rating"])

    df["title"] = df["title"].astype(str).str.strip()
    df["availability"] = df["availability"].astype(str).str.strip()
    df["price"] = df["price"].apply(parse_price)
    df["rating"] = df["rating"].apply(parse_rating)

    return df


def write_csv(df: pd.DataFrame, out: str | Path) -> Path:
    """Write the cleaned DataFrame to CSV, creating parent dirs as needed."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    return out
