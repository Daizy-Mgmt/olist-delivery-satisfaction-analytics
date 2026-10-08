-- Question: Which Brazilian destination states experience the worst on-time delivery rates and lowest customer satisfaction?
-- Grain: Customer State (2-letter code)
-- Definitions used: Minimum volume threshold = at least 500 delivered orders to ensure statistical relevance.
-- Filters and why: Filter to delivered orders. State is destination customer_state.
-- Finding: Southeastern states near hubs (SP, PR, MG) enjoy high on-time rates (>93%) and fast delivery (7-11 days). Remote Northern/Northeastern states (RR, AP, AM, AL, MA, SE, BA) suffer terrible delivery times (20-28 days average) and high late rates (>15-25% late), resulting in significant review score drops.

WITH state_metrics AS (
    SELECT
        customer_state,
        COUNT(*)                                                     AS delivered_orders,
        COUNT(CASE WHEN is_late = TRUE THEN 1 END)                   AS late_orders,
        ROUND(
            COUNT(CASE WHEN is_late = FALSE THEN 1 END)::numeric / COUNT(*) * 100.0, 
            2
        ) AS on_time_rate_pct,
        ROUND(AVG(delivery_days), 1)                                 AS avg_delivery_days,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delivery_days)  AS median_delivery_days,
        ROUND(AVG(review_score), 2)                                  AS avg_review_score,
        ROUND(
            COUNT(CASE WHEN review_score IN (1, 2) THEN 1 END)::numeric / NULLIF(COUNT(review_score), 0) * 100.0, 
            2
        ) AS low_score_pct
    FROM mart.fact_orders
    WHERE is_delivered = TRUE
    GROUP BY customer_state
    HAVING COUNT(*) >= 500
)
SELECT
    customer_state,
    delivered_orders,
    late_orders,
    on_time_rate_pct,
    avg_delivery_days,
    median_delivery_days,
    avg_review_score,
    low_score_pct,
    RANK() OVER (ORDER BY on_time_rate_pct ASC) AS worst_on_time_rank
FROM state_metrics
ORDER BY on_time_rate_pct ASC;
