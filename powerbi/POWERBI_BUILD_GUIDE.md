# Power BI Dashboard Build Guide: Step-by-Step Instructions

This guide provides the complete blueprint for assembling the **3-Page Executive Power BI Report** in Power BI Desktop.

---

## 🎨 Theme & Canvas Settings
* **Canvas Size:** 16:9 (1280 x 720 px)
* **Background:** Light gray / Off-white (`#F8F9FA`)
* **Color Palette:**
  * Primary Accent: Deep Blue (`#1E3A8A` or `#2563EB`)
  * Positive / On-Time: Emerald Green (`#10B981`)
  * Neutral / Warning: Amber (`#F59E0B`)
  * Breach / Negative: Crimson Red (`#EF4444`)

---

## 📑 Page 1: Executive Overview (Marketplace Performance)

**Page Purpose:** Answer *“How healthy is marketplace revenue, order volume, and overall fulfillment reliability?”*

### 1. Header & Slicers
* **Title:** "Marketplace Executive Performance & Revenue Overview"
* **Top-Right Slicer:** Date Range Slider (from `dim_date[date_actual]`, default: `2017-01-01` to `2018-08-31`).

### 2. Top KPI Cards (5 Cards across the top)
1. **Total GMV:** `[GMV]` → Formatted as Currency (`$13.59M`)
2. **Total Orders:** `[Orders]` → Formatted as Whole Number (`99,441`)
3. **Average Order Value (AOV):** `[AOV]` → Formatted as Currency (`$136.68`)
4. **On-Time Delivery Rate:** `[On-Time %]` → Formatted as Percentage (`93.2%`)
5. **Avg Review Score:** `[Avg Review Score]` → Formatted as Decimal with star (`4.09 ★`)

### 3. Visual 1: Line and Clustered Column Chart (Main Visual)
* **Visual Type:** Line and Clustered Column Chart
* **X-Axis:** `dim_date[year_month]`
* **Column y-axis:** `[GMV]` (Bar color: Deep Blue)
* **Line y-axis:** `[Orders]` (Line color: Amber, Stroke width: 3)
* **Title:** "Monthly GMV Trajectory & Order Volume (Peak in Nov 2017)"

### 4. Visual 2: Clustered Bar Chart
* **Visual Type:** Clustered Bar Chart
* **Y-Axis:** `dim_date[year_month]`
* **X-Axis:** `[GMV MoM %]` (Color rule: Green if ≥ 0, Red if < 0)
* **Title:** "Month-over-Month GMV Growth Rate (%)"

---

## 📑 Page 2: Delivery Performance & Customer Satisfaction

**Page Purpose:** Answer *“What is the exact impact of delivery delays on customer sentiment and repeat purchase?”*

### 1. Visual 1: The Satisfaction Cliff (Headline Finding)
* **Visual Type:** Line and Clustered Column Chart
* **X-Axis:** `fact_orders[delay_bucket]` (Sort by delay order: *On time / early*, *1-3 days late*, *4-7 days late*, *8+ days late*, *Not delivered*)
* **Column y-axis:** `[Avg Review Score]` (Color: Gradient from Green for on-time to Red for 8+ days late)
* **Line y-axis:** `[Low Score %]` (Line color: Red with data points)
* **Title:** "The Satisfaction Cliff: Customer Rating Collapse Beyond 8 Days Delay"
* **Takeaway Textbox:** *"Deliveries on time achieve 4.29 ★. Beyond 8 days of delay, ratings collapse to 1.70 ★ with 79.3% negative reviews."*

### 2. Visual 2: Geographic Disparity Map / Horizontal Bar Chart
* **Visual Type:** Horizontal Bar Chart (Sorted Ascending)
* **Y-Axis:** `fact_orders[customer_state]`
* **X-Axis:** `[On-Time %]` (Filtered to states with ≥ 500 orders)
* **Data Colors:** Conditional Formatting based on `[On-Time %]` (Red for < 88%, Green for > 93%)
* **Title:** "On-Time Fulfillment Rate by Destination State (MA, CE, BA lagging)"

### 3. Visual 3: Repeat Buyer Cliff Cards
* **Visual Type:** 2 Multi-Row Cards
  * Card 1: Repeat Rate for On-Time First Order → **3.40%**
  * Card 2: Repeat Rate for Late First Order → **1.82%** (-44% relative drop)

---

## 📑 Page 3: Seller Bottlenecks & Pareto Scorecards

**Page Purpose:** Answer *“Are late orders caused by widespread carrier failure or concentrated underperforming sellers?”*

### 1. Visual 1: Pareto Cumulative Lateness Chart
* **Visual Type:** Line and Clustered Column Chart
* **X-Axis:** `dim_seller[seller_id]` (Sorted by late items descending)
* **Column y-axis:** `Late Items Count`
* **Line y-axis:** `Cumulative Late %` (running total percentage)
* **Callout Box:** *"🎯 Pareto Law Confirmed: Top 10% of active sellers drive >52% of all late delivery items."*

### 2. Visual 2: Seller Quintile Performance Matrix
* **Visual Type:** Clustered Column Chart
* **X-Axis:** `Seller Quintile` (1 to 5)
* **Values:** `Seller Lateness Rate %` and `Avg Review Score`

### 3. Visual 3: Searchable Chronic Bottleneck Seller Table
* **Columns:**
  1. `dim_seller[seller_id]`
  2. `dim_seller[seller_state]`
  3. `Total Items Sold`
  4. `Late Items Count`
  5. `Late Rate %` (Data bar formatted)
  6. `Avg Review Score`
* **Interactive Feature:** Slicer by `seller_state` and search by `seller_id`.

---

## 🖨️ Exporting for Portfolio & Recruiters
1. **Save File:** Save as `powerbi/olist_delivery_satisfaction.pbix`.
2. **Export PDF:** Click **File → Export → Export to PDF** → Save to `docs/dashboard.pdf`.
3. **Capture Screenshots:**
   * Screenshot Page 1 → `images/pbi_page1_executive_overview.png`
   * Screenshot Page 2 → `images/pbi_page2_delivery_satisfaction.png`
   * Screenshot Page 3 → `images/pbi_page3_seller_scorecard.png`
