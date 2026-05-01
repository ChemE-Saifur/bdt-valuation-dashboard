from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# BDT Valuation Dashboard
# Cumulative inflation-differential model since 1 January 2025
# ============================================================

today = datetime.now(timezone.utc).strftime("%d %B %Y")

# ------------------------------------------------------------
# BASE DATE
# The model measures accumulated real overvaluation from this date.
# ------------------------------------------------------------

BASE_DATE = "1 January 2025"

# ------------------------------------------------------------
# BASE DATA
#
# IMPORTANT:
# Replace these base exchange rates with actual market/reference
# rates for 1 January 2025 or the nearest available business day.
#
# Formula:
# Base BDT/competitor = Base USD/BDT ÷ Base USD/competitor
# ------------------------------------------------------------

BASE_DATA = {
    "USD_BDT": 120.00,      # Replace with actual USD/BDT on or near 1 Jan 2025
    "USD_INR": 85.60,       # Replace with actual USD/INR on or near 1 Jan 2025
    "USD_VND": 25500.00,    # Replace with actual USD/VND on or near 1 Jan 2025
    "USD_CNY": 7.30,        # Replace with actual USD/CNY on or near 1 Jan 2025
}

# ------------------------------------------------------------
# CURRENT DATA
#
# Update these values weekly.
#
# Inflation values must be cumulative inflation from 1 Jan 2025
# to the current date, not only latest year-on-year inflation.
#
# Example:
# If Bangladesh price level increased 13.5% since 1 Jan 2025,
# set BD_CUM_INFLATION = 13.5
# ------------------------------------------------------------

CURRENT_DATA = {
    "USD_BDT": 122.62,
    "USD_INR": 95.2417,
"USD_VND": 26368.00,
    "USD_CNY": 6.86,

    # Cumulative inflation since 1 January 2025.
    # Replace these with actual cumulative CPI inflation.
"BD_CUM_INFLATION": 9.94,
"IN_CUM_INFLATION": 3.12,
"VN_CUM_INFLATION": 6.00,
"CN_CUM_INFLATION": 0.50,
}

# ------------------------------------------------------------
# BROAD REER ANCHOR
# This is separate from the bilateral cumulative model.
# Update when new Bangladesh REER-implied estimates are available.
# ------------------------------------------------------------

REER_IMPLIED_USD_BDT = 126.03
MARKET_USD_BDT_FOR_REER = 122.62


def pct(value):
    return f"{value:.2f}%"


def cross_rate(usd_bdt, usd_competitor):
    """
    Returns BDT per one unit of competitor currency.

    Example:
    USD/BDT = 122.62
    USD/INR = 94.787
    BDT/INR = 122.62 / 94.787
    """
    return usd_bdt / usd_competitor


def inflation_factor(percent):
    """
    Converts cumulative inflation percentage into price index factor.

    Example:
    13.5% cumulative inflation becomes 1.135
    """
    return 1 + (percent / 100)


def calculate_pair(label, competitor_code, usd_key, competitor_inflation_key):
    base_cross = cross_rate(BASE_DATA["USD_BDT"], BASE_DATA[usd_key])
    actual_cross = cross_rate(CURRENT_DATA["USD_BDT"], CURRENT_DATA[usd_key])

    bd_factor = inflation_factor(CURRENT_DATA["BD_CUM_INFLATION"])
    competitor_factor = inflation_factor(CURRENT_DATA[competitor_inflation_key])

    required_cross = base_cross * (bd_factor / competitor_factor)

    actual_nominal_adjustment = ((actual_cross / base_cross) - 1) * 100
    required_nominal_adjustment = ((required_cross / base_cross) - 1) * 100
    inflation_gap = ((bd_factor / competitor_factor) - 1) * 100

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

    return {
        "label": label,
        "competitor_code": competitor_code,
        "base_cross": base_cross,
        "actual_cross": actual_cross,
        "required_cross": required_cross,
        "inflation_gap": inflation_gap,
        "actual_nominal_adjustment": actual_nominal_adjustment,
        "required_nominal_adjustment": required_nominal_adjustment,
        "overvaluation": overvaluation,
        "verdict": verdict,
        "css_class": css_class,
    }


pairs = [
    calculate_pair("BDT vs INR", "INR", "USD_INR", "IN_CUM_INFLATION"),
    calculate_pair("BDT vs VND", "VND", "USD_VND", "VN_CUM_INFLATION"),
    calculate_pair("BDT vs RMB / CNY", "CNY", "USD_CNY", "CN_CUM_INFLATION"),
]

broad_reer_overvaluation = ((REER_IMPLIED_USD_BDT - MARKET_USD_BDT_FOR_REER) / MARKET_USD_BDT_FOR_REER) * 100
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


valuation_rows = f"""
<tr>
  <td>Broad REER anchor</td>
  <td>REER-implied USD/BDT: {REER_IMPLIED_USD_BDT}. Market USD/BDT: {MARKET_USD_BDT_FOR_REER}.</td>
  <td class="medium">BDT overvalued by about {pct(broad_reer_overvaluation)}</td>
  <td>This is the broad economy-wide REER anchor. It is separate from the bilateral cumulative inflation model.</td>
  <td>Medium-High</td>
</tr>
"""

for p in pairs:
    valuation_rows += f"""
<tr>
  <td>{p["label"]}</td>
  <td>
    Base cross rate on {BASE_DATE}: {p["base_cross"]:.6f} BDT per {p["competitor_code"]}.<br>
    Actual current cross rate: {p["actual_cross"]:.6f}.<br>
    Required inflation-adjusted rate: {p["required_cross"]:.6f}.
  </td>
  <td class="{p["css_class"]}">
    {p["verdict"]} by {pct(p["overvaluation"])}
  </td>
  <td>
    Cumulative inflation gap since {BASE_DATE}: {pct(p["inflation_gap"])}.<br>
    Required BDT adjustment: {pct(p["required_nominal_adjustment"])}.<br>
    Actual BDT adjustment: {pct(p["actual_nominal_adjustment"])}.<br>
    If required depreciation is greater than actual depreciation, BDT is overvalued.
  </td>
  <td>Model-based</td>
</tr>
"""

valuation_rows += f"""
<tr>
  <td>Overall competitor average</td>
  <td>Average of INR, VND and CNY bilateral cumulative inflation-adjusted signals.</td>
  <td class="{overall_class}">{overall_verdict}: {pct(overall_average)}</td>
  <td>This is the accumulated real competitiveness signal since {BASE_DATE}.</td>
  <td>Medium</td>
</tr>
"""


base_rows = f"""
<tr><td>Base date</td><td>{BASE_DATE}</td><td>Starting point for measuring accumulated real overvaluation.</td></tr>
<tr><td>Base USD/BDT</td><td>{BASE_DATA["USD_BDT"]}</td><td>Replace with actual USD/BDT on or near 1 Jan 2025.</td></tr>
<tr><td>Base USD/INR</td><td>{BASE_DATA["USD_INR"]}</td><td>Replace with actual USD/INR on or near 1 Jan 2025.</td></tr>
<tr><td>Base USD/VND</td><td>{BASE_DATA["USD_VND"]}</td><td>Replace with actual USD/VND on or near 1 Jan 2025.</td></tr>
<tr><td>Base USD/CNY</td><td>{BASE_DATA["USD_CNY"]}</td><td>Replace with actual USD/CNY on or near 1 Jan 2025.</td></tr>
"""


current_rows = f"""
<tr><td>Current USD/BDT</td><td>{CURRENT_DATA["USD_BDT"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/INR</td><td>{CURRENT_DATA["USD_INR"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/VND</td><td>{CURRENT_DATA["USD_VND"]}</td><td>Update weekly.</td></tr>
<tr><td>Current USD/CNY</td><td>{CURRENT_DATA["USD_CNY"]}</td><td>Update weekly.</td></tr>
<tr><td>Bangladesh cumulative inflation since {BASE_DATE}</td><td>{CURRENT_DATA["BD_CUM_INFLATION"]}%</td><td>Update from CPI index.</td></tr>
<tr><td>India cumulative inflation since {BASE_DATE}</td><td>{CURRENT_DATA["IN_CUM_INFLATION"]}%</td><td>Update from CPI index.</td></tr>
<tr><td>Vietnam cumulative inflation since {BASE_DATE}</td><td>{CURRENT_DATA["VN_CUM_INFLATION"]}%</td><td>Update from CPI index.</td></tr>
<tr><td>China cumulative inflation since {BASE_DATE}</td><td>{CURRENT_DATA["CN_CUM_INFLATION"]}%</td><td>Update from CPI index.</td></tr>
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
      <strong>Current dashboard verdict:</strong> {overall_verdict}, based on cumulative inflation differentials since {BASE_DATE}.
      This model tests whether BDT has depreciated enough to offset Bangladesh's accumulated inflation gap with India, Vietnam and China.
    </div>

    <h2>1. Current Valuation Table</h2>
    <table>
      <thead>
        <tr>
          <th>Comparator</th>
          <th>FX / Inflation Signal</th>
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
    <p>The base date is fixed at {BASE_DATE}. From this date onward, the model measures whether BDT has adjusted enough for cumulative inflation differentials.</p>
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

    <h2>4. Calculation Methodology</h2>

    <h3>A. Cross-rate calculation</h3>
    <div class="formula">BDT per competitor currency = USD/BDT ÷ USD/competitor currency</div>

    <h3>B. Required exchange rate based on cumulative inflation differential</h3>
    <div class="formula">Required BDT/competitor rate today
=
Base BDT/competitor rate on 1 Jan 2025
×
(1 + Bangladesh cumulative inflation since 1 Jan 2025)
÷
(1 + competitor cumulative inflation since 1 Jan 2025)</div>

    <h3>C. Overvaluation calculation</h3>
    <div class="formula">Overvaluation (%)
=
(Required BDT/competitor rate - Actual BDT/competitor rate)
÷
Actual BDT/competitor rate
× 100</div>

    <h3>D. Interpretation</h3>
    <p>
      If Bangladesh cumulative inflation is higher than competitor inflation, BDT must depreciate against that competitor's currency to preserve real export competitiveness.
      If BDT does not depreciate enough, the model records BDT overvaluation.
    </p>

    <h2>5. Data Update Rule</h2>
    <ol>
      <li>Keep {BASE_DATE} as the fixed base date.</li>
      <li>Update current USD/BDT, USD/INR, USD/VND and USD/CNY every week.</li>
      <li>Update cumulative CPI inflation from {BASE_DATE} for Bangladesh, India, Vietnam and China.</li>
      <li>Do not use only year-on-year inflation. Use cumulative inflation since the base date.</li>
      <li>Compare actual BDT depreciation with required BDT depreciation.</li>
    </ol>

    <div class="warning">
      <strong>Important caution:</strong> The base exchange rates and cumulative inflation values must be verified from official sources.
      The structure is correct, but the dashboard output is only as accurate as the input data.
    </div>

    <h2>6. Source Links</h2>
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
        </ul>
      </div>

      <div class="card">
        <h3>India Sources</h3>
        <ul>
          <li><a href="https://www.rbi.org.in/scripts/referenceratearchive.aspx" target="_blank">Reserve Bank of India Reference Rate Archive</a></li>
          <li><a href="https://www.mospi.gov.in/" target="_blank">India MOSPI CPI Releases</a></li>
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
          <li><a href="https://data.worldbank.org/indicator/PX.REX.REER" target="_blank">World Bank REER Indicator</a></li>
          <li><a href="https://data.imf.org/" target="_blank">IMF Data Portal</a></li>
          <li><a href="https://www.wto.org/" target="_blank">WTO Trade Data</a></li>
        </ul>
      </div>
    </div>

    <h2>7. Simple Interpretation Rule</h2>
    <p>
      Since {BASE_DATE}, if Bangladesh prices have risen faster than India, Vietnam or China, then BDT must depreciate enough against INR, VND and CNY to keep Bangladesh exporters equally competitive.
      If the exchange rate does not adjust, the accumulated inflation gap becomes real BDT overvaluation.
    </p>

    <p><strong>Last update note:</strong> Update the CURRENT_DATA section weekly. The GitHub Action will regenerate this page automatically.</p>
  </div>
</body>
</html>"""

Path("index.html").write_text(html, encoding="utf-8")

print("index.html updated successfully with cumulative inflation model from 1 January 2025")
