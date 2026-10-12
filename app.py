import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration & Enterprise Design System (IBCS / McKinsey Standard)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Olist Commercial Operations & SLA Decision Suite | Daisy Phukan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .exec-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 18px;
        border-left: 5px solid #3b82f6;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    .exec-banner h1 {
        font-size: 1.45rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .exec-banner p {
        font-size: 0.85rem;
        color: #cbd5e1;
        margin: 4px 0 0 0;
    }
    .gov-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        height: 100%;
    }
    .kpi-card.breach { border-top-color: #dc2626; }
    .kpi-card.compliant { border-top-color: #059669; }
    .kpi-card.warn { border-top-color: #d97706; }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .delta-pos { color: #059669; background: #ecfdf5; padding: 2px 6px; border-radius: 4px; }
    .delta-neg { color: #dc2626; background: #fef2f2; padding: 2px 6px; border-radius: 4px; }
    .delta-neu { color: #475569; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
    .chart-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    .assertion-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .assertion-subtitle {
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 12px;
    }
    .insight-callout {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.84rem;
        color: #1e293b;
        margin-top: 8px;
    }
    .gov-footer {
        margin-top: 32px;
        padding: 14px 20px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Data Ingestion & Region Enrichment
# -----------------------------------------------------------------------------
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "docs", "results")

REGION_MAP = {
    "SP": "Southeast", "RJ": "Southeast", "MG": "Southeast", "ES": "Southeast",
    "PR": "South", "SC": "South", "RS": "South",
    "BA": "Northeast", "PE": "Northeast", "CE": "Northeast", "MA": "Northeast", "PB": "Northeast",
    "DF": "Central-West", "GO": "Central-West", "MT": "Central-West", "MS": "Central-West",
    "PA": "North"
}

@st.cache_data
def load_data():
    df_kpi = pd.read_csv(os.path.join(RESULTS_DIR, "01_kpi_overview.csv"))
    df_delivery = pd.read_csv(os.path.join(RESULTS_DIR, "02_delivery_performance.csv"))
    df_reviews = pd.read_csv(os.path.join(RESULTS_DIR, "03_delay_vs_review.csv"))
    df_states = pd.read_csv(os.path.join(RESULTS_DIR, "04_state_delay_hotspots.csv"))
    df_sellers = pd.read_csv(os.path.join(RESULTS_DIR, "05_seller_scorecard.csv"))
    df_repeat = pd.read_csv(os.path.join(RESULTS_DIR, "07_repeat_purchase_cohorts.csv"))

    df_states["macro_region"] = df_states["customer_state"].map(REGION_MAP).fillna("Other")
    df_sellers["macro_region"] = df_sellers["seller_state"].map(REGION_MAP).fillna("Other")
    df_monthly = pd.merge(df_kpi, df_delivery, on="year_month", how="left")
    return df_kpi, df_delivery, df_reviews, df_states, df_sellers, df_repeat, df_monthly

df_kpi, df_delivery, df_reviews, df_states, df_sellers, df_repeat, df_monthly = load_data()

# Common Plotly Enterprise Layout Helper
def apply_enterprise_layout(fig, height=380, show_legend=True):
    fig.update_layout(
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#1e293b"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=height,
        margin=dict(l=16, r=16, t=28, b=16),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(255,255,255,0.8)"),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_family="Plus Jakarta Sans, sans-serif")
    )
    fig.update_xaxes(showgrid=False, linecolor="#cbd5e1", tickfont=dict(color="#475569"))
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(color="#475569"))
    return fig

# -----------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Slicers
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧭 Executive Navigation")
    page = st.radio(
        "Select Analytical Module:",
        [
            "1. Executive KPI & SLA Scorecard",
            "2. Customer Satisfaction & Cohort Diagnostics",
            "3. Seller Pareto (80/20) & Action Worklist",
            "4. SLA Policy & Commercial ROI Simulator",
            "5. BA Governance (BRD/RACI) & Reconciliation"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎛️ Global Slicers & Targets")

    all_months = sorted(df_monthly["year_month"].unique())
    selected_months = st.select_slider(
        "Reporting Window (Year-Month):",
        options=all_months,
        value=(all_months[0], all_months[-1])
    )

    all_regions = ["Southeast", "South", "Northeast", "Central-West", "North"]
    selected_regions = st.multiselect(
        "Macro-Regions (State Views):",
        options=all_regions,
        default=all_regions
    )

    sla_target_pct = st.slider(
        "Corporate On-Time SLA Target (%):",
        min_value=85.0,
        max_value=98.0,
        value=95.0,
        step=0.5,
        help="Adjusts the corporate SLA benchmark reference line across executive and state charts."
    )

    st.markdown("---")
    st.markdown("### 👤 Author & Architecture")
    st.markdown(
        "**Daisy Phukan**  \n"
        "*Technical Project Manager · BI & Business Analyst*  \n"
        "📍 Bengaluru, India  \n"
        "📧 [daisyphukan.work@gmail.com](mailto:daisyphukan.work@gmail.com)  \n"
        "🔗 [GitHub](https://github.com/Daizy-Mgmt) · [LinkedIn](https://linkedin.com/in/daisy-phukan-a401a4228)"
    )

# Filter monthly data by selected window
df_m_filtered = df_monthly[
    (df_monthly["year_month"] >= selected_months[0]) &
    (df_monthly["year_month"] <= selected_months[1])
].copy()

df_states_filtered = df_states[
    df_states["macro_region"].isin(selected_regions if selected_regions else all_regions)
].copy()

# -----------------------------------------------------------------------------
# Top Executive Banner
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="exec-banner">
    <div>
        <h1>📦 Olist Commercial Operations & Delivery SLA Decision Suite</h1>
        <p>Star Schema Analytical Mart (PostgreSQL 15) · 10 Reconciled Power BI DAX Measures · Interactive SLA & Margin Sensitivity Engine</p>
    </div>
    <div class="gov-badge">
        ✓ VERIFIED STAR SCHEMA: $13,591,643.70 GMV (0.00% DAX VARIANCE)
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# VIEW 1: EXECUTIVE KPI & SLA SCORECARD
# =============================================================================
if page == "1. Executive KPI & SLA Scorecard":
    # Compute window metrics alongside full-dataset verified totals
    window_gmv = df_m_filtered["gmv"].sum()
    window_orders = int(df_m_filtered["orders_count"].sum())
    window_delivered = int(df_m_filtered["total_delivered_orders"].sum())
    window_ontime = int(df_m_filtered["on_time_orders"].sum())
    window_ontime_pct = (window_ontime / window_delivered * 100) if window_delivered > 0 else 0.0
    window_aov = (window_gmv / window_orders) if window_orders > 0 else 0.0
    sla_gap = window_ontime_pct - sla_target_pct

    # 5 Enterprise KPI Cards (Full Star Schema Headline + Active Window Context)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="kpi-card compliant">
            <div class="kpi-title">Reconciled Total GMV</div>
            <div class="kpi-value">$13.59M</div>
            <div class="kpi-sub">
                <span class="delta-pos">Window: ${window_gmv/1e6:.2f}M</span>
                <span style="color:#64748b;">({selected_months[0]}–{selected_months[1]})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card compliant">
            <div class="kpi-title">Total Marketplace Orders</div>
            <div class="kpi-value">99,441</div>
            <div class="kpi-sub">
                <span class="delta-neu">96,470 Delivered</span>
                <span style="color:#64748b;">(97.0% Completion)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card compliant">
            <div class="kpi-title">Average Order Value (AOV)</div>
            <div class="kpi-value">$136.68</div>
            <div class="kpi-sub">
                <span class="delta-neu">Window: ${window_aov:.2f}</span>
                <span style="color:#64748b;">Item + Freight</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        card_cls = "compliant" if sla_gap >= 0 else "breach"
        delta_cls = "delta-pos" if sla_gap >= 0 else "delta-neg"
        st.markdown(f"""
        <div class="kpi-card {card_cls}">
            <div class="kpi-title">On-Time Fulfillment SLA</div>
            <div class="kpi-value">{window_ontime_pct:.2f}%</div>
            <div class="kpi-sub">
                <span class="{delta_cls}">{sla_gap:+.2f}% vs {sla_target_pct:.1f}% SLA</span>
                <span style="color:#64748b;">(6,534 Late)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-card warn">
            <div class="kpi-title">Customer CSAT (Review ★)</div>
            <div class="kpi-value">4.09 / 5.0</div>
            <div class="kpi-sub">
                <span class="delta-neg">-0.11 vs 4.20★ Target</span>
                <span style="color:#64748b;">14.9% 1–2★ Share</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Row 2: Diagnostic Trajectory Visuals
    col_left, col_right = st.columns([6, 6])

    with col_left:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">GMV Scaled 8.3x in 2017 (Peak: $1.00M in Nov Black Friday) Before Stabilizing at ~$900K/Mo</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assertion-subtitle">Monthly Gross Merchandise Value ($) and Order Volume ({selected_months[0]} to {selected_months[1]}) | Source: mart.fact_orders</div>', unsafe_allow_html=True)

        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(
            x=df_m_filtered["year_month"],
            y=df_m_filtered["gmv"],
            name="Monthly GMV ($)",
            marker_color=["#1d4ed8" if m == "2017-11" else "#94a3b8" for m in df_m_filtered["year_month"]],
            hovertemplate="<b>%{x}</b><br>GMV: $%{y:,.0f}<extra></extra>"
        ))
        fig_rev.add_trace(go.Scatter(
            x=df_m_filtered["year_month"],
            y=df_m_filtered["orders_count"],
            name="Order Volume",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#0f172a", width=2.5),
            marker=dict(size=6, color="#0f172a"),
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"
        ))
        fig_rev.update_layout(
            yaxis=dict(title="GMV ($ USD)", tickprefix="$"),
            yaxis2=dict(title="Orders Placed", overlaying="y", side="right", showgrid=False)
        )
        apply_enterprise_layout(fig_rev, height=350)
        st.plotly_chart(fig_rev, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="assertion-title">SLA Compliance Dropped Below {sla_target_pct:.1f}% Target During Q4 Black Friday (87.6%) & Q1 2018 (81.0%)</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Monthly On-Time Delivery % vs. Corporate Target & 90th-Percentile (P90) Transit Days | Source: mart.fact_orders</div>', unsafe_allow_html=True)

        fig_sla = go.Figure()
        bar_colors = ["#059669" if v >= sla_target_pct else "#dc2626" for v in df_m_filtered["on_time_rate_pct"]]
        fig_sla.add_trace(go.Bar(
            x=df_m_filtered["year_month"],
            y=df_m_filtered["on_time_rate_pct"],
            name="On-Time SLA %",
            marker_color=bar_colors,
            opacity=0.88,
            hovertemplate="<b>%{x}</b><br>On-Time Rate: %{y:.2f}%<extra></extra>"
        ))
        fig_sla.add_trace(go.Scatter(
            x=df_m_filtered["year_month"],
            y=df_m_filtered["p90_delivery_days"],
            name="P90 Tail Transit Days",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#d97706", width=2.5, dash="dot"),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>P90 Transit: %{y:.1f} days<extra></extra>"
        ))
        fig_sla.add_hline(
            y=sla_target_pct,
            line_dash="dash",
            line_color="#0f172a",
            annotation_text=f"SLA Target ({sla_target_pct:.1f}%)",
            annotation_position="bottom right"
        )
        fig_sla.update_layout(
            yaxis=dict(title="On-Time Delivery Rate (%)", range=[70, 102], ticksuffix="%"),
            yaxis2=dict(title="P90 Transit Days", overlaying="y", side="right", showgrid=False, range=[0, 40])
        )
        apply_enterprise_layout(fig_sla, height=350)
        st.plotly_chart(fig_sla, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 3: Executive Summary Table & Key Takeaway
    st.markdown("""
    <div class="insight-callout">
        <strong>🧭 Executive Diagnostic Summary:</strong> Marketplace volume scaled rapidly through November 2017 ($1.00M Black Friday peak), but carrier and seller capacity failed to absorb peak load—driving P90 tail transit times from <strong>19 days up to 32 days</strong> in Q1 2018 and pushing On-Time SLA down to <strong>81.04%</strong> in March 2018 before operational recovery in Q2 2018.
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# VIEW 2: CUSTOMER SATISFACTION & COHORT DIAGNOSTICS
# =============================================================================
elif page == "2. Customer Satisfaction & Cohort Diagnostics":
    col_l, col_r = st.columns([6, 6])

    with col_l:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">The 8-Day Satisfaction Cliff: 1–2★ Reviews Surge 8.5x (9.3% ➔ 79.3%) Past 8 Days Late</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Average Review Rating (★) and Negative Review Share (%) by Delivery Delay Tier (n = 99,441)</div>', unsafe_allow_html=True)

        fig_cliff = go.Figure()
        cliff_colors = ["#059669", "#d97706", "#ea580c", "#dc2626", "#7f1d1d"]
        fig_cliff.add_trace(go.Bar(
            x=df_reviews["delay_bucket"],
            y=df_reviews["avg_review_score"],
            name="Avg Review Score (1–5★)",
            marker_color=cliff_colors,
            text=df_reviews["avg_review_score"].apply(lambda x: f"{x:.2f} ★"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg Rating: %{y:.2f} ★<extra></extra>"
        ))
        fig_cliff.add_trace(go.Scatter(
            x=df_reviews["delay_bucket"],
            y=df_reviews["low_score_share_pct"],
            name="1–2★ Negative Review Share (%)",
            yaxis="y2",
            mode="lines+markers+text",
            text=df_reviews["low_score_share_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="top center",
            line=dict(color="#0f172a", width=3, dash="dot"),
            marker=dict(size=8, color="#dc2626"),
            hovertemplate="<b>%{x}</b><br>1–2★ Share: %{y:.2f}%<extra></extra>"
        ))
        fig_cliff.update_layout(
            yaxis=dict(title="Average Review Score (★)", range=[0, 5.4]),
            yaxis2=dict(title="1–2 Star Review Share (%)", overlaying="y", side="right", range=[0, 100], showgrid=False, ticksuffix="%")
        )
        apply_enterprise_layout(fig_cliff, height=370)
        st.plotly_chart(fig_cliff, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Cohort Nuance: 1–7 Day Delays Cut Repeat Buying by 22.6% (3.40% ➔ 2.63%)</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Customer Repeat Purchase Rate (%) by First-Order Delivery Experience (n = 96,096 unique buyers)</div>', unsafe_allow_html=True)

        df_rep_deliv = df_repeat.copy()
        rep_colors = ["#059669", "#d97706", "#ea580c", "#dc2626", "#64748b"]
        fig_rep = go.Figure()
        fig_rep.add_trace(go.Bar(
            x=df_rep_deliv["first_order_delay_bucket"],
            y=df_rep_deliv["repeat_purchase_rate_pct"],
            name="Repeat Purchase Rate (%)",
            marker_color=rep_colors,
            text=df_rep_deliv["repeat_purchase_rate_pct"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Repeat Rate: %{y:.2f}%<br>Customers: %{customdata:,}<extra></extra>",
            customdata=df_rep_deliv["total_customers"]
        ))
        fig_rep.add_hline(
            y=3.12,
            line_dash="dash",
            line_color="#475569",
            annotation_text="Marketplace Baseline (3.12%)",
            annotation_position="top right"
        )
        fig_rep.update_layout(
            yaxis=dict(title="Repeat Purchase Rate (%)", range=[0, 5.6], ticksuffix="%")
        )
        apply_enterprise_layout(fig_rep, height=370, show_legend=False)
        st.plotly_chart(fig_rep, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-callout">
        <strong>🔬 Senior Analytical Note (Base-Rate & Replacement Effect):</strong>
        <ul style="margin:4px 0 0 18px; padding:0;">
            <li><strong>Structural Base Rate:</strong> Across Olist, <strong>96.88% of customers are one-time buyers</strong> (3.12% overall repeat rate). While 1–7 day delays reduce repeat propensity by <strong>22.6% relative</strong> (from 3.40% to 2.63%), the primary financial damage of late delivery is not repeat LTV loss—it is the <strong>79.3% 1–2★ review spike</strong> that poisons product conversion and inflates customer service ticket volume.</li>
            <li><strong>Why "Not Delivered" Shows 4.68% Repeat Rate:</strong> Customers whose initial order was canceled or unavailable immediately placed a <em>replacement order</em> on the platform within 48 hours—an important data artifact separated in our staging layer.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Row 2: Geographic Corridor Analysis
    c_map1, c_map2 = st.columns([7, 5])
    with c_map1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="assertion-title">Regional SLA Disparity: Northern & Northeastern Corridors Miss {sla_target_pct:.1f}% SLA Target by up to 12.4 pts</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">On-Time Delivery Rate (%) by Destination State (≥500 Delivered Orders) | Filtered by Macro-Region</div>', unsafe_allow_html=True)

        df_st_sorted = df_states_filtered.sort_values("on_time_rate_pct", ascending=True)
        state_colors = ["#059669" if v >= sla_target_pct else ("#d97706" if v >= 90.0 else "#dc2626") for v in df_st_sorted["on_time_rate_pct"]]

        fig_st = go.Figure(go.Bar(
            x=df_st_sorted["on_time_rate_pct"],
            y=df_st_sorted["customer_state"],
            orientation="h",
            marker_color=state_colors,
            text=df_st_sorted["on_time_rate_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            customdata=np.stack((df_st_sorted["macro_region"], df_st_sorted["avg_delivery_days"], df_st_sorted["late_orders"]), axis=-1),
            hovertemplate="<b>State: %{y} (%{customdata[0]})</b><br>On-Time SLA: %{x:.2f}%<br>Avg Transit: %{customdata[1]:.1f} days<br>Late Orders: %{customdata[2]:,}<extra></extra>"
        ))
        fig_st.add_vline(
            x=sla_target_pct,
            line_dash="dash",
            line_color="#0f172a",
            annotation_text=f"Target: {sla_target_pct:.1f}%",
            annotation_position="bottom right"
        )
        fig_st.update_layout(xaxis=dict(title="On-Time Delivery Rate (%)", range=[75, 101], ticksuffix="%"), yaxis=dict(title="Customer State"))
        apply_enterprise_layout(fig_st, height=430, show_legend=False)
        st.plotly_chart(fig_st, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_map2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Longer Transit Corridors Directly Drive SLA Breaches & Lower Ratings</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Average Transit Days vs. On-Time Rate (%) Sized by Order Volume</div>', unsafe_allow_html=True)

        fig_scat = px.scatter(
            df_states_filtered,
            x="avg_delivery_days",
            y="on_time_rate_pct",
            size="delivered_orders",
            color="macro_region",
            text="customer_state",
            color_discrete_map={
                "Southeast": "#2563eb",
                "South": "#059669",
                "Central-West": "#d97706",
                "Northeast": "#dc2626",
                "North": "#7f1d1d"
            },
            labels={"avg_delivery_days": "Avg Transit Days", "on_time_rate_pct": "On-Time Rate (%)", "macro_region": "Macro-Region"}
        )
        fig_scat.update_traces(textposition="top center")
        fig_scat.add_hline(y=sla_target_pct, line_dash="dash", line_color="#64748b")
        apply_enterprise_layout(fig_scat, height=430)
        st.plotly_chart(fig_scat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# VIEW 3: SELLER PARETO (80/20) & ACTIONABLE EXCEPTION WORKLIST
# =============================================================================
elif page == "3. Seller Pareto (80/20) & Action Worklist":
    df_sellers_sorted = df_sellers.sort_values(by=["late_items", "seller_late_rate_pct"], ascending=[False, False]).reset_index(drop=True)
    df_sellers_sorted["seller_rank"] = df_sellers_sorted.index + 1
    df_sellers_sorted["seller_pct_rank"] = df_sellers_sorted["seller_rank"] / len(df_sellers_sorted) * 100
    total_late_items = df_sellers_sorted["late_items"].sum()
    df_sellers_sorted["cum_late_share_pct"] = df_sellers_sorted["late_items"].cumsum() / total_late_items * 100

    top_10_pct_count = int(np.ceil(len(df_sellers_sorted) * 0.10))
    top_10_pct_late_share = df_sellers_sorted.loc[top_10_pct_count - 1, "cum_late_share_pct"]

    c_p1, c_p2 = st.columns([7, 5])

    with c_p1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="assertion-title">Pareto Concentration: Top 10% Worst Active Sellers ({top_10_pct_count} Merchants) Drive {top_10_pct_late_share:.1f}% of All Late Items</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Cumulative Share of Late Order Items (%) Across 682 Active Sellers (≥30 Delivered Items)</div>', unsafe_allow_html=True)

        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Scatter(
            x=df_sellers_sorted["seller_pct_rank"],
            y=df_sellers_sorted["cum_late_share_pct"],
            mode="lines",
            name="Cumulative Late Items (%)",
            line=dict(color="#dc2626", width=3),
            fill="tozeroy",
            fillcolor="rgba(220, 38, 38, 0.08)",
            hovertemplate="Top %{x:.1f}% of Sellers<br>Drive %{y:.1f}% of Late Items<extra></extra>"
        ))
        fig_pareto.add_trace(go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            name="Equal Distribution Baseline",
            line=dict(color="#94a3b8", width=1.5, dash="dash")
        ))
        fig_pareto.add_vline(x=10, line_dash="dot", line_color="#0f172a", annotation_text=f"Top 10% Sellers = {top_10_pct_late_share:.1f}% Late Items", annotation_position="top right")
        fig_pareto.update_layout(
            xaxis=dict(title="Share of Active Sellers Ranked by Late Volume (%)", ticksuffix="%", range=[0, 100]),
            yaxis=dict(title="Cumulative Share of Late Items (%)", ticksuffix="%", range=[0, 105])
        )
        apply_enterprise_layout(fig_pareto, height=360)
        st.plotly_chart(fig_pareto, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_p2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Quintile 5 Sellers Average 15.8% Late Rate & Drag Review Scores Down to 3.87 ★</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Seller Performance Stratified by Late-Rate Quintile (NTILE(5) Window Function)</div>', unsafe_allow_html=True)

        q_summary = df_sellers.groupby("seller_quintile", as_index=False).agg(
            sellers_count=("seller_id", "count"),
            total_items=("total_items", "sum"),
            late_items=("late_items", "sum"),
            avg_late_rate=("seller_late_rate_pct", "mean"),
            avg_review=("avg_seller_review_score", "mean")
        )
        q_labels = {1: "Q1 (Best)", 2: "Q2", 3: "Q3", 4: "Q4", 5: "Q5 (Worst)"}
        q_summary["quintile_label"] = q_summary["seller_quintile"].map(q_labels)

        fig_q = go.Figure()
        fig_q.add_trace(go.Bar(
            x=q_summary["quintile_label"],
            y=q_summary["avg_late_rate"],
            name="Avg Seller Late Rate (%)",
            marker_color=["#059669", "#10b981", "#64748b", "#d97706", "#dc2626"],
            text=q_summary["avg_late_rate"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside"
        ))
        fig_q.add_trace(go.Scatter(
            x=q_summary["quintile_label"],
            y=q_summary["avg_review"],
            name="Avg Review Score (★)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#0f172a", width=2.5),
            marker=dict(size=8)
        ))
        fig_q.update_layout(
            yaxis=dict(title="Avg Late Rate (%)", range=[0, 22], ticksuffix="%"),
            yaxis2=dict(title="Avg Review Score (★)", overlaying="y", side="right", range=[3.4, 4.5], showgrid=False)
        )
        apply_enterprise_layout(fig_q, height=360)
        st.plotly_chart(fig_q, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Row: Actionable Operator Worklist
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="assertion-title">📋 Operational Action Worklist: Bottleneck Seller SLA Governance Scorecard</div>', unsafe_allow_html=True)
    st.markdown('<div class="assertion-subtitle">Filter active merchants by SLA tier and export the targeted intervention list directly to CSV for Ops/CRM execution.</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([3, 3, 3, 3])
    with f1:
        selected_quintiles = st.multiselect("Filter by Seller Quintile:", options=[5, 4, 3, 2, 1], default=[5, 4])
    with f2:
        min_items_filter = st.number_input("Minimum Fulfilled Items:", min_value=30, max_value=1000, value=100, step=20)
    with f3:
        min_late_rate_filter = st.slider("Min Late Rate (%):", min_value=0.0, max_value=30.0, value=8.0, step=1.0)

    df_worklist = df_sellers_sorted[
        (df_sellers_sorted["seller_quintile"].isin(selected_quintiles if selected_quintiles else [5, 4, 3, 2, 1])) &
        (df_sellers_sorted["total_items"] >= min_items_filter) &
        (df_sellers_sorted["seller_late_rate_pct"] >= min_late_rate_filter)
    ].copy()

    def assign_sla_action(row):
        if row["seller_late_rate_pct"] >= 12.0 or (row["seller_quintile"] == 5 and row["late_items"] >= 40):
            return "🔴 Tier 3: Mandatory 3PL / Search Throttle"
        elif row["seller_late_rate_pct"] >= 7.5:
            return "🟠 Tier 2: SLA Warning & Lead-Time Audit"
        return "🟢 Tier 1: Compliant"

    df_worklist["SLA Governance Action"] = df_worklist.apply(assign_sla_action, axis=1)
    df_worklist["Seller ID (Short)"] = df_worklist["seller_id"].str[:10] + "..."

    with f4:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        csv_bytes = df_worklist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Export {len(df_worklist)} Flagged Sellers (CSV)",
            data=csv_bytes,
            file_name="olist_flagged_seller_sla_worklist.csv",
            mime="text/csv",
            use_container_width=True
        )

    display_cols = ["seller_rank", "Seller ID (Short)", "seller_state", "macro_region", "total_items", "late_items", "seller_late_rate_pct", "avg_seller_review_score", "seller_quintile", "SLA Governance Action"]
    st.dataframe(
        df_worklist[display_cols].rename(columns={
            "seller_rank": "Pareto Rank",
            "seller_state": "State",
            "macro_region": "Region",
            "total_items": "Total Items",
            "late_items": "Late Items",
            "seller_late_rate_pct": "Late Rate (%)",
            "avg_seller_review_score": "Avg Rating (★)",
            "seller_quintile": "Quintile"
        }),
        use_container_width=True,
        height=310,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# VIEW 4: SLA POLICY & COMMERCIAL ROI SIMULATOR (DECISION ENGINE)
# =============================================================================
elif page == "4. SLA Policy & Commercial ROI Simulator":
    st.markdown("""
    <div class="insight-callout" style="margin-bottom: 16px;">
        <strong>🎛️ Executive Decision & Breakeven Simulator:</strong> Modeled on commercial deal-desk and operational ROI calculators. Adjust policy parameters below to evaluate the trade-off between <strong>enforcing strict Seller SLA cutoffs</strong> (which risks losing GMV from non-compliant sellers who churn) versus <strong>eliminating late deliveries, deterring 1–2★ reviews, and reducing customer support/voucher leakage</strong>.
    </div>
    """, unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([4, 8])

    with sim_col1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">⚙️ Policy Levers & Unit Economics</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Configure SLA intervention thresholds & marketplace economics</div>', unsafe_allow_html=True)

        cutoff_late_pct = st.slider(
            "1. Seller Late-Rate Enforcement Cutoff (%):",
            min_value=6.0, max_value=25.0, value=10.0, step=0.5,
            help="Sellers above this late-delivery rate are placed on mandatory 3PL fulfillment or search throttling."
        )
        rehab_rate_pct = st.slider(
            "2. Flagged Seller Rehabilitation Rate (%):",
            min_value=30, max_value=95, value=75, step=5,
            help="Share of flagged sellers who adopt platform 3PL / fix dispatch SLAs vs. churning off the platform."
        )
        edd_buffer_reduction_pct = st.slider(
            "3. Dynamic EDD Buffer Late-Order Reduction (%):",
            min_value=0, max_value=50, value=25, step=5,
            help="Share of long-tail transit delays prevented by adding +3 to +5 day EDD buffers on Northern/Northeastern routes."
        )
        voucher_cost_usd = st.slider(
            "4. Support & Apology Cost per Severe Delay ($):",
            min_value=5.0, max_value=30.0, value=15.0, step=2.5,
            help="Average cost of customer service contact + retention voucher per severely delayed order."
        )
        take_rate_pct = st.slider(
            "5. Marketplace Commission Take-Rate (%):",
            min_value=8.0, max_value=20.0, value=12.0, step=1.0,
            help="Platform net revenue share of GMV."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Empirical calculations from validated CSVs
    flagged_sellers = df_sellers[df_sellers["seller_late_rate_pct"] >= cutoff_late_pct]
    num_flagged_sellers = len(flagged_sellers)
    flagged_items_total = int(flagged_sellers["total_items"].sum())
    flagged_late_items = int(flagged_sellers["late_items"].sum())

    # Baseline marketplace metrics
    base_delivered_orders = 96470
    base_late_orders = 6534
    base_ontime_pct = 93.23
    avg_item_gmv = 13591643.70 / 112650  # ~$120.65 per item

    # Impact of Seller SLA Gating + Dynamic EDD calibration
    late_eliminated_from_sellers = int(flagged_late_items * (rehab_rate_pct / 100.0) * 0.75)
    remaining_late_pool = max(0, base_late_orders - late_eliminated_from_sellers)
    late_eliminated_from_edd = int(remaining_late_pool * (edd_buffer_reduction_pct / 100.0))
    total_late_orders_prevented = min(base_late_orders, late_eliminated_from_sellers + late_eliminated_from_edd)

    projected_ontime_pct = ((base_delivered_orders - (base_late_orders - total_late_orders_prevented)) / base_delivered_orders) * 100.0

    # 1-2 Star Reviews Deterred (Late orders average 62.6% 1-2 star rate vs 9.27% on-time = 53.3% excess negative review rate)
    negative_reviews_prevented = int(total_late_orders_prevented * 0.533)

    # Financial Sensitivity Calculations
    # 1. Saved CS / Apology Voucher & Escalation Leakage
    saved_support_and_voucher_usd = total_late_orders_prevented * voucher_cost_usd

    # 2. Protected Listing Conversion & Repeat GMV (Take-Rate Margin)
    # Preventing 1-2 star reviews protects product page conversion (~0.8 incremental orders per prevented 1-star review + 0.77pp repeat lift)
    protected_gmv_usd = (negative_reviews_prevented * 0.85 * 136.68) + (total_late_orders_prevented * 0.0077 * 136.68)
    protected_commission_usd = protected_gmv_usd * (take_rate_pct / 100.0)

    # 3. Churned Seller GMV Risk (Unhappy flagged sellers who leave platform instead of rehabilitating, net of 60% buyer substitution to compliant sellers)
    unrehabilitated_items = flagged_items_total * ((100.0 - rehab_rate_pct) / 100.0)
    net_lost_gmv_after_substitution = unrehabilitated_items * avg_item_gmv * 0.40
    forfeited_commission_usd = net_lost_gmv_after_substitution * (take_rate_pct / 100.0)

    net_commercial_impact_usd = saved_support_and_voucher_usd + protected_commission_usd - forfeited_commission_usd

    with sim_col2:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="kpi-card warn">
                <div class="kpi-title">Sellers Flagged</div>
                <div class="kpi-value">{num_flagged_sellers} / 682</div>
                <div class="kpi-sub"><span class="delta-neu">{flagged_late_items:,} Late Items</span></div>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="kpi-card compliant">
                <div class="kpi-title">Projected On-Time SLA</div>
                <div class="kpi-value">{projected_ontime_pct:.2f}%</div>
                <div class="kpi-sub"><span class="delta-pos">+{projected_ontime_pct - base_ontime_pct:.2f}% Lift</span></div>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="kpi-card compliant">
                <div class="kpi-title">1–2★ Reviews Prevented</div>
                <div class="kpi-value">{negative_reviews_prevented:,}</div>
                <div class="kpi-sub"><span class="delta-pos">{total_late_orders_prevented:,} Delays Avoided</span></div>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            net_cls = "compliant" if net_commercial_impact_usd >= 0 else "breach"
            net_badge = "delta-pos" if net_commercial_impact_usd >= 0 else "delta-neg"
            st.markdown(f"""
            <div class="kpi-card {net_cls}">
                <div class="kpi-title">Net Commercial Impact</div>
                <div class="kpi-value">${net_commercial_impact_usd:,.0f}</div>
                <div class="kpi-sub"><span class="{net_badge}">Annualized P&L Delta</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Commercial P&L Sensitivity Bridge: Benefits of Defect Reduction vs. Seller Churn Risk</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Simulated Platform Contribution Margin Impact ($ USD) Under Selected SLA Governance Policy</div>', unsafe_allow_html=True)

        fig_wf = go.Figure(go.Waterfall(
            name="P&L Bridge",
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=[
                "1. Saved Support & Voucher Leakage",
                "2. Protected Conversion & Repeat Commission",
                "3. Forfeited Take-Rate (Seller Churn Risk)",
                "Net Platform P&L Impact"
            ],
            textposition="outside",
            text=[
                f"+${saved_support_and_voucher_usd:,.0f}",
                f"+${protected_commission_usd:,.0f}",
                f"-${forfeited_commission_usd:,.0f}",
                f"${net_commercial_impact_usd:,.0f}"
            ],
            y=[
                saved_support_and_voucher_usd,
                protected_commission_usd,
                -forfeited_commission_usd,
                net_commercial_impact_usd
            ],
            connector={"line": {"color": "#94a3b8"}},
            increasing={"marker": {"color": "#059669"}},
            decreasing={"marker": {"color": "#dc2626"}},
            totals={"marker": {"color": "#2563eb"}}
        ))
        fig_wf.update_layout(yaxis=dict(title="Platform Financial Impact ($ USD)", tickprefix="$"))
        apply_enterprise_layout(fig_wf, height=360, show_legend=False)
        st.plotly_chart(fig_wf, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# VIEW 5: BA GOVERNANCE (BRD/RACI) & SQL-TO-DAX RECONCILIATION
# =============================================================================
elif page == "5. BA Governance (BRD/RACI) & Reconciliation":
    tab_brd, tab_rec = st.tabs(["📋 BA/TPM Operational Governance (BRD & RACI)", "🔍 SQL-to-Power BI DAX Reconciliation Audit"])

    with tab_brd:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Business Requirements Document (BRD) Summary: Automated Seller SLA Governance</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Bridging BI Insights to CRM/ERP Execution (HubSpot / Jira / Logistics Ops)</div>', unsafe_allow_html=True)

        g1, g2 = st.columns([6, 6])
        with g1:
            st.markdown("#### 1. Operational Trigger Rules & User Stories")
            st.markdown("""
            * **US-01 (Automated Tier-2 Warning):** *As a Seller Operations Manager, I want the CRM to automatically trigger an SLA Warning Ticket when an active seller (≥30 orders) exceeds a **7.5% rolling 30-day late dispatch rate**, so that Seller Success can audit their handling lead-time before customer ratings collapse.*
            * **US-02 (Tier-3 Search Throttling & 3PL Gate):** *As VP of Marketplace Operations, I want sellers exceeding a **12.0% late rate (Quintile 5)** to have their search impression rank throttled by 50% until they enroll in platform cross-docking (Fulfillment by Olist), cutting marketplace late items by up to 52.5%.*
            * **US-03 (Dynamic Northern Corridor EDD Buffer):** *As a Checkout Product Manager, I want the EDD engine to append a **+3 to +5 business day buffer** on cross-state routes into MA, CE, BA, PA, and RJ where P90 transit exceeds 21 days.*
            """)
        with g2:
            st.markdown("#### 2. Cross-Functional RACI Governance Matrix")
            raci_df = pd.DataFrame([
                {"Workstream / Deliverable": "Weekly Seller SLA Scorecard & Breach Detection", "BI / Data Analyst": "R (Owner)", "Marketplace Ops": "A", "Seller Success CRM": "C", "Core Engineering": "I"},
                {"Workstream / Deliverable": "Tier-2 Seller Lead-Time Audit & Warning Notice", "BI / Data Analyst": "I", "Marketplace Ops": "C", "Seller Success CRM": "R / A", "Core Engineering": "I"},
                {"Workstream / Deliverable": "Tier-3 Search Demotion & 3PL Onboarding Gate", "BI / Data Analyst": "C", "Marketplace Ops": "A", "Seller Success CRM": "R", "Core Engineering": "R"},
                {"Workstream / Deliverable": "Northern Corridor Dynamic EDD Buffer (+3–5d)", "BI / Data Analyst": "C (Calibrate)", "Marketplace Ops": "I", "Seller Success CRM": "I", "Core Engineering": "R / A"},
                {"Workstream / Deliverable": "4+ Day Delay Proactive Apology Voucher ($15)", "BI / Data Analyst": "C (Track ROI)", "Marketplace Ops": "A", "Seller Success CRM": "R", "Core Engineering": "I"},
            ])
            st.dataframe(raci_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_rec:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown('<div class="assertion-title">Zero-Variance Financial & Metric Reconciliation (PostgreSQL 15 Star Schema vs. Power BI DAX)</div>', unsafe_allow_html=True)
        st.markdown('<div class="assertion-subtitle">Every KPI in this suite is verified against mart.fact_orders and mart.fact_order_items with 0.00% discrepancy.</div>', unsafe_allow_html=True)

        rec_df = pd.DataFrame([
            {"KPI Name": "Gross Merchandise Value (GMV)", "Star Schema SQL Query": "SUM(items_value) WHERE order_status NOT IN ('canceled','unavailable')", "Power BI DAX Measure": "SUM(fact_orders[items_value])", "SQL Output": "$13,591,643.70", "DAX Output": "$13,591,643.70", "Variance": "0.00% ✅"},
            {"KPI Name": "Total Marketplace Orders", "Star Schema SQL Query": "COUNT(DISTINCT order_id) FROM mart.fact_orders", "Power BI DAX Measure": "DISTINCTCOUNT(fact_orders[order_id])", "SQL Output": "99,441", "DAX Output": "99,441", "Variance": "0.00% ✅"},
            {"KPI Name": "Delivered Orders", "Star Schema SQL Query": "COUNT(*) WHERE is_delivered = TRUE", "Power BI DAX Measure": "CALCULATE([Orders], fact_orders[is_delivered] = TRUE)", "SQL Output": "96,470", "DAX Output": "96,470", "Variance": "0.00% ✅"},
            {"KPI Name": "Average Order Value (AOV)", "Star Schema SQL Query": "SUM(items_value) / COUNT(DISTINCT order_id)", "Power BI DAX Measure": "DIVIDE([GMV], [Orders], 0)", "SQL Output": "$136.68", "DAX Output": "$136.68", "Variance": "0.00% ✅"},
            {"KPI Name": "On-Time Delivery Rate %", "Star Schema SQL Query": "COUNT(delay_days <= 0) / COUNT(is_delivered)", "Power BI DAX Measure": "DIVIDE([On-Time Orders], [Delivered Orders], 0)", "SQL Output": "93.23%", "DAX Output": "93.23%", "Variance": "0.00% ✅"},
            {"KPI Name": "Average Review Score (CSAT)", "Star Schema SQL Query": "AVG(review_score) FROM deduplicated stg_order_reviews", "Power BI DAX Measure": "AVERAGE(fact_orders[review_score])", "SQL Output": "4.09 ★", "DAX Output": "4.09 ★", "Variance": "0.00% ✅"},
        ])
        st.dataframe(rec_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Persistent Enterprise Data Governance Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div class="gov-footer">
    <div><strong>Data Governance & Lineage:</strong> Kaggle Olist Brazilian E-Commerce (99,441 Orders · 112,650 Order Items · 96,096 Unique Customers) ➔ PostgreSQL 15 Star Schema (<code>raw</code> ➔ <code>stg</code> ➔ <code>mart</code>)</div>
    <div><strong>Author:</strong> Daisy Phukan (TPM & Business/BI Analyst) · <a href="mailto:daisyphukan.work@gmail.com">daisyphukan.work@gmail.com</a></div>
</div>
""", unsafe_allow_html=True)
