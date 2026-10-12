import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Olist E-Commerce Analytics | Daisy Phukan",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #1f77b4;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Ingestion (From Validated Result Marts)
# -----------------------------------------------------------------------------
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "docs", "results")

@st.cache_data
def load_data():
    df_kpi = pd.read_csv(os.path.join(RESULTS_DIR, "01_kpi_overview.csv"))
    df_delivery = pd.read_csv(os.path.join(RESULTS_DIR, "02_delivery_performance.csv"))
    df_reviews = pd.read_csv(os.path.join(RESULTS_DIR, "03_delay_vs_review.csv"))
    df_states = pd.read_csv(os.path.join(RESULTS_DIR, "04_state_delay_hotspots.csv"))
    df_sellers = pd.read_csv(os.path.join(RESULTS_DIR, "05_seller_scorecard.csv"))
    df_repeat = pd.read_csv(os.path.join(RESULTS_DIR, "07_repeat_purchase_cohorts.csv"))
    return df_kpi, df_delivery, df_reviews, df_states, df_sellers, df_repeat

df_kpi, df_delivery, df_reviews, df_states, df_sellers, df_repeat = load_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Context
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/PostgreSQL-Dark.svg", width=60)
    st.title("Navigation")
    
    page = st.radio(
        "Select Analytics View:",
        [
            "1. Executive KPI Overview",
            "2. Delivery & Customer Satisfaction",
            "3. Seller Bottlenecks & Pareto Curve",
            "4. Business Recommendations Memo"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 👤 Candidate Profile")
    st.markdown("**Daisy Phukan**  \n*Technical Project Manager → Business / Data Analyst*")
    st.markdown("📍 Bengaluru, India")
    st.markdown("[GitHub Profile](https://github.com/Daizy-Mgmt) | [PL-300 Candidate](https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/)")
    
    st.markdown("---")
    st.markdown("### 🛠️ Architecture Stack")
    st.caption("• **Data Engine:** PostgreSQL 15 (Docker)\n• **Modeling:** Star Schema Dimensional Marts\n• **Logic:** Advanced SQL CTEs, Window Functions, DAX\n• **Front-End:** Streamlit & Plotly")

# -----------------------------------------------------------------------------
# Page 1: Executive KPI Overview
# -----------------------------------------------------------------------------
if page == "1. Executive KPI Overview":
    st.markdown('<div class="main-title">Executive Performance & Revenue Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">High-level marketplace health, GMV trajectory, and volume growth (2017 – 2018).</div>', unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total GMV", "$13.59M", "+104% (Nov Peak)")
    with col2:
        st.metric("Total Orders", "99,441", "96.5k Delivered")
    with col3:
        st.metric("Average Order Value (AOV)", "$136.68", "$137.71 2018 Run Rate")
    with col4:
        st.metric("On-Time Rate %", "93.23%", "-4.2% Holiday Dip")
    with col5:
        st.metric("Average Review Score", "4.09 / 5.0", "14.9% Negative Rate")
    
    st.markdown("---")
    
    # Visual 1: Monthly GMV and Orders Trend
    c1, c2 = st.columns([7, 5])
    
    with c1:
        st.subheader("Monthly GMV & Order Volume Trajectory")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=df_kpi['year_month'],
            y=df_kpi['gmv'],
            name="GMV ($)",
            marker_color='#2563eb',
            opacity=0.85
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_kpi['year_month'],
            y=df_kpi['orders_count'],
            name="Orders Count",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=7)
        ))
        fig_trend.update_layout(
            yaxis=dict(title="GMV ($)", showgrid=True),
            yaxis2=dict(title="Orders Placed", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1, x=0),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.caption("🔍 **Key Finding:** GMV surged exponentially throughout 2017, peaking during Black Friday (Nov 2017: $986k GMV, 7.3k orders) before stabilizing at ~$850k–$900k monthly run rate in 2018.")

    with c2:
        st.subheader("Month-over-Month GMV Growth Rate (%)")
        df_mom = df_kpi.dropna(subset=['gmv_mom_pct'])
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in df_mom['gmv_mom_pct']]
        
        fig_mom = px.bar(
            df_mom,
            x='year_month',
            y='gmv_mom_pct',
            labels={'year_month': 'Month', 'gmv_mom_pct': 'MoM Growth (%)'},
            text_auto='.1f'
        )
        fig_mom.update_traces(marker_color=colors)
        fig_mom.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=400
        )
        st.plotly_chart(fig_mom, use_container_width=True)
        st.caption("📈 **Growth Cycle:** Fast early-stage scaling (+104% in Feb 2017) followed by plateau and seasonality peaks.")

# -----------------------------------------------------------------------------
# Page 2: Delivery & Customer Satisfaction
# -----------------------------------------------------------------------------
elif page == "2. Delivery & Customer Satisfaction":
    st.markdown('<div class="main-title">Delivery Performance & Customer Satisfaction Impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Empirical evidence showing how logistics delays directly erode customer review ratings and retention.</div>', unsafe_allow_html=True)
    
    # Headline Visual: Review Score by Delay Bucket
    c1, c2 = st.columns([7, 5])
    
    with c1:
        st.subheader("⭐ The Satisfaction Cliff: Review Score vs. Delay Bucket")
        fig_delay = go.Figure()
        
        fig_delay.add_trace(go.Bar(
            x=df_reviews['delay_bucket'],
            y=df_reviews['avg_review_score'],
            name="Avg Review Score (1-5)",
            marker_color=['#10b981', '#f59e0b', '#f97316', '#ef4444', '#991b1b'],
            text=df_reviews['avg_review_score'].apply(lambda x: f"{x:.2f} ★"),
            textposition='outside'
        ))
        
        fig_delay.add_trace(go.Scatter(
            x=df_reviews['delay_bucket'],
            y=df_reviews['low_score_share_pct'],
            name="Negative Reviews % (1-2 Stars)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color='#dc2626', width=3, dash='dot'),
            marker=dict(size=8)
        ))
        
        fig_delay.update_layout(
            yaxis=dict(title="Average Review Score", range=[0, 5.2]),
            yaxis2=dict(title="Share of 1-2 Star Reviews (%)", overlaying="y", side="right", range=[0, 100]),
            legend=dict(orientation="h", y=1.1, x=0),
            margin=dict(l=20, r=20, t=30, b=20),
            height=430
        )
        st.plotly_chart(fig_delay, use_container_width=True)
        st.error("🚨 **Executive Insight:** Customers are tolerant of minor 1-3 day delays (score drops from 4.29 to 3.29). However, past 8 days of delay, customer satisfaction collapses entirely: **79.3% of orders receive 1-2 star ratings**, averaging a catastrophic **1.70 / 5.0**.")

    with c2:
        st.subheader("🔄 Impact on Repeat Purchase Behavior")
        fig_repeat = px.bar(
            df_repeat,
            x='first_order_delay_bucket',
            y='repeat_purchase_rate_pct',
            color='repeat_purchase_rate_pct',
            color_continuous_scale='Blues',
            text_auto='.2f',
            labels={'first_order_delay_bucket': 'First Order Experience', 'repeat_purchase_rate_pct': 'Repeat Purchase Rate (%)'}
        )
        fig_repeat.update_layout(height=430, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_repeat, use_container_width=True)
        st.caption("📉 **Churn Multiplier:** First impressions dictate customer lifetime value. Delays on a customer's initial order cut repeat purchase propensity by **~25% to 44%**.")

    st.markdown("---")
    
    # Regional Delivery Breakdown
    st.subheader("🗺️ Regional Disparities: On-Time Rate & Transit Days by Brazilian State")
    c3, c4 = st.columns([7, 5])
    
    with c3:
        fig_states = px.bar(
            df_states.sort_values(by="on_time_rate_pct", ascending=True),
            x='on_time_rate_pct',
            y='customer_state',
            orientation='h',
            color='on_time_rate_pct',
            color_continuous_scale='RdYlGn',
            labels={'on_time_rate_pct': 'On-Time Rate (%)', 'customer_state': 'Destination State'},
            text_auto='.1f'
        )
        fig_states.update_layout(height=480, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_states, use_container_width=True)
    
    with c4:
        st.markdown("""
        ### 📍 Geographic Takeaways:
        * **Southern / Southeast Hubs (SP, MG, PR, SC):**
          * Benefit from dense carrier infrastructure.
          * Average transit time: **8 – 11 days**.
          * On-Time Rate: **>92 – 95%**.
        
        * **Remote Northern / Northeastern States (MA, CE, BA, PA):**
          * Suffer severe transit bottlenecks.
          * Average transit time: **19 – 24 days**.
          * On-Time Rate plunges as low as **82.6%** in Maranhão (MA).
          * Recommendation: Implement realistic dynamic estimated delivery dates (EDDs) for regional carriers.
        """)

# -----------------------------------------------------------------------------
# Page 3: Seller Bottlenecks & Pareto Curve
# -----------------------------------------------------------------------------
elif page == "3. Seller Bottlenecks & Pareto Curve":
    st.markdown('<div class="main-title">Seller Lateness Concentration & Pareto Bottlenecks</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Quantifying whether delivery breaches are systemic or driven by chronic underperforming sellers.</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([7, 5])
    
    with c1:
        st.subheader("📉 The 80/20 Rule: Cumulative Share of Late Delivery Items")
        # Prepare Pareto curve
        df_sellers_sorted = df_sellers.sort_values(by="late_items", ascending=False).reset_index(drop=True)
        df_sellers_sorted['seller_rank_pct'] = (df_sellers_sorted.index + 1) / len(df_sellers_sorted) * 100
        
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Scatter(
            x=df_sellers_sorted['seller_rank_pct'],
            y=df_sellers_sorted['cumulative_late_pct'],
            mode='lines',
            name="Cumulative Late Items %",
            line=dict(color='#ef4444', width=3)
        ))
        # 80/20 reference lines
        fig_pareto.add_shape(type='line', x0=10, y0=0, x1=10, y1=52.5, line=dict(color='gray', dash='dash'))
        fig_pareto.add_shape(type='line', x0=0, y0=52.5, x1=10, y1=52.5, line=dict(color='gray', dash='dash'))
        
        fig_pareto.update_layout(
            xaxis=dict(title="% of Total Active Sellers (Ranked Worst to Best)", range=[0, 100]),
            yaxis=dict(title="% of Total Late Order Items", range=[0, 105]),
            height=430,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
        st.warning("🎯 **Pareto Concentration Finding:** Just **10% of active sellers account for over 52% of all late delivered items** across the entire marketplace! Operational intervention on a targeted cohort of ~68 sellers solves more than half of late delivery issues.")

    with c2:
        st.subheader("Seller Performance Quintiles (NTILE)")
        quintile_agg = df_sellers.groupby("seller_quintile").agg(
            avg_late_rate=('seller_late_rate_pct', 'mean'),
            avg_score=('avg_seller_review_score', 'mean'),
            seller_count=('seller_id', 'count')
        ).reset_index()
        
        fig_q = px.bar(
            quintile_agg,
            x='seller_quintile',
            y='avg_late_rate',
            color='avg_score',
            color_continuous_scale='Viridis',
            labels={'seller_quintile': 'Seller Quintile (1=Best, 5=Worst)', 'avg_late_rate': 'Avg Lateness %'},
            text_auto='.1f'
        )
        fig_q.update_layout(height=430, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_q, use_container_width=True)
        st.caption("Quintile 5 sellers exhibit an average lateness rate of **24.8%**, pulling down customer trust.")

    st.markdown("---")
    st.subheader("🔍 Chronic Bottleneck Seller Scorecard (Top 20 Worst Offenders)")
    st.dataframe(
        df_sellers[['seller_id', 'seller_state', 'total_items', 'late_items', 'seller_late_rate_pct', 'avg_seller_review_score', 'cumulative_late_pct']].head(20),
        use_container_width=True,
        column_config={
            "seller_id": "Seller ID",
            "seller_state": "State",
            "total_items": st.column_config.NumberColumn("Total Items Sold", format="%d"),
            "late_items": st.column_config.NumberColumn("Late Items", format="%d"),
            "seller_late_rate_pct": st.column_config.ProgressColumn("Lateness Rate %", format="%.1f%%", min_value=0, max_value=50),
            "avg_seller_review_score": st.column_config.NumberColumn("Avg Review Rating", format="%.2f ★"),
            "cumulative_late_pct": st.column_config.NumberColumn("Cumulative Late %", format="%.1f%%")
        }
    )

# -----------------------------------------------------------------------------
# Page 4: Business Recommendations Memo
# -----------------------------------------------------------------------------
elif page == "4. Business Recommendations Memo":
    st.markdown('<div class="main-title">Executive Strategy & Recommendations Memo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Actionable operational playbook derived directly from empirical SQL findings.</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📌 MEMORANDUM
    **TO:** Marketplace Operations & Logistics Leadership  
    **FROM:** Daisy Phukan, Technical Project Manager / Business Analytics  
    **SUBJECT:** Olist Delivery SLA Optimization & Customer Retention Strategy  
    **DATA SOURCE:** 99,441 Marketplace Orders (2016–2018 Brazilian E-Commerce Dataset)  

    ---

    ### 🎯 Key Findings Summary
    1. **The 8-Day Satisfaction Threshold:** Minor delays (1–3 days) cause a mild score decline (4.29 → 3.29 ★). However, breaches exceeding 8 days trigger complete satisfaction collapse: **79.3% 1–2 star negative reviews** with average rating falling to **1.70 ★**.
    2. **High Seller Concentration (Pareto):** 52.5% of all late delivery items originate from only **10% of active sellers** (approx. 68 sellers). 
    3. **First-Purchase Churn:** Customers experiencing a delivery delay on their very first transaction show a **~44% drop in repeat purchase propensity** compared to on-time buyers.
    4. **Severe Regional Disparities:** Delivery transit times to Northern/Northeastern states (MA, CE, PA, BA) average 19–24 days with late rates exceeding 15–17%, vs 8–11 days in São Paulo.

    ---

    ### 🚀 4 Actionable Business Recommendations

    #### 1. Implement Seller Fulfillment SLA Gating & Penalties
    * **Action:** Institute a 3-strike fulfillment SLA policy for Quintile 5 sellers (>15% late rate).
    * **Mechanism:** Require sellers with chronic delays to switch to Olist-managed fulfillment centers (FBA-style cross-docking) or throttle their search algorithm exposure until late dispatch rates fall below 5%.
    * **Expected Impact:** Eliminating the top 10% seller bottlenecks resolves **>50% of late delivery occurrences**.

    #### 2. Dynamic Estimated Delivery Date (EDD) Calibration for Remote States
    * **Action:** Adjust estimated delivery date algorithms dynamically for Northern/Northeastern zones (MA, CE, BA).
    * **Mechanism:** Add a dynamic +3 to +5 day buffer to the promised delivery date shown at checkout for remote postal codes.
    * **Expected Impact:** Under-promising and over-delivering shifts orders from the "Late" bucket to the "On Time / Early" bucket, recovering customer review scores without requiring immediate physical transit speedups.

    #### 3. Proactive Post-Breach Retention Vouchers
    * **Action:** Automatically trigger an apology notification and a 15% discount voucher when an order crosses 4 days past its estimated delivery date.
    * **Expected Impact:** Re-engages first-time buyers whose lifetime value is otherwise lost, counteracting the 44% repeat purchase cliff.

    #### 4. Southeastern Cross-Docking Hub Consolidations
    * **Action:** Over 70% of sellers reside in São Paulo (SP). Partner with regional logistics aggregators to batch shipments destined for northern transit corridors.
    * **Expected Impact:** Reduces the 23.7-day average transit time to Pará (PA) and Maranhão (MA) by 3–4 business days.
    """)

# Footer
st.markdown("---")
st.caption("📊 Built by Daisy Phukan | Verified with PostgreSQL 15 Star Schema Marts & Production DAX Measures.")
