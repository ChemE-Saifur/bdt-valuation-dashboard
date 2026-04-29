from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------
# Simple first version.
# Later we can replace these hardcoded values with
# live data collection from official sources/APIs.
# --------------------------------------------------

today = datetime.now(timezone.utc).strftime("%d %B %Y")

rows = [
    {
        "comparator": "Broad REER anchor",
        "signal": "Latest REER-based estimate to be updated manually or by data API.",
        "misalignment": "BDT likely modestly overvalued",
        "interpretation": "The Taka should be judged by inflation-adjusted competitiveness, not only USD/BDT.",
        "confidence": "Medium"
    },
    {
        "comparator": "BDT vs INR",
        "signal": "Compare Bangladesh inflation, India inflation, USD/BDT and USD/INR.",
        "misalignment": "BDT likely overvalued vs INR if Bangladesh inflation remains higher without enough BDT depreciation.",
        "interpretation": "India’s lower inflation and exchange-rate movement can give Indian exporters a real-price advantage.",
        "confidence": "Medium"
    },
    {
        "comparator": "BDT vs VND",
        "signal": "Compare Bangladesh inflation, Vietnam inflation, USD/BDT and USD/VND.",
        "misalignment": "BDT likely overvalued vs VND if Bangladesh inflation remains higher.",
        "interpretation": "Vietnam remains a direct competitor in garments, footwear, electronics and export diversification.",
        "confidence": "Medium"
    },
    {
        "comparator": "BDT vs RMB / CNY",
        "signal": "Compare Bangladesh inflation, China inflation, USD/BDT and USD/CNY.",
        "misalignment": "BDT likely overvalued vs RMB if Bangladesh inflation remains much higher than China.",
        "interpretation": "China’s low inflation means Bangladesh needs either productivity gains or exchange-rate adjustment.",
        "confidence": "Medium"
    },
    {
        "comparator": "Overall conclusion",
        "signal": "Weekly dashboard estimate.",
        "misalignment": "Current verdict: BDT is probably moderately overvalued for export competitiveness.",
        "interpretation": "The policy issue is BDT’s real value against competitor currencies, not only the nominal USD/BDT rate.",
        "confidence": "Medium"
    }
]

table_rows = ""

for row in rows:
    table_rows += f"""
        <tr>
          <td>{row['comparator']}</td>
          <td>{row['signal']}</td>
          <td class="medium">{row['misalignment']}</td>
          <td>{row['interpretation']}</td>
          <td>{row['confidence']}</td>
        </tr>
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BDT Valuation Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111827; background: #f9fafb; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 6px 24px rgba(0,0,0,0.08); }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    .meta {{ color: #4b5563; margin-bottom: 18px; font-size: 14px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th {{ background: #111827; color: white; text-align: left; padding: 12px; }}
    td {{ border-bottom: 1px solid #e5e7eb; padding: 12px; vertical-align: top; }}
    tr:nth-child(even) td {{ background: #f9fafb; }}
    .high {{ font-weight: 700; color: #991b1b; }}
    .medium {{ font-weight: 700; color: #92400e; }}
    .low {{ font-weight: 700; color: #065f46; }}
    .note {{ margin-top: 18px; color: #4b5563; font-size: 13px; line-height: 1.45; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>BDT Valuation Dashboard vs INR, VND and RMB</h1>
    <div class="meta">Updated: {today}. Status: weekly automated dashboard.</div>

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
        {table_rows}
      </tbody>
    </table>

    <div class="note">
      Method: Broad REER anchor plus bilateral competitiveness signals using exchange-rate movements,
      CPI inflation differentials, REER/NEER information, reserves, current account and export performance.
      This is a policy dashboard, not a trading recommendation.
    </div>
  </div>
</body>
</html>
"""

Path("index.html").write_text(html, encoding="utf-8")

print("index.html updated successfully")
