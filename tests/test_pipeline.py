"""Proves the success criterion against the offline fixture (no network).

- parsing the fixture yields the expected number of products
- prices parse to floats
- ratings map to ints in 1-5
- the CSV is written
"""
from pathlib import Path

import pandas as pd

from src.clean import clean, parse_price, parse_rating, write_csv
from src.dashboard import render_dashboard
from src.scrape import scrape_fixture

EXPECTED_COUNT = 6  # number of <article class="product_pod"> in sample_data/page.html


def test_fixture_yields_expected_product_count():
    products = scrape_fixture()
    assert len(products) == EXPECTED_COUNT
    # First product matches the fixture exactly.
    assert products[0]["title"] == "A Light in the Attic"
    assert products[0]["price"] == "£51.77"
    assert products[0]["rating"] == "Three"


def test_prices_parse_to_floats():
    df = clean(scrape_fixture())
    assert df["price"].map(lambda v: isinstance(v, float)).all()
    assert df.loc[0, "price"] == 51.77
    assert (df["price"] > 0).all()


def test_ratings_map_to_ints_1_to_5():
    df = clean(scrape_fixture())
    assert df["rating"].map(lambda v: isinstance(v, (int,)) or float(v).is_integer()).all()
    assert df["rating"].between(1, 5).all()
    assert df.loc[0, "rating"] == 3  # "Three"


def test_parse_helpers_directly():
    assert parse_price("£51.77") == 51.77
    assert parse_price("$1,234.50".replace(",", "")) == 1234.50
    assert parse_rating("Five") == 5
    assert parse_rating("one") == 1


def test_csv_is_written(tmp_path):
    df = clean(scrape_fixture())
    out = tmp_path / "products.csv"
    write_csv(df, out)
    assert out.exists()
    reloaded = pd.read_csv(out)
    assert len(reloaded) == EXPECTED_COUNT
    assert list(reloaded.columns) == ["title", "price", "availability", "rating"]


def test_dashboard_is_written(tmp_path):
    df = clean(scrape_fixture())
    out = tmp_path / "index.html"
    render_dashboard(df, out)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "Chart" in html  # Chart.js wired up
    assert "A Light in the Attic" in html  # data embedded inline
