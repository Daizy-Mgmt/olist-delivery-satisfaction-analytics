# Metric Reconciliation Report: SQL vs BI Engine

**Audited on:** 2026-10-13  
**Database:** PostgreSQL 15 (`mart` schema)  
**Reporting Engine:** Power BI / Analytical Data Mart  

---

## 1. Headline Numbers Reconciliation Table

| Metric # | Metric Name | SQL Benchmark Query | SQL Benchmark Value | BI / DAX Measure Value | Match? (Yes/No) | Variance / Notes |
|:---:|---|---|:---:|:---:|:---:|---|
| **1** | **Gross Merchandise Value (GMV)** | `SELECT SUM(items_value) FROM mart.fact_orders;` | **$13,591,643.70** | **$13,591,643.70** | **YES** | Exact match. Verified against raw item price sum to ensure zero fanout. |
| **2** | **Total Orders** | `SELECT COUNT(DISTINCT order_id) FROM mart.fact_orders;` | **99,441** | **99,441** | **YES** | Exact match. Primary key grain is 100% unique. |
| **3** | **Delivered Orders** | `SELECT COUNT(*) FROM mart.fact_orders WHERE is_delivered = TRUE;` | **96,470** | **96,470** | **YES** | Exact match. Filtered strictly to `order_status = 'delivered'` with valid non-null delivery date. |
| **4** | **On-Time Delivery Rate %** | `SELECT ROUND(COUNT(CASE WHEN is_late = FALSE THEN 1 END)*100.0/COUNT(*), 2) FROM mart.fact_orders WHERE is_delivered = TRUE;` | **93.23%** | **93.23%** | **YES** | Exact match. 89,936 on-time delivered orders / 96,470 delivered orders. |
| **5** | **Average Review Score** | `SELECT ROUND(AVG(review_score), 2) FROM mart.fact_orders;` | **4.09** | **4.09** | **YES** | Exact match across deduplicated latest reviews. |

---

## 2. Granularity & Fanout Audit

1. **Items to Orders Join:**
   * Raw items sum = `$13,591,643.70` (112,650 rows across 98,666 orders).
   * Fact orders item sum = `$13,591,643.70` (99,441 total orders, including orders with missing items).
   * **Variance = $0.00** (Zero join multiplication).

2. **Order Payment Aggregation:**
   * 2,961 orders contain multiple payment transactions (vouchers, credit card installments).
   * Pre-aggregation in `staging.payments_per_order` prevented double-counting order totals.

3. **Customer Repeat Identification:**
   * 96,096 unique customer entities placed 99,441 orders.
   * Repeat customer count = 3,000 unique individuals (3.12% repeat rate).
