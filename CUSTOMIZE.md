# Customizing this for a client

The swap-in points, in the order you'll usually touch them:

### 1. The target URL + selectors — `src/scrape.py`
This is the main change. Point `BASE_URL` at the client's target site (or set
`TARGET_URL` in `.env`), then update the CSS selectors in `parse_html()` to match
that site's markup. Today they target the books.toscrape.com structure:

| Field        | Selector                          | Notes                                   |
|--------------|-----------------------------------|-----------------------------------------|
| title        | `h3 a` → `title` attribute        | visible text is truncated; attr is full |
| price        | `p.price_color`                   | text like `£51.77`                      |
| availability | `p.instock.availability`          | text like `In stock`                    |
| rating       | `p.star-rating` → second class    | e.g. `star-rating Three`                |

Open the client's page, inspect the repeating "card" element, and rewrite these
four lookups. Everything downstream (cleaning, CSV, dashboard) keys off the same
dict shape, so it keeps working.

### 2. The cleaning rules — `src/clean.py`
`parse_price` strips currency symbols to a float; `parse_rating` maps rating words
to ints. Adjust for the client's data (different currency format, percentage
discounts, dates, SKUs, etc.). Add columns to the DataFrame as needed.

### 3. Output destination — `src/cli.py` / `src/clean.py`
By default it writes a local CSV. For a client you'll usually add a destination:
- **Google Sheet** via [`gspread`](https://docs.gspread.org/) — append rows to a
  shared sheet they already use. Add a `src/sink.py` with a `write_sheet(df)` and
  call it from `run_pipeline`.
- A **different CSV path / shared drive** — just change `--out`.
- POST to an internal API / webhook.

### 4. The dashboard fields — `src/dashboard.py`
Edit `_TEMPLATE`: change the chart (e.g. price-over-time line chart if you keep
history), the table columns, and the summary stats. The data is embedded inline as
JSON, so the page stays self-contained and openable without a server.

### 5. The schedule — `.github/workflows/scrape.yml`
Tune the `cron:` expression (it's in **UTC**). `0 7 * * *` is daily at 07:00 UTC.
For a self-hosted run, use OS cron / Windows Task Scheduler calling
`python -m src.cli --live`.

## Politeness & legal notes (important)

- **Respect `robots.txt`** of the target site, and check its Terms of Service —
  **scraping terms vary by site**, and some prohibit it. books.toscrape.com is a
  sandbox built for this, which is why it's the demo target.
- **Rate-limit yourself.** `scrape_live()` already sleeps between page fetches
  (`delay=1.0`s). Increase it for larger sites; never hammer a server.
- Send an honest, identifiable `User-Agent` (see `HEADERS` in `src/scrape.py`).
- Cache / scrape only what you need, and prefer an official API if one exists.
- Don't scrape personal data or anything behind a login without permission.
