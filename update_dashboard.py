from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# BDT Valuation Dashboard
# Base-rate model using cumulative inflation differentials
# ============================================================

today = datetime.now(timezone.utc).strftime("%d %B %Y")

# ------------------------------------------------------------
# BASE DATA
# These are the starting-point rates.
# The dashboard will ask:
# Since this base date, has BDT depreciated enough to offset
# Bangladesh's inflation gap with India, Vietnam and China?
# ------------------------------------------------------------

BASE_DATE = "30 April 2026"

BASE_DATA = {
    "USD_BDT": 122.62,
    "USD_INR": 94.787,
    "USD_VND": 25113.0,
    "USD_CNY": 6.86,

    # CPI index at base date.
    # We set all countries to 100 at base date.
    "CPI_BD": 100.0,
    "CPI_IN": 100.0,
    "CPI_VN": 100.0,
    "CPI_CN": 100.0,
}

# ------------------------------------------------------------
# CURRENT DATA
# Update these numbers weekly or monthly.
#
# Important:
# CPI values here should be cumulative CPI index values since
# the base date, not simply annual inflation rates.
#
# Example:
# If Bangladesh cumulative inflation since base date is 3%,
# set CPI_BD = 103.0.
#
# If India cumulative inflation since base date is 1%,
# set CPI_IN = 101.0.
#
# If BB keeps USD/BDT fixed but Bangladesh inflation keeps
# exceeding competitor inflation, the model will automatically
# show rising BDT overvaluation.
# ------------------------------------------------------------

CURRENT_DATA = {
    "USD_BDT": 122.62,
    "USD_INR": 94.787,
    "USD_VND": 25113.0,
    "USD_CNY": 6.86,

    # Current cumulative CPI index since base date.
    # Initially all are 100 because the base date is today.
    "CPI_BD": 100.0,
    "CPI_IN": 100.0,
    "CPI_VN": 100.0,
    "CPI_CN": 100.0,
}

# ------------------------------------------------------------
# Supporting headline data
# These are shown for context only.
# They are not used directly in the cumulative calculation.
# ------------------------------------------------------------

HEADLINE_CONTEXT = {
    "Bangladesh CPI YoY": "8.71%",
    "India CPI YoY": "3.40%",
    "Vietnam CPI YoY": "4.65%",
    "China CPI YoY": "1.00%",
    "Bangladesh REER-implied USD/BDT": "126.03",
    "Market USD/BDT": "122.62",
}


def pct(value):
    return f"{value:.2f}%"


def cross_rate(usd_bdt, usd_competitor):
    """
    Returns BDT per 1 unit of competitor currency.

    Example:
    USD/BDT = 122.62
    USD/INR = 94.787
    BDT/INR = 122.62 / 94.787
    """
    return usd_bdt / usd_competitor


def calculate_pair(label, competitor_code, usd_key, cpi_key):
    """
    Calculates:
    1. Base BDT/competitor cross rate
    2. Current actual BDT/competitor cross rate
    3. Required BDT/competitor rate based on cumulative CPI differential
    4. Overvaluation or undervaluation percentage
    """

    base_cross = cross_rate(BASE_DATA["USD_BDT"], BASE_DATA[usd_key])
    actual_cross = cross_rate(CURRENT_DATA["USD_BDT"], CURRENT_DATA[usd_key])

    bd_cpi_factor = CURRENT_DATA["CPI_BD"] / BASE_DATA["CPI_BD"]
    competitor_cpi_factor = CURRENT_DATA[cpi_key] / BASE_DATA[cpi_key]

    required_cross = base_cross * (bd_cpi_factor / competitor_cpi_factor)

    overvaluation = ((required_cross - actual_cross) / actual_cross) * 100

    if overvaluation > 2:
        verdict = "BDT overvalued"
        css_class = "high"
    elif overvaluation < -2:
        verdict = "BDT undervalued"
        css_class = "low"
    else:
        verdict = "Near fair value"
        css_class = "medium"

    inflation_gap = ((bd_cpi_factor / competitor_cpi_factor) - 1) * 100
    nominal_adjustment = ((actual_cross / base_cross) - 1) * 100

    return {
        "label": label,
        "competitor_code": competitor_code,
        "base_cross": base_cross,
        "actual_cross": actual_cross,
        "required_cross": required_cross,
        "inflation_gap": inflation_gap,
        "nominal_adjustment": nominal_adjustment,
        "overvaluation": overvaluation,
        "verdict": verdict,
        "css_class": css_class,
    }


pairs = [
    calculate_pair("BDT vs INR", "INR", "USD_INR", "CPI_IN"),
    calculate_pair("BDT vs VND", "VND", "USD_VND", "CPI_VN"),
    calculate_pair("BDT vs RMB / CNY", "CNY", "USD_CNY", "CPI_CN"),
]

broad_reer_overvaluation = ((126.03 - 122.62) / 122.62) * 100


valuation_rows = ""

valuation_rows += f"""
<tr>
  <td>Broad REER anchor</td>
  <td>REER-implied USD/BDT: 126.03. Market USD/BDT: 122.62.</td>
  <td class="medium">BDT overvalued by about {pct(broad_reer_overvaluation)}</td>
  <td>This is the broad economy-wide REER anchor. It suggests modest BDT overvaluation.</td>
  <td>Medium-High</td>
</tr>
"""

for p in pairs:
    valuation_rows += f"""
<tr>
  <td>{p["label"]}</td>
  <td>
    Base cross rate: {p["base_cross"]:.6f} BDT per {p["competitor_code"]}.<br>
    Actual current cross rate: {p["actual_cross"]:.6f}.<br>
    Required inflation-adjusted rate: {p["required_cross"]:.6f}.
  </td>
  <td class="{p["css_class"]}">
    {p["verdict"]} by {pct(p["overvaluation"])}
  </td>
  <td>
    Inflation gap since base date: {pct(p["inflation_gap"])}.<br>
    Actual nominal BDT adjustment: {pct(p["nominal_adjustment"])}.<br>
    If the inflation gap is larger than actual depreciation, BDT becomes overvalued in real terms.
  </td>
  <td>Model-based</td>
</tr>
"""

overall_average = sum(p["overvaluation"] for p in pairs) / len(pairs)

if overall_average > 2:
    overall_verdict = "BDT is overvalued against direct export competitors"
    overall_class = "high"
elif overall_average < -2:
    overall_verdict = "BDT is undervalued against direct export competitors"
    overall_class = "low"
else:
    overall_verdict = "BDT is near fair value against direct export competitors"
    overall_class = "medium"

valuation_rows += f"""
<tr>
  <td>Overall competitor average</td>
  <td>Average of INR, VND and CNY bilateral inflation-adjusted signals.</td>
  <td class="{overall_class}">{overall_verdict}: {pct(overall_average)}</td>
  <td>This is the accumulated real competitiveness signal since {BASE_DATE}.</td>
  <td>Medium</td>
</tr>
"""


base_rows = f"""
<tr><td>Base date</td><td>{BASE_DATE}</td><td>Starting point for all calculations.</td></tr>
<tr><td>Base USD/BDT</td><td>{BASE_DATA["USD_BDT"]}</td><td>Starting Taka exchange rate.</td></tr>
<tr><td>Base USD/INR</td><td>{BASE_DATA["USD_INR"]}</td><td>Used to calculate base BDT/INR.</td></tr>
<tr><td>Base USD/VND</td><td>{BASE_DATA["USD_VND"]}</td><td>Used to calculate base BDT/VND.</td></tr>
<tr><td>Base USD/CNY</td><td>{BASE_DATA["USD_CNY"]}</td><td>Used to calculate base BDT/CNY.</td></tr>
<tr><td>Base CPI index</td><td>100 for all countries</td><td>All CPI indices are normalized to 100 on the base date.</td></tr>
"""


current_rows = f"""
<tr><td>Current USD/BDT</td><td>{CURRENT_DATA["USD_BDT"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/INR</td><td>{CURRENT_DATA["USD_INR"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/VND</td><td>{CURRENT_DATA["USD_VND"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/CNY</td><td>{CURRENT_DATA["USD_CNY"]}</td><td>Update weekly.</td></tr>
<tr><td>Bangladesh CPI index since base</td><td>{CURRENT_DATA["CPI_BD"]}</td><td>Example: 103 means 3% cumulative inflation since base date.</td></tr>
<tr><td>India CPI index since base</td><td>{CURRENT_DATA["CPI_IN"]}</td><td>Example: 101 means 1% cumulative inflation since base date.</td></tr>
<tr><td>Vietnam CPI index since base</td><td>{CURRENT_DATA["CPI_VN"]}</td><td>Example: 101 means 1% cumulative inflation since base date.</td></tr>
<tr><td>China CPI index since base</td><td>{CURRENT_DATA["CPI_CN"]}</td><td>Example: 100.5 means 0.5% cumulative inflation since base date.</td></tr>
"""


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BDT Valuation Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111827; background: #f9fafb; }}
    .wrap {{ max-width: 1250px; margin: 0 auto; background: white; padding: 28px; border-radius: 16px; box-shadow: 0 6px 24px rgba(0,0,0,0.08); }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin-top: 34px; font-size: 21px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
    h3 {{ margin-top: 22px; font-size: 17px; }}
    .meta {{ color: #4b5563; margin-bottom: 18px; font-size: 14px; }}
    .summary {{ background: #f3f4f6; border-left: 5px solid #111827; padding: 16px; border-radius: 10px; margin: 18px 0; line-height: 1.55; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 12px; }}
    th {{ background: #111827; color: white; text-align: left; padding: 12px; }}
    td {{ border-bottom: 1px solid #e5e7eb; padding: 12px; vertical-align: top; }}
    tr:nth-child(even) td {{ background: #f9fafb; }}
    .high {{ font-weight: 700; color: #991b1b; }}
    .medium {{ font-weight: 700; color: #92400e; }}
    .low {{ font-weight: 700; color: #065f46; }}
    .formula {{ background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 10px; font-family: Consolas, Monaco, monospace; font-size: 14px; overflow-x: auto; line-height: 1.55; white-space: pre-wrap; }}
    .note, .source-note {{ color: #4b5563; font-size: 13px; line-height: 1.55; }}
    .warning {{ background: #fff7ed; border-left: 5px solid #f97316; padding: 14px; border-radius: 10px; line-height: 1.55; margin-top: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-top: 12px; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; background: #ffffff; }}
    a {{ color: #0f766e; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul, ol {{ line-height: 1.6; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>BDT Valuation Dashboard vs INR, VND and RMB</h1>
    <div class="meta">Updated: {today}. Base date: {BASE_DATE}. Status: weekly automated dashboard.</div>

    <div class="summary">
      <strong>Current dashboard verdict:</strong> {overall_verdict}, based on the accumulated inflation-adjusted movement of BDT against INR, VND and CNY since {BASE_DATE}.
      This model directly tests whether BDT has depreciated enough to offset Bangladesh's inflation differential with export competitors.
    </div>

    <h2>1. Current Valuation Table</h2>
    <table>
      <thead>
        <tr>
          <th>Comparator</th>
          <th>Latest FX / Inflation Signal</th>
          <th>Estimated BDT Misalignment</th>
          <th>Interpretation for Bangladesh Exporters</th>
          <th>Confidence</th>
        </tr>
      </thead>
      <tbody>
        {valuation_rows}
      </tbody>
    </table>

    <h2>2. Base Data</h2>
    <p>The base date fixes the starting exchange rates. From this date forward, the model measures whether BDT has adjusted enough for cumulative inflation differentials.</p>
    <table>
      <thead>
        <tr>
          <th>Base variable</th>
          <th>Value</th>
          <th>Purpose</th>
        </tr>
      </thead>
      <tbody>
        {base_rows}
      </tbody>
    </table>

    <h2>3. Current Data Used in This Week's Calculation</h2>
    <table>
      <thead>
        <tr>
          <th>Current variable</th>
          <th>Value</th>
          <th>How to update</th>
        </tr>
      </thead>
      <tbody>
        {current_rows}
      </tbody>
    </table>

    <h2>4. How to Calculate BDT Overvaluation Yourself</h2>

    <h3>A. Cross-rate calculation</h3>
    <div class="formula">BDT per competitor currency = USD/BDT ÷ USD/competitor currency

Example:
USD/BDT = 122.62
USD/INR = 94.787

BDT/INR = 122.62 ÷ 94.787 = 1.2936 BDT per INR</div>

    <h3>B. Inflation-adjusted required exchange rate</h3>
    <div class="formula">Required BDT/competitor rate today
=
Base BDT/competitor rate
×
(Bangladesh CPI index today ÷ Bangladesh CPI index at base)
÷
(Competitor CPI index today ÷ Competitor CPI index at base)</div>

    <h3>C. Overvaluation calculation</h3>
    <div class="formula">Overvaluation (%)
=
(Required BDT/competitor rate - Actual BDT/competitor rate)
÷
Actual BDT/competitor rate
× 100

If the number is positive:
BDT is overvalued against that competitor.

If the number is negative:
BDT is undervalued against that competitor.</div>

    <h3>D. Why inflation differentials accumulate</h3>
    <p>
      Suppose Bangladesh inflation since the base date is 9% and India inflation is 4%.
      Then Bangladesh's price level has risen roughly 5% more than India's.
      If BDT does not depreciate by roughly that amount against INR, Bangladesh loses real price competitiveness.
      This gap accumulates over time.
    </p>

    <h2>5. Headline Context</h2>
    <table>
      <thead>
        <tr>
          <th>Indicator</th>
          <th>Latest reference value</th>
          <th>Use</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Bangladesh CPI YoY</td><td>{HEADLINE_CONTEXT["Bangladesh CPI YoY"]}</td><td>Context only. Use cumulative CPI index for calculation.</td></tr>
        <tr><td>India CPI YoY</td><td>{HEADLINE_CONTEXT["India CPI YoY"]}</td><td>Context only. Use cumulative CPI index for calculation.</td></tr>
        <tr><td>Vietnam CPI YoY</td><td>{HEADLINE_CONTEXT["Vietnam CPI YoY"]}</td><td>Context only. Use cumulative CPI index for calculation.</td></tr>
        <tr><td>China CPI YoY</td><td>{HEADLINE_CONTEXT["China CPI YoY"]}</td><td>Context only. Use cumulative CPI index for calculation.</td></tr>
        <tr><td>Bangladesh REER-implied USD/BDT</td><td>{HEADLINE_CONTEXT["Bangladesh REER-implied USD/BDT"]}</td><td>Broad REER anchor.</td></tr>
        <tr><td>Market USD/BDT</td><td>{HEADLINE_CONTEXT["Market USD/BDT"]}</td><td>Used for broad REER comparison.</td></tr>
      </tbody>
    </table>

    <h2>6. Reproducibility Checklist</h2>
    <ol>
      <li>Keep the base exchange rates fixed at the base date.</li>
      <li>Update current USD/BDT, USD/INR, USD/VND and USD/CNY.</li>
      <li>Update cumulative CPI index since the base date for Bangladesh, India, Vietnam and China.</li>
      <li>Calculate actual current BDT cross-rates.</li>
      <li>Calculate required inflation-adjusted BDT cross-rates.</li>
      <li>Compare required rates with actual rates.</li>
      <li>If required BDT depreciation is greater than actual depreciation, BDT is overvalued.</li>
    </ol>

    <div class="warning">
      <strong>Important caution:</strong> This dashboard estimates export-competitiveness misalignment, not a trading forecast.
      Exact valuation requires full trade weights, price indices, base periods, productivity trends, terms of trade, capital flows and reserve policy.
    </div>

    <h2>7. Source Links</h2>
    <div class="grid">
      <div class="card">
        <h3>Methodology Sources</h3>
        <ul>
          <li><a href="https://data.imf.org/en/datasets/IMF.STA%3AEER" target="_blank">IMF Effective Exchange Rate Dataset</a></li>
          <li><a href="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PX.REX.REER" target="_blank">World Bank WDI REER Metadata</a></li>
          <li><a href="https://www.bis.org/statistics/eer.htm" target="_blank">BIS Effective Exchange Rate Indices</a></li>
          <li><a href="https://www.imf.org/en/Publications/fandd/issues/Series/Back-to-Basics/Real-Exchange-Rates" target="_blank">IMF Finance & Development: Real Exchange Rates</a></li>
        </ul>
      </div>

      <div class="card">
        <h3>Bangladesh Sources</h3>
        <ul>
          <li><a href="https://www.bb.org.bd/" target="_blank">Bangladesh Bank</a></li>
          <li><a href="https://bbs.gov.bd/" target="_blank">Bangladesh Bureau of Statistics</a></li>
          <li><a href="https://today.thefinancialexpress.com.bd/last-page/inflation-pushes-reer-up-143-points-in-mar-1776877886" target="_blank">Financial Express report on Bangladesh REER, March 2026</a></li>
        </ul>
      </div>

      <div class="card">
        <h3>India Sources</h3>
        <ul>
          <li><a href="https://www.rbi.org.in/scripts/referenceratearchive.aspx" target="_blank">Reserve Bank of India Reference Rate Archive</a></li>
          <li><a href="https://www.msei.in/markets/currency/historical-data/rbireferenceratearchives" target="_blank">MSEI RBI Reference Rate Archive</a></li>
          <li><a href="https://www.mospi.gov.in/" target="_blank">India MOSPI CPI releases</a></li>
        </ul>
      </div>

      <div class="card">
        <h3>Vietnam Sources</h3>
        <ul>
          <li><a href="https://www.sbv.gov.vn/" target="_blank">State Bank of Vietnam</a></li>
          <li><a href="https://www.gso.gov.vn/" target="_blank">Vietnam General Statistics Office</a></li>
        </ul>
      </div>

      <div class="card">
        <h3>China Sources</h3>
        <ul>
          <li><a href="http://www.pbc.gov.cn/en/" target="_blank">People's Bank of China</a></li>
          <li><a href="https://www.chinamoney.com.cn/english/" target="_blank">ChinaMoney / CFETS</a></li>
          <li><a href="https://www.stats.gov.cn/english/" target="_blank">National Bureau of Statistics of China</a></li>
        </ul>
      </div>

      <div class="card">
        <h3>Cross-check Sources</h3>
        <ul>
          <li><a href="https://data.worldbank.org/indicator/PX.REX.REER" target="_blank">World Bank REER indicator</a></li>
          <li><a href="https://data.imf.org/" target="_blank">IMF Data Portal</a></li>
          <li><a href="https://www.wto.org/" target="_blank">WTO trade data</a></li>
        </ul>
      </div>
    </div>

    <h2>8. Simple Interpretation Rule</h2>
    <p>
      If Bangladesh inflation is higher than India, Vietnam or China, but BDT does not depreciate enough against those currencies,
      then BDT appreciates in real terms. This acts like a hidden tax on Bangladesh exporters because their costs rise faster than competitor costs
      while the exchange rate does not compensate them.
    </p>

    <p class="source-note">
      <strong>Last update note:</strong> Update the CURRENT_DATA section in the Python script with the latest exchange rates and cumulative CPI indices.
      The weekly GitHub Action will then regenerate this page automatically.
    </p>
  </div>
</body>
</html>"""

Path("index.html").write_text(html, encoding="utf-8")

print("index.html updated successfully with cumulative inflation-differential model")
