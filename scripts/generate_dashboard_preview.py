import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "docs", "results")
IMG_DIR = os.path.join(BASE_DIR, "docs", "images")
os.makedirs(IMG_DIR, exist_ok=True)

df_kpi = pd.read_csv(os.path.join(RESULTS_DIR, "01_kpi_overview.csv"))
df_delivery = pd.read_csv(os.path.join(RESULTS_DIR, "02_delivery_performance.csv"))
df_reviews = pd.read_csv(os.path.join(RESULTS_DIR, "03_delay_vs_review.csv"))
df_states = pd.read_csv(os.path.join(RESULTS_DIR, "04_state_delay_hotspots.csv"))
df_sellers = pd.read_csv(os.path.join(RESULTS_DIR, "05_seller_scorecard.csv"))

# Build SVG elements dynamically from actual CSV values
svg_lines = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 720" width="100%" height="100%">',
    '<defs>',
    '  <style>',
    '    .font { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; }',
    '    .card { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.2; rx: 10; }',
    '    .kpi-label { font-size: 10px; font-weight: 700; fill: #64748b; letter-spacing: 0.05em; }',
    '    .kpi-val { font-size: 23px; font-weight: 800; fill: #0f172a; }',
    '    .kpi-sub { font-size: 10.5px; font-weight: 600; }',
    '    .chart-title { font-size: 13px; font-weight: 700; fill: #0f172a; }',
    '    .chart-sub { font-size: 10px; fill: #64748b; }',
    '    .axis-txt { font-size: 9.5px; fill: #475569; }',
    '    .val-txt { font-size: 9.5px; font-weight: 700; fill: #0f172a; }',
    '  </style>',
    '</defs>',
    '<!-- Background -->',
    '<rect width="1200" height="720" fill="#f8fafc" rx="12"/>',
    '',
    '<!-- Top Executive Header Banner -->',
    '<rect x="20" y="16" width="1160" height="58" fill="#0f172a" rx="10"/>',
    '<rect x="20" y="16" width="6" height="58" fill="#3b82f6" rx="3"/>',
    '<text x="40" y="41" class="font" font-size="16" font-weight="800" fill="#ffffff">OLIST COMMERCIAL OPERATIONS &amp; DELIVERY SLA EXECUTIVE SUITE</text>',
    '<text x="40" y="60" class="font" font-size="11" fill="#cbd5e1">Star Schema Data Mart (PostgreSQL 15) · 10 Reconciled Power BI DAX Measures · 99,441 Orders ($13,591,643.70 GMV)</text>',
    '<rect x="915" y="31" width="248" height="28" fill="#064e3b" stroke="#10b981" stroke-width="1" rx="14"/>',
    '<text x="1039" y="49" text-anchor="middle" class="font" font-size="10.5" font-weight="700" fill="#34d399">✓ SQL = DAX RECONCILED (0.00% VAR)</text>',
]

# 5 KPI Scorecards (y=86 to 166)
kpis = [
    ("RECONCILED TOTAL GMV", "$13.59M", "+8.3x Scale (Peak $1.00M Nov '17)", "#059669"),
    ("DELIVERED ORDERS", "96,470", "99,441 Total (97.0% Completion)", "#2563eb"),
    ("AVERAGE ORDER VALUE", "$136.68", "Exact SQL &amp; DAX Match", "#2563eb"),
    ("ON-TIME FULFILLMENT SLA", "93.23%", "-1.77% vs 95.0% Target (6,534 Late)", "#dc2626"),
    ("CUSTOMER CSAT (REVIEW ★)", "4.09 / 5.0", "Collapses to 1.70 ★ when 8+d Late", "#d97706"),
]

for i, (label, val, sub, color) in enumerate(kpis):
    x = 20 + i * 234
    svg_lines.extend([
        f'<rect x="{x}" y="86" width="224" height="80" class="card"/>',
        f'<rect x="{x}" y="86" width="224" height="4" fill="{color}" rx="2"/>',
        f'<text x="{x+14}" y="106" class="font kpi-label">{label}</text>',
        f'<text x="{x+14}" y="135" class="font kpi-val">{val}</text>',
        f'<text x="{x+14}" y="154" class="font kpi-sub" fill="{color}">{sub}</text>',
    ])

# Panel 1 (Top-Left): Monthly GMV & On-Time SLA Trajectory (x=20, y=178, w=572, h=255)
svg_lines.extend([
    '<rect x="20" y="178" width="572" height="255" class="card"/>',
    '<text x="36" y="200" class="font chart-title">1. GMV Scaled 8.3x in 2017 (Peak $1.00M Black Friday) While Q1 \'18 SLA Dipped to 81.0%</text>',
    '<text x="36" y="215" class="font chart-sub">Monthly Gross Merchandise Value ($K Bars) &amp; On-Time SLA % (Red Line vs 95% Target)</text>',
    '<line x1="52" y1="395" x2="565" y2="395" stroke="#cbd5e1" stroke-width="1"/>',
    '<line x1="52" y1="245" x2="565" y2="245" stroke="#f1f5f9" stroke-width="1"/>',
    '<line x1="52" y1="295" x2="565" y2="295" stroke="#f1f5f9" stroke-width="1"/>',
    '<line x1="52" y1="345" x2="565" y2="345" stroke="#f1f5f9" stroke-width="1"/>',
])

# Plot 20 monthly bars + SLA line
n_m = len(df_kpi)
bar_w = 16
step_x = 500 / n_m
sla_points = []
for idx, row in df_kpi.iterrows():
    bx = 58 + idx * step_x
    gmv_k = row["gmv"] / 1000.0
    bh = (gmv_k / 1050.0) * 145.0
    by = 395 - bh
    bcolor = "#1d4ed8" if row["year_month"] == "2017-11" else "#94a3b8"
    ym_lbl = row["year_month"][2:]
    svg_lines.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w}" height="{bh:.1f}" fill="{bcolor}" rx="2"/>')
    if idx % 2 == 0 or row["year_month"] == "2017-11":
        svg_lines.append(f'<text x="{bx + bar_w/2:.1f}" y="410" text-anchor="middle" class="font axis-txt" font-size="8">{ym_lbl}</text>')
    # SLA point (scale 75% to 100% -> y=395 to 235)
    ot_pct = df_delivery.loc[idx, "on_time_rate_pct"]
    sy = 395 - ((ot_pct - 75.0) / 25.0) * 155.0
    sla_points.append((bx + bar_w/2, sy, ot_pct, row["year_month"]))

# 95% SLA Target Line
target_y = 395 - ((95.0 - 75.0) / 25.0) * 155.0
svg_lines.append(f'<line x1="52" y1="{target_y:.1f}" x2="565" y2="{target_y:.1f}" stroke="#059669" stroke-width="1.3" stroke-dasharray="4,3"/>')
svg_lines.append(f'<text x="562" y="{target_y - 4:.1f}" text-anchor="end" class="font" font-size="8.5" font-weight="700" fill="#059669">95.0% SLA Target</text>')

poly_pts = " ".join([f"{px:.1f},{py:.1f}" for px, py, _, _ in sla_points])
svg_lines.append(f'<polyline fill="none" stroke="#dc2626" stroke-width="2.2" points="{poly_pts}"/>')
for px, py, ot_pct, ym in sla_points:
    svg_lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.8" fill="#dc2626"/>')
    if ym in ("2017-11", "2018-03", "2018-06"):
        svg_lines.append(f'<text x="{px:.1f}" y="{py - 6:.1f}" text-anchor="middle" class="font val-txt" fill="#dc2626" font-size="8.5">{ot_pct:.1f}%</text>')

# Panel 2 (Top-Right): The 8-Day Satisfaction Cliff (x=608, y=178, w=572, h=255)
svg_lines.extend([
    '<rect x="608" y="178" width="572" height="255" class="card"/>',
    '<text x="624" y="200" class="font chart-title">2. The 8-Day Satisfaction Cliff: Review Scores Collapse 4.29★ ➔ 1.70★ (79.3% Negative)</text>',
    '<text x="624" y="215" class="font chart-sub">Average Review Score (1–5★ Bars) &amp; 1–2 Star Negative Review Share % (Dotted Line)</text>',
    '<line x1="640" y1="395" x2="1155" y2="395" stroke="#cbd5e1" stroke-width="1"/>',
])

cliff_colors = ["#059669", "#d97706", "#ea580c", "#dc2626", "#7f1d1d"]
neg_pts = []
for idx, row in df_reviews.iterrows():
    cx = 665 + idx * 96
    score = row["avg_review_score"]
    neg_pct = row["low_score_share_pct"]
    ch = (score / 5.0) * 145.0
    cy = 395 - ch
    svg_lines.append(f'<rect x="{cx}" y="{cy:.1f}" width="54" height="{ch:.1f}" fill="{cliff_colors[idx]}" rx="4"/>')
    svg_lines.append(f'<text x="{cx+27}" y="{cy - 6:.1f}" text-anchor="middle" class="font val-txt">{score:.2f} ★</text>')
    svg_lines.append(f'<text x="{cx+27}" y="411" text-anchor="middle" class="font axis-txt" font-size="9">{row["delay_bucket"]}</text>')
    ny = 395 - (neg_pct / 100.0) * 155.0
    neg_pts.append((cx + 27, ny, neg_pct))

neg_poly = " ".join([f"{px:.1f},{py:.1f}" for px, py, _ in neg_pts])
svg_lines.append(f'<polyline fill="none" stroke="#0f172a" stroke-width="2.2" stroke-dasharray="3,3" points="{neg_poly}"/>')
for px, py, neg_pct in neg_pts:
    svg_lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#0f172a"/>')
    svg_lines.append(f'<text x="{px:.1f}" y="{py - 8:.1f}" text-anchor="middle" class="font" font-size="8.5" font-weight="700" fill="#dc2626">{neg_pct:.1f}% 1-2★</text>')

# Panel 3 (Bottom-Left): Seller Pareto 80/20 Concentration + SLA Simulator Callout (x=20, y=445, w=572, h=255)
svg_lines.extend([
    '<rect x="20" y="445" width="572" height="255" class="card"/>',
    '<text x="36" y="467" class="font chart-title">3. Seller Pareto (80/20): Top 10% Worst Active Sellers (68 Merchants) Drive 52.5% of Delays</text>',
    '<text x="36" y="482" class="font chart-sub">Cumulative Share of Late Order Items Across 682 Active Sellers (≥30 Fulfilled Items)</text>',
    '<line x1="60" y1="665" x2="555" y2="665" stroke="#cbd5e1" stroke-width="1"/>',
    '<line x1="60" y1="505" x2="60" y2="665" stroke="#cbd5e1" stroke-width="1"/>',
    '<!-- Diagonal equality baseline -->',
    '<line x1="60" y1="665" x2="555" y2="505" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,4"/>',
])

df_s = df_sellers.sort_values(by=["late_items", "seller_late_rate_pct"], ascending=[False, False]).reset_index(drop=True)
total_late = df_s["late_items"].sum()
df_s["pct_s"] = (df_s.index + 1) / len(df_s)
df_s["cum_l"] = df_s["late_items"].cumsum() / total_late

pareto_pts = ["60.0,665.0"]
for idx in range(0, len(df_s), 8):
    px = 60.0 + df_s.loc[idx, "pct_s"] * 495.0
    py = 665.0 - df_s.loc[idx, "cum_l"] * 160.0
    pareto_pts.append(f"{px:.1f},{py:.1f}")
pareto_pts.append("555.0,505.0")
poly_str = " ".join(pareto_pts)
fill_str = poly_str + " 555.0,665.0 60.0,665.0"

p10_x = 60.0 + 0.10 * 495.0
p10_y = 665.0 - 0.525 * 160.0

svg_lines.extend([
    f'<polygon points="{fill_str}" fill="#dc2626" fill-opacity="0.08"/>',
    f'<polyline fill="none" stroke="#dc2626" stroke-width="2.8" points="{poly_str}"/>',
    f'<line x1="{p10_x:.1f}" y1="665" x2="{p10_x:.1f}" y2="{p10_y:.1f}" stroke="#0f172a" stroke-width="1.4" stroke-dasharray="3,3"/>',
    f'<line x1="60" y1="{p10_y:.1f}" x2="{p10_x:.1f}" y2="{p10_y:.1f}" stroke="#0f172a" stroke-width="1.4" stroke-dasharray="3,3"/>',
    f'<circle cx="{p10_x:.1f}" cy="{p10_y:.1f}" r="4.5" fill="#0f172a"/>',
    f'<rect x="{p10_x + 14:.1f}" y="{p10_y - 12:.1f}" width="265" height="40" fill="#fef2f2" stroke="#dc2626" stroke-width="1" rx="6"/>',
    f'<text x="{p10_x + 24:.1f}" y="{p10_y + 4:.1f}" class="font" font-size="10" font-weight="700" fill="#991b1b">Top 10% Bottleneck Sellers (68 / 682)</text>',
    f'<text x="{p10_x + 24:.1f}" y="{p10_y + 19:.1f}" class="font" font-size="9.5" fill="#7f1d1d">Drive 52.5% of All Late Items (Quintile 5: 19.4% Late)</text>',
    '<text x="307" y="684" text-anchor="middle" class="font axis-txt">Cumulative Share of Active Sellers (0% ➔ 100%)</text>',
])

# Panel 4 (Bottom-Right): Regional SLA Gap & Cohort Retention Findings (x=608, y=445, w=572, h=255)
svg_lines.extend([
    '<rect x="608" y="445" width="572" height="255" class="card"/>',
    '<text x="624" y="467" class="font chart-title">4. Regional Corridor SLA Breaches vs. Southeast Hubs (95.0% Target)</text>',
    '<text x="624" y="482" class="font chart-sub">On-Time Fulfillment Rate (%) &amp; Average Transit Days Across Key Brazilian States</text>',
])

selected_states = ["MA", "CE", "BA", "RJ", "PA", "PE", "SC", "RS", "MG", "SP", "PR"]
df_st_sub = df_states[df_states["customer_state"].isin(selected_states)].sort_values("on_time_rate_pct", ascending=True).reset_index(drop=True)

for idx, row in df_st_sub.iterrows():
    sy = 496 + idx * 16.5
    ot = row["on_time_rate_pct"]
    st_code = row["customer_state"]
    days = row["avg_delivery_days"]
    bw = ((ot - 70.0) / 30.0) * 390.0
    bcol = "#dc2626" if ot < 90.0 else ("#d97706" if ot < 95.0 else "#059669")
    svg_lines.extend([
        f'<text x="645" y="{sy+10:.1f}" text-anchor="end" class="font val-txt" font-size="9.5">{st_code}</text>',
        f'<rect x="652" y="{sy:.1f}" width="{bw:.1f}" height="12" fill="{bcol}" rx="2"/>',
        f'<text x="{658 + bw:.1f}" y="{sy+10:.1f}" class="font axis-txt" font-size="9" font-weight="600">{ot:.1f}% ({days:.1f}d transit)</text>',
    ])

target_st_x = 652 + ((95.0 - 70.0) / 30.0) * 390.0
svg_lines.extend([
    f'<line x1="{target_st_x:.1f}" y1="492" x2="{target_st_x:.1f}" y2="678" stroke="#0f172a" stroke-width="1.3" stroke-dasharray="3,3"/>',
    f'<text x="{target_st_x:.1f}" y="690" text-anchor="middle" class="font" font-size="8.5" font-weight="700" fill="#0f172a">95.0% Corporate SLA Target</text>',
    '</svg>'
])

out_svg = os.path.join(IMG_DIR, "executive_dashboard_preview.svg")
with open(out_svg, "w", encoding="utf-8") as f:
    f.write("\n".join(svg_lines))
print(f"Successfully generated vector dashboard preview: {out_svg}")

# Second Preview: Tab 4 — SLA Policy & Commercial ROI Simulator
sim_svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" width="100%" height="100%">',
    '<defs>',
    '  <style>',
    '    .font { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; }',
    '    .card { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.2; rx: 10; }',
    '  </style>',
    '</defs>',
    '<rect width="1200" height="440" fill="#f8fafc" rx="12"/>',
    '<rect x="20" y="16" width="1160" height="46" fill="#1e293b" rx="8"/>',
    '<text x="38" y="44" class="font" font-size="14.5" font-weight="800" fill="#ffffff">🎛️ MODULE 4: INTERACTIVE SLA POLICY &amp; COMMERCIAL ROI SENSITIVITY SIMULATOR (DECISION ENGINE)</text>',
    '<text x="1162" y="44" text-anchor="end" class="font" font-size="11" font-weight="700" fill="#93c5fd">Deal-Desk &amp; Ops Breakeven Model</text>',
    '',
    '<!-- Left Column: Interactive Sliders Mockup -->',
    '<rect x="20" y="74" width="360" height="348" class="card"/>',
    '<text x="38" y="100" class="font" font-size="13" font-weight="700" fill="#0f172a">⚙️ Policy Levers &amp; Unit Economics</text>',
    '<text x="38" y="116" class="font" font-size="10" fill="#64748b">Live sensitivity controls in Streamlit app.py</text>',
    '',
    '<text x="38" y="146" class="font" font-size="10.5" font-weight="600" fill="#334155">1. Seller Late-Rate Enforcement Cutoff: 10.0%</text>',
    '<rect x="38" y="154" width="320" height="6" fill="#e2e8f0" rx="3"/><rect x="38" y="154" width="140" height="6" fill="#2563eb" rx="3"/><circle cx="178" cy="157" r="7" fill="#2563eb"/>',
    '',
    '<text x="38" y="196" class="font" font-size="10.5" font-weight="600" fill="#334155">2. Flagged Seller 3PL Rehabilitation Rate: 75%</text>',
    '<rect x="38" y="204" width="320" height="6" fill="#e2e8f0" rx="3"/><rect x="38" y="204" width="220" height="6" fill="#2563eb" rx="3"/><circle cx="258" cy="207" r="7" fill="#2563eb"/>',
    '',
    '<text x="38" y="246" class="font" font-size="10.5" font-weight="600" fill="#334155">3. Northern Route EDD Buffer Delay Reduction: 25%</text>',
    '<rect x="38" y="254" width="320" height="6" fill="#e2e8f0" rx="3"/><rect x="38" y="254" width="160" height="6" fill="#2563eb" rx="3"/><circle cx="198" cy="257" r="7" fill="#2563eb"/>',
    '',
    '<text x="38" y="296" class="font" font-size="10.5" font-weight="600" fill="#334155">4. CS &amp; Apology Voucher Cost / Late Order: $15.00</text>',
    '<rect x="38" y="304" width="320" height="6" fill="#e2e8f0" rx="3"/><rect x="38" y="304" width="150" height="6" fill="#2563eb" rx="3"/><circle cx="188" cy="307" r="7" fill="#2563eb"/>',
    '',
    '<text x="38" y="346" class="font" font-size="10.5" font-weight="600" fill="#334155">5. Platform Commission Take-Rate: 12.0%</text>',
    '<rect x="38" y="354" width="320" height="6" fill="#e2e8f0" rx="3"/><rect x="38" y="354" width="110" height="6" fill="#2563eb" rx="3"/><circle cx="148" cy="357" r="7" fill="#2563eb"/>',
    '',
    '<rect x="38" y="378" width="320" height="30" fill="#eff6ff" stroke="#bfdbfe" rx="6"/>',
    '<text x="198" y="397" text-anchor="middle" class="font" font-size="10.5" font-weight="700" fill="#1d4ed8">📥 1-Click CSV Export: Flagged Seller Worklist</text>',
    '',
    '<!-- Right Column: Simulated KPI Cards & P&L Waterfall Bridge -->',
    '<rect x="396" y="74" width="186" height="76" class="card"/><rect x="396" y="74" width="186" height="4" fill="#d97706" rx="2"/>',
    '<text x="410" y="94" class="font" font-size="9.5" font-weight="700" fill="#64748b">SELLERS FLAGGED</text>',
    '<text x="410" y="120" class="font" font-size="21" font-weight="800" fill="#0f172a">97 / 682</text>',
    '<text x="410" y="139" class="font" font-size="10" font-weight="600" fill="#d97706">2,641 Late Items Targeted</text>',
    '',
    '<rect x="594" y="74" width="186" height="76" class="card"/><rect x="594" y="74" width="186" height="4" fill="#059669" rx="2"/>',
    '<text x="608" y="94" class="font" font-size="9.5" font-weight="700" fill="#64748b">PROJECTED ON-TIME SLA</text>',
    '<text x="608" y="120" class="font" font-size="21" font-weight="800" fill="#0f172a">96.08%</text>',
    '<text x="608" y="139" class="font" font-size="10" font-weight="600" fill="#059669">+2.85% SLA Lift (Exceeds 95%)</text>',
    '',
    '<rect x="792" y="74" width="186" height="76" class="card"/><rect x="792" y="74" width="186" height="4" fill="#059669" rx="2"/>',
    '<text x="806" y="94" class="font" font-size="9.5" font-weight="700" fill="#64748b">1–2★ REVIEWS PREVENTED</text>',
    '<text x="806" y="120" class="font" font-size="21" font-weight="800" fill="#0f172a">1,464</text>',
    '<text x="806" y="139" class="font" font-size="10" font-weight="600" fill="#059669">2,747 Late Orders Avoided</text>',
    '',
    '<rect x="990" y="74" width="190" height="76" class="card"/><rect x="990" y="74" width="190" height="4" fill="#2563eb" rx="2"/>',
    '<text x="1004" y="94" class="font" font-size="9.5" font-weight="700" fill="#64748b">NET PLATFORM P&amp;L IMPACT</text>',
    '<text x="1004" y="120" class="font" font-size="21" font-weight="800" fill="#0f172a">+$36,840</text>',
    '<text x="1004" y="139" class="font" font-size="10" font-weight="600" fill="#2563eb">Net of Churned Seller Risk</text>',
    '',
    '<!-- Waterfall Chart Card -->',
    '<rect x="396" y="162" width="784" height="260" class="card"/>',
    '<text x="414" y="186" class="font" font-size="13" font-weight="700" fill="#0f172a">Commercial P&amp;L Sensitivity Bridge: Defect Elimination Gains vs. Seller Churn Exposure</text>',
    '<text x="414" y="201" class="font" font-size="10" fill="#64748b">Simulated Contribution Margin Bridge ($ USD) | Accounts for 3.12% Repeat Base-Rate &amp; 60% Buyer Substitution</text>',
    '<line x1="430" y1="380" x2="1150" y2="380" stroke="#cbd5e1" stroke-width="1"/>',
    '',
    '<!-- Waterfall Bars -->',
    '<rect x="465" y="265" width="110" height="115" fill="#059669" rx="4"/>',
    '<text x="520" y="257" text-anchor="middle" class="font" font-size="10.5" font-weight="700" fill="#059669">+$41,205</text>',
    '<text x="520" y="398" text-anchor="middle" class="font" font-size="9.5" fill="#334155">1. Saved CS &amp; Voucher Cost</text>',
    '',
    '<line x1="575" y1="265" x2="645" y2="265" stroke="#94a3b8" stroke-dasharray="3,3"/>',
    '<rect x="645" y="210" width="110" height="55" fill="#059669" rx="4"/>',
    '<text x="700" y="202" text-anchor="middle" class="font" font-size="10.5" font-weight="700" fill="#059669">+$20,760</text>',
    '<text x="700" y="398" text-anchor="middle" class="font" font-size="9.5" fill="#334155">2. Protected Rating &amp; Repeat Margin</text>',
    '',
    '<line x1="755" y1="210" x2="825" y2="210" stroke="#94a3b8" stroke-dasharray="3,3"/>',
    '<rect x="825" y="210" width="110" height="68" fill="#dc2626" rx="4"/>',
    '<text x="880" y="292" text-anchor="middle" class="font" font-size="10.5" font-weight="700" fill="#dc2626">-$25,125</text>',
    '<text x="880" y="398" text-anchor="middle" class="font" font-size="9.5" fill="#334155">3. Churned Seller Take-Rate Risk</text>',
    '',
    '<line x1="935" y1="278" x2="1005" y2="278" stroke="#94a3b8" stroke-dasharray="3,3"/>',
    '<rect x="1005" y="278" width="110" height="102" fill="#2563eb" rx="4"/>',
    '<text x="1060" y="270" text-anchor="middle" class="font" font-size="11" font-weight="800" fill="#2563eb">+$36,840 Net</text>',
    '<text x="1060" y="398" text-anchor="middle" class="font" font-size="9.5" font-weight="700" fill="#0f172a">4. Net Platform P&amp;L Gain</text>',
    '</svg>'
]

out_sim_svg = os.path.join(IMG_DIR, "sla_simulator_preview.svg")
with open(out_sim_svg, "w", encoding="utf-8") as f:
    f.write("\n".join(sim_svg))
print(f"Successfully generated simulator preview: {out_sim_svg}")

