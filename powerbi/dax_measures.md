# Power BI Star Schema Data Model & DAX Measure Suite

This document defines the dimensional data model, relationships, and the complete DAX calculation suite for the **Olist Delivery Performance & Customer Satisfaction Analytics** report.

All measures are housed in a dedicated `_Measures` table to separate business logic from physical schema columns.

---

## 1. Dimensional Model & Relationships (Star Schema)

In Power BI Desktop, import tables from the `mart` schema and establish the following **1-to-Many (`1:*`), Single Cross-Filter Direction** relationships:

| From Dimension (1) | Column | To Fact (*) | Column | Cardinality | Active |
|---|---|---|---|---|---|
| `mart.dim_date` | `date_actual` | `mart.fact_orders` | `purchase_ts` (Date) | 1 to Many | Yes |
| `mart.dim_customer` | `customer_unique_id` | `mart.fact_orders` | `customer_unique_id` | 1 to Many | Yes |
| `mart.dim_seller` | `seller_id` | `mart.fact_order_items` | `seller_id` | 1 to Many | Yes |
| `mart.dim_product` | `product_id` | `mart.fact_order_items` | `product_id` | 1 to Many | Yes |
| `mart.fact_orders` | `order_id` | `mart.fact_order_items` | `order_id` | 1 to Many | Yes |

### Key Modeling Settings:
1. **Mark as Date Table:** Right-click `mart.dim_date` → *Mark as date table* → select `date_actual`.
2. **Hide Key Columns:** Hide all foreign keys (`order_id`, `customer_unique_id`, `seller_id`, `product_id`) in the fact tables from Report View to force users to slice by dimension attributes.
3. **Format Currency & Percentages:** Set currency format (`$#,##0.00`) for financial measures and percentage format (`0.0%`) for ratios.

---

## 2. Dedicated `_Measures` Table Setup

In Power BI Desktop:
1. Go to the **Modeling** tab → click **New Table**.
2. Enter:
   ```dax
   _Measures = { BLANK() }
   ```
3. Create all measures below in this table. Hide the initial blank column once measures are added so the `_Measures` folder moves to the top of the Fields pane with a calculator icon.

---

## 3. Production DAX Measure Library

### [M01] Gross Merchandise Value (GMV)
* **Description:** Total product revenue across all valid non-canceled/unavailable orders. Excludes freight.
* **SQL Reconciliation:** Matches `SUM(items_value)` in `mart.fact_orders` exactly (**$13,591,643.70**).
```dax
GMV = 
SUM(fact_orders[items_value])
```

---

### [M02] Order Count
* **Description:** Distinct count of unique orders placed.
* **SQL Reconciliation:** Matches `COUNT(DISTINCT order_id)` in `mart.fact_orders` (**99,441**).
```dax
Orders = 
DISTINCTCOUNT(fact_orders[order_id])
```

---

### [M03] Average Order Value (AOV)
* **Description:** Average item revenue generated per order. Uses `DIVIDE()` to safely handle divide-by-zero errors.
* **SQL Reconciliation:** **$136.68** overall across all orders ($137.71 for 2017-2018 operational window).
```dax
AOV = 
DIVIDE(
    [GMV], 
    [Orders], 
    0
)
```

---

### [M04] Delivered Orders
* **Description:** Total count of orders successfully received by customers (`is_delivered = TRUE`).
* **SQL Reconciliation:** Matches `COUNT(*)` where `is_delivered = TRUE` (**96,470**).
```dax
Delivered Orders = 
CALCULATE(
    [Orders],
    fact_orders[is_delivered] = TRUE()
)
```

---

### [M05] On-Time Delivery %
* **Description:** Share of delivered orders that arrived on or before the estimated delivery date (`is_late = FALSE`).
* **SQL Reconciliation:** **93.23%** across all delivered orders (89,936 on-time / 96,470 delivered).
```dax
On-Time % = 
VAR OnTimeOrders = 
    CALCULATE(
        [Orders],
        fact_orders[is_delivered] = TRUE(),
        fact_orders[is_late] = FALSE()
    )
RETURN
    DIVIDE(
        OnTimeOrders, 
        [Delivered Orders], 
        0
    )
```

---

### [M06] Average Review Score
* **Description:** Mean customer review rating on a 1.0 to 5.0 scale from deduplicated order reviews.
* **SQL Reconciliation:** **4.09** overall (4.29 for on-time orders; 1.70 for 8+ days late orders).
```dax
Avg Review Score = 
AVERAGE(fact_orders[review_score])
```

---

### [M07] Low Score Rate % (1-2 Stars)
* **Description:** Proportion of orders resulting in dissatisfaction (1 or 2 stars).
* **SQL Reconciliation:** **14.92%** overall (9.27% for on-time orders; collapses to 79.29% for 8+ days late orders).
```dax
Low Score % = 
VAR DissatisfiedOrders = 
    CALCULATE(
        COUNTROWS(fact_orders),
        fact_orders[review_score] IN { 1, 2 }
    )
VAR TotalRatedOrders = 
    CALCULATE(
        COUNTROWS(fact_orders),
        NOT(ISBLANK(fact_orders[review_score]))
    )
RETURN
    DIVIDE(
        DissatisfiedOrders, 
        TotalRatedOrders, 
        0
    )
```

---

### [M08] Average Delay Days (Late Orders Only)
* **Description:** Average number of business/calendar days past the estimated delivery promise, calculated strictly for late orders.
* **SQL Reconciliation:** **11.8 days** average lateness for orders that breached SLA.
```dax
Avg Delay Days (Late Only) = 
CALCULATE(
    AVERAGE(fact_orders[delay_days]),
    fact_orders[is_late] = TRUE()
)
```

---

### [M09] GMV Month-over-Month Growth % (MoM)
* **Description:** Percentage change in GMV compared to the preceding calendar month using Power BI Time Intelligence.
* **SQL Reconciliation:** Matches monthly SQL `LAG()` calculations in `01_kpi_overview.sql`.
```dax
GMV MoM % = 
VAR CurrentGMV = [GMV]
VAR PreviousMonthGMV = 
    CALCULATE(
        [GMV],
        DATEADD(dim_date[date_actual], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentGMV - PreviousMonthGMV, 
        PreviousMonthGMV, 
        BLANK()
    )
```

---

### [M10] Customer Repeat Purchase %
* **Description:** Percentage of unique buyers who placed 2 or more lifetime orders.
* **SQL Reconciliation:** **3.12%** lifetime customer repeat rate (3,000 repeat buyers / 96,096 unique customers).
```dax
Repeat Customer % = 
VAR RepeatCustomers = 
    CALCULATE(
        DISTINCTCOUNT(fact_orders[customer_unique_id]),
        dim_customer[is_repeat_customer] = TRUE()
    )
VAR TotalCustomers = 
    DISTINCTCOUNT(fact_orders[customer_unique_id])
RETURN
    DIVIDE(
        RepeatCustomers, 
        TotalCustomers, 
        0
    )
```

---

## 4. Benchmark Reconciliation Table (SQL vs DAX)

| Metric | SQL Benchmark Query | DAX Formula | Reconciled Value | Status |
|---|---|---|---|---|
| **Total GMV** | `SELECT SUM(items_value) FROM mart.fact_orders;` | `[GMV]` | **$13,591,643.70** | ✅ Exact Match |
| **Total Orders** | `SELECT COUNT(DISTINCT order_id) FROM mart.fact_orders;` | `[Orders]` | **99,441** | ✅ Exact Match |
| **Delivered Orders** | `SELECT COUNT(*) FROM mart.fact_orders WHERE is_delivered = TRUE;` | `[Delivered Orders]` | **96,470** | ✅ Exact Match |
| **On-Time Delivery %** | `SELECT ROUND(COUNT(CASE WHEN is_late = FALSE THEN 1 END)*100.0/COUNT(*), 2) FROM mart.fact_orders WHERE is_delivered = TRUE;` | `[On-Time %]` | **93.23%** | ✅ Exact Match |
| **Avg Review Score** | `SELECT ROUND(AVG(review_score), 2) FROM mart.fact_orders;` | `[Avg Review Score]` | **4.09** | ✅ Exact Match |
