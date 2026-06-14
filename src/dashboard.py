"""Dashboard: render a self-contained static HTML page from the cleaned data.

The page embeds the rows as inline JSON (no server, no fetch — open the file
directly in a browser) and renders a Chart.js bar chart of price-by-book plus a
sortable HTML table. Chart.js is loaded from a CDN.
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

import pandas as pd

# Chart.js from CDN (pinned major version) so the dashboard is self-contained.
CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4"

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Competitor Price Dashboard</title>
  <script src="{chartjs}"></script>
  <style>
    :root {{ --fg: #1a1a2e; --muted: #6b7280; --accent: #4f46e5; --border: #e5e7eb; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
           margin: 0; padding: 2rem; color: var(--fg); background: #f7f7fb; }}
    h1 {{ margin: 0 0 .25rem; }}
    .meta {{ color: var(--muted); margin-bottom: 1.5rem; font-size: .9rem; }}
    .card {{ background: #fff; border: 1px solid var(--border); border-radius: 12px;
             padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.04); }}
    .stats {{ display: flex; gap: 2rem; flex-wrap: wrap; }}
    .stat .num {{ font-size: 1.6rem; font-weight: 700; }}
    .stat .lbl {{ color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ text-align: left; padding: .6rem .75rem; border-bottom: 1px solid var(--border); }}
    th {{ cursor: pointer; user-select: none; background: #fafafe; position: sticky; top: 0; }}
    th:hover {{ color: var(--accent); }}
    th[data-dir="asc"]::after {{ content: " \\2191"; }}
    th[data-dir="desc"]::after {{ content: " \\2193"; }}
    tbody tr:hover {{ background: #fafafe; }}
    .num-cell {{ text-align: right; font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body>
  <h1>Competitor Price Dashboard</h1>
  <div class="meta">Generated {generated} &middot; {count} products tracked</div>

  <div class="card stats">
    <div class="stat"><div class="num">{count}</div><div class="lbl">Products</div></div>
    <div class="stat"><div class="num">{avg_price}</div><div class="lbl">Avg price</div></div>
    <div class="stat"><div class="num">{min_price}</div><div class="lbl">Cheapest</div></div>
    <div class="stat"><div class="num">{max_price}</div><div class="lbl">Most expensive</div></div>
  </div>

  <div class="card">
    <canvas id="priceChart" height="120"></canvas>
  </div>

  <div class="card">
    <table id="dataTable">
      <thead>
        <tr>
          <th data-key="title" data-type="str">Title</th>
          <th data-key="price" data-type="num" class="num-cell">Price</th>
          <th data-key="rating" data-type="num" class="num-cell">Rating</th>
          <th data-key="availability" data-type="str">Availability</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>

  <!-- Data is embedded inline so the page works offline with no server. -->
  <script id="data" type="application/json">{data_json}</script>
  <script>
    const ROWS = JSON.parse(document.getElementById("data").textContent);

    // ---- Bar chart: price by book ----
    new Chart(document.getElementById("priceChart"), {{
      type: "bar",
      data: {{
        labels: ROWS.map(r => r.title),
        datasets: [{{
          label: "Price",
          data: ROWS.map(r => r.price),
          backgroundColor: "#4f46e5",
          borderRadius: 4
        }}]
      }},
      options: {{
        plugins: {{ legend: {{ display: false }} }},
        scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: "Price" }} }} }}
      }}
    }});

    // ---- Sortable table ----
    const tbody = document.querySelector("#dataTable tbody");
    function render(rows) {{
      tbody.innerHTML = rows.map(r => `<tr>
        <td>${{r.title}}</td>
        <td class="num-cell">${{r.price.toFixed(2)}}</td>
        <td class="num-cell">${{r.rating}}</td>
        <td>${{r.availability}}</td>
      </tr>`).join("");
    }}
    render(ROWS);

    document.querySelectorAll("#dataTable th").forEach(th => {{
      th.addEventListener("click", () => {{
        const key = th.dataset.key, type = th.dataset.type;
        const dir = th.dataset.dir === "asc" ? "desc" : "asc";
        document.querySelectorAll("#dataTable th").forEach(h => h.removeAttribute("data-dir"));
        th.dataset.dir = dir;
        const sorted = [...ROWS].sort((a, b) => {{
          let av = a[key], bv = b[key];
          if (type === "str") {{ av = String(av).toLowerCase(); bv = String(bv).toLowerCase(); }}
          return (av < bv ? -1 : av > bv ? 1 : 0) * (dir === "asc" ? 1 : -1);
        }});
        render(sorted);
      }});
    }});
  </script>
</body>
</html>
"""


def render_dashboard(df: pd.DataFrame, out: str | Path) -> Path:
    """Render the cleaned DataFrame to a self-contained dashboard HTML file."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = df.to_dict(orient="records")
    prices = df["price"] if len(df) else pd.Series(dtype=float)

    html = _TEMPLATE.format(
        chartjs=CHARTJS_CDN,
        generated=_dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        count=len(df),
        avg_price=f"{prices.mean():.2f}" if len(df) else "0.00",
        min_price=f"{prices.min():.2f}" if len(df) else "0.00",
        max_price=f"{prices.max():.2f}" if len(df) else "0.00",
        data_json=json.dumps(rows, ensure_ascii=False),
    )
    out.write_text(html, encoding="utf-8")
    return out
