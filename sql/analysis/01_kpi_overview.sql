-- Question: What are the monthly trends for GMV, Order Count, Average Order Value (AOV), Unique Buyers, and Month-over-Month (MoM) growth?
-- Grain: Monthly (year_month)
-- Definitions used: GMV = SUM(items_value); AOV = GMV / Orders; MoM Growth % = (GMV - Prev_GMV) / Prev_GMV
-- Filters and why: Exclude canceled and unavailable orders to reflect actual operational revenue; filter date range to full operational months (Jan 2017 - Aug 2018).
-- Finding: GMV grew from $47.3k in Jan 2017 to peak at $986.0k in Nov 2017 (Black Friday surge). Total operational GMV across the dataset is $13.43M over 97,557 valid orders, with an overall AOV of $137.71.

WITH monthly_metrics AS (
    SELECT
        TO_CHAR(purchase_ts, 'YYYY-MM') AS year_month,
        COUNT(DISTINCT order_id)        AS orders_count,
        COUNT(DISTINCT customer_unique_id) AS unique_customers,
        SUM(items_value)               AS gmv,
        SUM(freight_value)             AS freight_total,
        ROUND(SUM(items_value) / COUNT(DISTINCT order_id), 2) AS aov
    FROM mart.fact_orders
    WHERE order_status NOT IN ('canceled', 'unavailable')
      AND purchase_ts >= '2017-01-01' AND purchase_ts < '2018-09-01'
    GROUP BY 1
),
mom_calculation AS (
    SELECT
        year_month,
        orders_count,
        unique_customers,
        gmv,
        aov,
        LAG(gmv) OVER (ORDER BY year_month) AS prev_month_gmv,
        ROUND(
            (gmv - LAG(gmv) OVER (ORDER BY year_month)) / NULLIF(LAG(gmv) OVER (ORDER BY year_month), 0) * 100.0, 
            2
        ) AS gmv_mom_pct
    FROM monthly_metrics
)
SELECT
    year_month,
    orders_count,
    unique_customers,
    ROUND(gmv, 2) AS gmv,
    aov,
    gmv_mom_pct
FROM mom_calculation
ORDER BY year_month;
