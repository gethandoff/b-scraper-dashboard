# Project B — Scraper → Spreadsheet / Dashboard

> Scheduled scrape of a target site (e.g. competitor prices) → a clean spreadsheet
> + a simple HTML dashboard.

**Client hook:** *Wake up to fresh competitor data every morning.*

![demo](docs/demo.gif) <!-- record a GIF of `python demo.py` + opening the dashboard and drop it here -->

## What it does

Scrapes a target site, cleans the result with `pandas`, writes `data/products.csv`,
and generates a self-contained `dashboard/index.html` (a Chart.js bar chart + a
sortable table). A GitHub Actions cron can run it every morning and commit fresh
data back to the repo — for free on public repos.

The demo uses [books.toscrape.com](https://books.toscrape.com), a sandbox site
built explicitly for scraping practice (safe and legal to scrape).

## Quick start

```bash
pip install -r requirements.txt

# Run the demo (NO network, NO API key — parses the bundled HTML fixture)
python demo.py

# then open the dashboard in your browser:
#   dashboard/index.html
```

That writes `data/products.csv` and `dashboard/index.html` and prints a summary.

### Scrape the real site

```bash
python -m src.cli --live              # fetch the first 3 catalogue pages
python -m src.cli --live --pages 2    # fewer pages
python -m src.cli --out my.csv        # offline, custom CSV path
```

## How it works

```
                          --live  ─▶ requests ─▶ real site
target ──▶ src/scrape.py ─┤                                 ─▶ list[dict]
                          default ─▶ sample_data/page.html (offline fixture)
                                                │
   src/clean.py (pandas: £51.77→51.77, "Three"→3, strip) ─▶ DataFrame
                                                │
                       ┌────────────────────────┴───────────────────────┐
                       ▼                                                 ▼
            src/clean.py → data/products.csv          src/dashboard.py → dashboard/index.html
                                                       (inline JSON + Chart.js bar chart + sortable table)
```

- **`src/scrape.py`** — fetch + parse with `selectolax`. The `--live` flag hits the
  real URL; by default it parses the bundled fixture so the demo and tests need no network.
- **`src/clean.py`** — pandas cleaning: price → float, star-rating word → int 1–5, strip whitespace.
- **`src/dashboard.py`** — renders a static HTML page with the data embedded inline
  (works by double-clicking the file — no server) and Chart.js from a CDN.
- **`src/cli.py`** — `argparse` entry point that runs the whole pipeline.

## Tests

```bash
pytest
```

The suite proves the success criterion offline: the fixture parses to the expected
number of products, prices parse to floats, ratings map to ints 1–5, and the CSV
(and dashboard) are written.

## Scheduling — "fresh data every morning"

`.github/workflows/scrape.yml` runs the scraper on a daily cron (07:00 UTC), then
commits the updated `data/products.csv` + `dashboard/index.html` back to the repo.
It also supports manual runs (`workflow_dispatch`). GitHub Actions is **free on
public repositories**, so this costs $0.

To change the time, edit the `cron:` line (it's UTC). To self-host instead, a plain
OS cron / Task Scheduler entry running `python -m src.cli --live` works too.

## Customize for a client

See [CUSTOMIZE.md](CUSTOMIZE.md) — swap the target URL + selectors, change the output
destination (e.g. Google Sheet), tweak the dashboard, and tune the schedule. Note the
politeness / robots.txt guidance there: scraping terms vary by site.

## License

MIT
