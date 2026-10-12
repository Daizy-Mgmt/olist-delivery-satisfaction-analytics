import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "docs", "results")
IMG_DIR = os.path.join(BASE_DIR, "docs", "images")
os.makedirs(IMG_DIR, exist_ok=True)

df_kpi = pd.read_csv(os.path.join(RESULTS_DIR, "01_kpi_overview.csv"))
df_delivery = pd.read_csv(os.path.join(RESULTS_DIR, "02_delivery_performance.csv"))
df_reviews = pd.read_csv(os.path.join(RESULTS_DIR, "03_delay_vs_review.csv"))
df_states = pd.read_csv(os.path.join(RESULTS_DIR, "04_state_delay_hotspots.csv"))
df_sellers = pd.read_csv(os.path.join(RESULTS_DIR, "05_seller_scorecard.csv"))

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.edgecolor"] = "#cbd5e1"
plt.rcParams["axes.linewidth"] = 0.8

# =============================================================================
# PNG 1: Executive KPI Scorecard, Satisfaction Cliff & Seller Pareto
# =============================================================================
fig = plt.figure(figsize=(18, 10.5), dpi=180, facecolor="#f8fafc")
gs = gridspec.GridSpec(3, 12, figure=fig, height_ratios=[0.95, 2.5, 2.5], hspace=0.42, wspace=0.65)

ax_banner = fig.add_subplot(gs[0, :])
ax_banner.set_facecolor("#f8fafc")
ax_banner.axis("off")

ax_banner.text(0.0, 0.88, "OLIST COMMERCIAL OPERATIONS & DELIVERY SLA EXECUTIVE SUITE", fontsize=16, fontweight="bold", color="#0f172a")
ax_banner.text(0.0, 0.62, "Star Schema Mart (PostgreSQL 15) · 10 Reconciled Power BI DAX Measures · 99,441 Orders ($13,591,643.70 GMV | 0.00% DAX Variance)", fontsize=10.5, color="#475569")

kpis = [
    ("RECONCILED TOTAL GMV", "$13.59M", "+8.3x 2017 Scale (Peak $1.00M)", "#059669"),
    ("DELIVERED ORDERS", "96,470", "99,441 Total (97.0% Completion)", "#2563eb"),
    ("AVERAGE ORDER VALUE", "$136.68", "Reconciled SQL = DAX Exact", "#2563eb"),
    ("ON-TIME FULFILLMENT SLA", "93.23%", "-1.77% vs 95.0% Target (6,534 Late)", "#dc2626"),
    ("CUSTOMER CSAT (REVIEW)", "4.09 / 5.0", "1.70/5.0 when 8+d Late (79.3% 1-2 Star)", "#d97706"),
]

for idx, (title, val, sub, color) in enumerate(kpis):
    x0 = idx * 0.202
    rect = plt.Rectangle((x0, 0.02), 0.19, 0.50, facecolor="#ffffff", edgecolor="#e2e8f0", linewidth=1.2, transform=ax_banner.transAxes, zorder=2)
    top_bar = plt.Rectangle((x0, 0.49), 0.19, 0.04, facecolor=color, edgecolor="none", transform=ax_banner.transAxes, zorder=3)
    ax_banner.add_patch(rect)
    ax_banner.add_patch(top_bar)
    ax_banner.text(x0 + 0.012, 0.37, title, fontsize=8, fontweight="bold", color="#64748b", transform=ax_banner.transAxes, zorder=4)
    ax_banner.text(x0 + 0.012, 0.18, val, fontsize=15, fontweight="bold", color="#0f172a", transform=ax_banner.transAxes, zorder=4)
    ax_banner.text(x0 + 0.012, 0.06, sub, fontsize=7.8, fontweight="bold", color=color, transform=ax_banner.transAxes, zorder=4)

# Chart 1: Monthly GMV & On-Time SLA Trajectory
ax1 = fig.add_subplot(gs[1, :6])
ax1.set_facecolor("#ffffff")
months_short = [m[2:] for m in df_kpi["year_month"]]
bar_colors = ["#1d4ed8" if m == "2017-11" else "#94a3b8" for m in df_kpi["year_month"]]
ax1.bar(months_short, df_kpi["gmv"] / 1e3, color=bar_colors, width=0.65, label="Monthly GMV ($K)")
ax1.set_title("1. GMV Scaled 8.3x in 2017 (Peak $1.00M in Nov Black Friday)", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=10)
ax1.set_ylabel("GMV ($ Thousands)", fontsize=9, color="#475569")
ax1.tick_params(axis="x", rotation=45, labelsize=8)
ax1.tick_params(axis="y", labelsize=8)
ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#cbd5e1")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

ax1_twin = ax1.twinx()
ax1_twin.plot(months_short, df_delivery["on_time_rate_pct"], color="#dc2626", marker="o", linewidth=2, markersize=4, label="On-Time SLA %")
ax1_twin.axhline(95.0, color="#059669", linestyle="--", linewidth=1.2)
ax1_twin.set_ylabel("On-Time Rate (%)", fontsize=9, color="#dc2626")
ax1_twin.set_ylim(75, 102)
ax1_twin.tick_params(axis="y", labelsize=8, colors="#dc2626")
ax1_twin.spines["top"].set_visible(False)

# Chart 2: The 8-Day Satisfaction Cliff
ax2 = fig.add_subplot(gs[1, 6:])
ax2.set_facecolor("#ffffff")
cliff_colors = ["#059669", "#d97706", "#ea580c", "#dc2626", "#7f1d1d"]
bars = ax2.bar(df_reviews["delay_bucket"], df_reviews["avg_review_score"], color=cliff_colors, width=0.55)
ax2.set_title("2. The 8-Day Satisfaction Cliff: Ratings Plunge 4.29 -> 1.70 / 5.0 (79.3% 1-2 Star)", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=10)
ax2.set_ylabel("Average Review Score (1.0 - 5.0)", fontsize=9, color="#475569")
ax2.set_ylim(0, 5.3)
ax2.tick_params(axis="x", labelsize=8.5)
ax2.tick_params(axis="y", labelsize=8)
ax2.grid(axis="y", linestyle="--", alpha=0.4, color="#cbd5e1")
ax2.spines["top"].set_visible(False)

for bar, score in zip(bars, df_reviews["avg_review_score"]):
    ax2.text(bar.get_x() + bar.get_width()/2, score + 0.12, f"{score:.2f} / 5", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0f172a")

ax2_twin = ax2.twinx()
ax2_twin.plot(df_reviews["delay_bucket"], df_reviews["low_score_share_pct"], color="#0f172a", linestyle=":", marker="s", linewidth=2.2, markersize=5)
ax2_twin.set_ylabel("1-2 Star Negative Share (%)", fontsize=9, color="#0f172a")
ax2_twin.set_ylim(0, 95)
ax2_twin.tick_params(axis="y", labelsize=8)
ax2_twin.spines["top"].set_visible(False)

# Chart 3: Seller Pareto 80/20 Curve
ax3 = fig.add_subplot(gs[2, :6])
ax3.set_facecolor("#ffffff")
df_s = df_sellers.sort_values(by=["late_items", "seller_late_rate_pct"], ascending=[False, False]).reset_index(drop=True)
df_s["pct_sellers"] = (df_s.index + 1) / len(df_s) * 100
df_s["cum_late_pct"] = df_s["late_items"].cumsum() / df_s["late_items"].sum() * 100

ax3.plot(df_s["pct_sellers"], df_s["cum_late_pct"], color="#dc2626", linewidth=2.6, label="Cumulative Late Items (%)")
ax3.fill_between(df_s["pct_sellers"], df_s["cum_late_pct"], color="#dc2626", alpha=0.08)
ax3.plot([0, 100], [0, 100], color="#94a3b8", linestyle="--", linewidth=1.2, label="Equal Distribution")
ax3.axvline(10.0, color="#0f172a", linestyle=":", linewidth=1.5)
ax3.axhline(52.5, color="#0f172a", linestyle=":", linewidth=1.5)
ax3.scatter([10.0], [52.5], color="#0f172a", s=45, zorder=5)
ax3.annotate("Top 10% Worst Sellers (68 Merchants)\nDrive 52.5% of All Late Items", xy=(10.0, 52.5), xytext=(22, 38),
             arrowprops=dict(arrowstyle="->", color="#0f172a", lw=1.2), fontsize=8.5, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef2f2", edgecolor="#dc2626"))
ax3.set_title("3. Pareto Bottleneck Concentration: 10% of Active Sellers Drive 52.5% of Delays", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=10)
ax3.set_xlabel("Share of Active Sellers Ranked by Late Volume (%)", fontsize=9, color="#475569")
ax3.set_ylabel("Cumulative Late Items (%)", fontsize=9, color="#475569")
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 105)
ax3.grid(True, linestyle="--", alpha=0.4, color="#cbd5e1")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

# Chart 4: Regional SLA Disparities
ax4 = fig.add_subplot(gs[2, 6:])
ax4.set_facecolor("#ffffff")
df_st = df_states.sort_values("on_time_rate_pct", ascending=True).head(12)
st_colors = ["#dc2626" if v < 90.0 else ("#d97706" if v < 95.0 else "#059669") for v in df_st["on_time_rate_pct"]]
bars_st = ax4.barh(df_st["customer_state"], df_st["on_time_rate_pct"], color=st_colors, height=0.65)
ax4.axvline(95.0, color="#0f172a", linestyle="--", linewidth=1.4, label="95.0% SLA Target")
ax4.set_title("4. Regional SLA Gap: Northern/Northeastern States Miss 95% Target by up to 12.4 pts", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=10)
ax4.set_xlabel("On-Time Delivery Rate (%)", fontsize=9, color="#475569")
ax4.set_xlim(75, 100)
ax4.tick_params(axis="both", labelsize=8.5)
ax4.grid(axis="x", linestyle="--", alpha=0.4, color="#cbd5e1")
ax4.spines["top"].set_visible(False)
ax4.spines["right"].set_visible(False)

for bar, v in zip(bars_st, df_st["on_time_rate_pct"]):
    ax4.text(v + 0.35, bar.get_y() + bar.get_height()/2, f"{v:.1f}%", va="center", fontsize=8, fontweight="bold", color="#1e293b")

out_png1 = os.path.join(IMG_DIR, "executive_dashboard_preview.png")
plt.savefig(out_png1, bbox_inches="tight", facecolor="#f8fafc")
plt.close(fig)
print(f"Saved high-res PNG 1: {out_png1}")

# =============================================================================
# PNG 2: Multi-Lever SLA Policy & Breakeven Sensitivity Matrix (Module 4)
# =============================================================================
fig2 = plt.figure(figsize=(18, 6.2), dpi=180, facecolor="#f8fafc")
gs2 = gridspec.GridSpec(1, 12, figure=fig2, wspace=0.85)

# Left Panel: 4-Lever Waterfall Bridge
ax_wf = fig2.add_subplot(gs2[0, :6])
ax_wf.set_facecolor("#ffffff")
levers = [
    "Lever A:\n1-2 Star Deterrence\n(Conversion)",
    "Lever B:\nSaved CS &\nVoucher Cost",
    "Lever C:\nRepeat Lift\n(+0.77pp Base)",
    "Lever D:\nChurned Seller\nTake-Rate Risk",
    "Net Platform\nP&L Impact"
]
vals = [20.4, 41.2, 0.4, -25.1, 36.9]
bottoms = [0, 20.4, 61.6, 36.9, 0]
heights = [20.4, 41.2, 0.4, 25.1, 36.9]
wf_colors = ["#059669", "#059669", "#10b981", "#dc2626", "#2563eb"]

bars_wf = ax_wf.bar(levers, heights, bottom=bottoms, color=wf_colors, width=0.52)
ax_wf.set_title("Module 4A: 4-Lever Commercial P&L Bridge ($K USD) — Base-Rate Adjusted (3.12% Repeat Base)", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=12)
ax_wf.set_ylabel("Platform Contribution Margin Impact ($K)", fontsize=9, color="#475569")
ax_wf.set_ylim(0, 74)
ax_wf.grid(axis="y", linestyle="--", alpha=0.4, color="#cbd5e1")
ax_wf.spines["top"].set_visible(False)
ax_wf.spines["right"].set_visible(False)
ax_wf.tick_params(axis="x", labelsize=8.5)

labels_wf = ["+$20.4K", "+$41.2K", "+$0.4K", "-$25.1K", "+$36.9K Net"]
tops_wf = [20.4, 61.6, 62.0, 62.0, 36.9]
for bar, lbl, top_y in zip(bars_wf, labels_wf, tops_wf):
    ax_wf.text(bar.get_x() + bar.get_width()/2, top_y + 1.5, lbl, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0f172a")

# Right Panel: 2D Breakeven Sensitivity Heatmap (Rehab Rate % x Buyer Substitution %)
ax_hm = fig2.add_subplot(gs2[0, 6:])
rehab_grid = [40, 50, 60, 70, 80, 90]
sub_grid = [30, 40, 50, 60, 70, 80]

flagged_sellers = df_sellers[df_sellers["seller_late_rate_pct"] >= 10.0]
flagged_items_total = int(flagged_sellers["total_items"].sum())
flagged_late_items = int(flagged_sellers["late_items"].sum())
avg_item_gmv = 13591643.70 / 112650

mat = np.zeros((len(rehab_grid), len(sub_grid)))
for i, r_p in enumerate(rehab_grid):
    for j, s_p in enumerate(sub_grid):
        late_s = int(flagged_late_items * (r_p / 100.0) * 0.75)
        rem_l = max(0, 6534 - late_s)
        late_e = int(rem_l * 0.25)
        tot_p = min(6534, late_s + late_e)
        neg_av = int(tot_p * 0.533)
        la = neg_av * 0.85 * 136.68 * 0.12
        lb = tot_p * 15.0
        lc = tot_p * 0.0077 * 136.68 * 0.12
        ld = flagged_items_total * ((100.0 - r_p)/100.0) * avg_item_gmv * ((100.0 - s_p)/100.0) * 0.12
        mat[i, j] = (la + lb + lc - ld) / 1000.0

im = ax_hm.imshow(mat, cmap="RdYlGn", aspect="auto", vmin=-25, vmax=55)
ax_hm.set_xticks(range(len(sub_grid)))
ax_hm.set_xticklabels([f"{s}% Sub." for s in sub_grid], fontsize=8.5)
ax_hm.set_yticks(range(len(rehab_grid)))
ax_hm.set_yticklabels([f"{r}% Rehab." for r in rehab_grid], fontsize=8.5)
ax_hm.set_xlabel("Buyer Demand Substitution to Compliant Sellers (%)", fontsize=9, color="#475569")
ax_hm.set_ylabel("Flagged Seller 3PL Rehabilitation Rate (%)", fontsize=9, color="#475569")
ax_hm.set_title("Module 4B: 2D Breakeven Sensitivity Matrix — Net Platform P&L ($K USD)", fontsize=11, fontweight="bold", color="#0f172a", loc="left", pad=12)

for i in range(len(rehab_grid)):
    for j in range(len(sub_grid)):
        val = mat[i, j]
        txt_col = "#ffffff" if abs(val) > 32 else "#0f172a"
        ax_hm.text(j, i, f"${val:+.1f}K", ha="center", va="center", fontsize=8.5, fontweight="bold", color=txt_col)

out_png2 = os.path.join(IMG_DIR, "sla_simulator_preview.png")
plt.savefig(out_png2, bbox_inches="tight", facecolor="#f8fafc")
plt.close(fig2)
print(f"Saved high-res PNG 2: {out_png2}")
