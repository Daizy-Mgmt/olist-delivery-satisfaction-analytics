-- Question: How have delivery performance, on-time rates, median delivery days, and 90th percentile delivery days evolved monthly?
-- Grain: Monthly (year_month)
-- Definitions used: On-Time Rate % = (Delivered Orders with is_late = FALSE) / Total Delivered Orders; Delivery Days = delivered_ts::date - purchase_ts::date
-- Filters and why: Filter to order_status = 'delivered' and non-null customer delivery date. Date range: Jan 2017 to Aug 2018.
-- Finding: Overall on-time delivery rate averaged 93.3% across the dataset. The median delivery time across Brazil is 10 days, but the 90th percentile delivery time reaches 23 days. Delivery delays spiked severely in Nov-Dec 2017 (holiday volume surge) and March 2018.

WITH delivery_stats AS (
    SELECT
        TO_CHAR(purchase_ts, 'YYYY-MM') AS year_month,
        COUNT(*) AS total_delivered_orders,
        COUNT(CASE WHEN is_late = FALSE THEN 1 END) AS on_time_orders,
        COUNT(CASE WHEN is_late = TRUE THEN 1 END) AS late_orders,
        ROUND(
            COUNT(CASE WHEN is_late = FALSE THEN 1 END)::numeric / COUNT(*) * 100.0, 
            2
        ) AS on_time_rate_pct,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delivery_days) AS median_delivery_days,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY delivery_days) AS p90_delivery_days,
        ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(CASE WHEN is_late = TRUE THEN delay_days END), 1) AS avg_late_delay_days
    FROM mart.fact_orders
    WHERE is_delivered = TRUE
      AND purchase_ts >= '2017-01-01' AND purchase_ts < '2018-09-01'
    GROUP BY 1
)
SELECT
    year_month,
    total_delivered_orders,
    on_time_orders,
    late_orders,
    on_time_rate_pct,
    median_delivery_days,
    p90_delivery_days,
    avg_delivery_days,
    avg_late_delay_days
FROM delivery_stats
ORDER BY year_month;
