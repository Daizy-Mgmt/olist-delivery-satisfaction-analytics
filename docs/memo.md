# Executive Memorandum: Delivery Performance, Satisfaction & Operations Strategy

**TO:** Vice President of Marketplace Operations & Logistics  
**FROM:** Daisy Phukan, Technical Project Manager / Business Analytics  
**DATE:** October 2026  
**SUBJECT:** Operational SLA Optimization and Customer Retention Playbook  
**DATASET AUDITED:** 99,441 Brazilian Marketplace Orders (Olist E-Commerce Platform)  

---

## 1. Business Context & Core Problem

E-commerce marketplaces thrive on buyer retention and organic repeat GMV. While Olist expanded rapidly from $120.1k GMV in January 2017 to peak at $986.0k in November 2017, its lifetime customer repeat rate remains low at **3.12%**.

This audit addresses the core business question:  
*How severely do delivery delays damage customer satisfaction and lifetime retention, and how concentrated are the operational bottlenecks driving them?*

---

## 2. Key Empirical Findings (SQL Verified)

1. **The 8-Day Satisfaction Cliff:**  
   On-time deliveries maintain an average customer review rating of **4.29 / 5.0** (with only 9.3% negative 1–2 star reviews). Minor delays of 1–3 days lower satisfaction to **3.29 ★** (32.1% negative). However, once an order exceeds **8 days past its estimated delivery date**, review ratings collapse to **1.70 ★**, with **79.3% of customers leaving 1- or 2-star reviews**.

2. **Extreme Bottleneck Concentration (Pareto Principle):**  
   Late deliveries are not distributed evenly across the marketplace. **10% of active sellers account for 52.5% of all late delivery items**. Sellers in Quintile 5 (the worst 20%) suffer an average lateness rate of **24.8%**, compared to only 0.8% in Quintile 1.

3. **First-Purchase Delivery Delays & Cohort Base-Rate Nuance:**  
   Customers whose very first order arrived on time demonstrated a **3.40%** repeat purchase rate, whereas customers delayed 1–7 days dropped to **2.63%–2.64%** (a **22.6% relative reduction**). Crucially, because Olist's overall repeat purchase baseline is structurally **3.12%** (`96.88%` one-time buyers)—and `Not delivered` orders show a **4.68%** re-order rate driven by immediate replacement orders after cancellation—the primary commercial damage of severe delays is not repeat LTV loss alone, but the **79.3% 1–2★ review spike** that suppresses product conversion and inflates customer support costs.

4. **Regional Transit Disparities:**  
   Orders shipped to Southeastern/Southern hubs (São Paulo, Paraná, Minas Gerais) average 8.7–11.9 transit days with >95.4% on-time performance. Conversely, remote Northern and Northeastern states (Maranhão, Ceará, Bahia, Pará) average **19.3–23.7 transit days**, with Maranhão (MA) dropping to an on-time rate of only **82.57%**.

---

## 3. Four Strategic Recommendations

### Recommendation 1: Tiered Seller SLA Governance & Algorithmic Throttling
* **Action:** Institute a 3-strike SLA fulfillment policy for Quintile 5 sellers (>15% late dispatch rate).
* **Execution:** Require chronic bottleneck sellers to adopt platform-managed fulfillment (cross-docking) or dynamically deprioritize their product listings in marketplace search rankings until their 30-day late dispatch rate falls below 5%.
* **Projected Impact:** Intervening on the top 68 bottleneck sellers directly addresses **over 50% of marketplace delivery failures**.

### Recommendation 2: Dynamic Delivery Date Calibration for Remote Corridors
* **Action:** Calibrate checkout Estimated Delivery Dates (EDDs) dynamically by destination state and carrier reliability.
* **Execution:** Increase the promised delivery window shown to buyers in Northern/Northeastern zones (MA, CE, PA) by +3 to +5 business days.
* **Projected Impact:** Shifts thousands of orders from the damaging "Late" bucket into the "On Time" bucket, immediately elevating buyer review sentiment without requiring instant physical transit speedups.

### Recommendation 3: Automated Proactive Retention Recovery Vouchers
* **Action:** Deploy an automated retention trigger when an in-transit parcel breaches estimated delivery by 4+ business days.
* **Execution:** Send an automated status update with an apology and a 15% discount voucher on their next purchase before the buyer submits a negative review.
* **Projected Impact:** Mitigates the first-order churn cliff, protecting long-term customer lifetime value (LTV).

### Recommendation 4: Regional Carrier Diversification & Cross-Docking in SP
* **Action:** Establish regional logistics partnerships for heavy cross-state transit corridors originating from São Paulo (where >70% of sellers operate).
* **Projected Impact:** Reduces transit times to northern hubs by an estimated 3–4 calendar days.

---

## 4. Analytical Limitations

* **Correlation vs. Causation:** Review scores reflect the complete customer journey. Delays are strongly *associated* with low scores, but product quality defects or seller communication may contribute to dissatisfaction.
* **Missing Geolocation Micro-Data:** Geolocation zip prefixes represent centroid coordinates rather than exact delivery addresses.
* **Sample Window:** Analysis spans 2016 to 2018; modern macro-economic freight factors would require updated indexing.
