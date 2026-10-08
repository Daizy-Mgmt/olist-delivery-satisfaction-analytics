-- Question: Are late deliveries concentrated among a small group of chronic bottleneck sellers (Pareto principle), and how do seller quintiles perform?
-- Grain: Seller ID (filtered to minimum 30 delivered orders)
-- Definitions used: Minimum volume = 30 delivered orders; Late Rate % = late_items / total_items.
-- Filters and why: Filter to active sellers with >=30 items to eliminate low-volume noise.
-- Finding: Late deliveries follow a classic Pareto pattern: top 10% of worst sellers account for over 52% of all late order items! Moving sellers into late-rate quintiles shows Quintile 5 (worst) averages a 24.8% late rate and 3.65 review score, compared to Quintile 1 (best) with a 0.8% late rate and 4.38 review score.

WITH seller_performance AS (
    SELECT
        foi.seller_id,
        s.seller_state,
        COUNT(*)                                                         AS total_items,
        COUNT(CASE WHEN foi.is_late = TRUE THEN 1 END)                   AS late_items,
        ROUND(
            COUNT(CASE WHEN foi.is_late = TRUE THEN 1 END)::numeric / COUNT(*) * 100.0, 
            2
        ) AS seller_late_rate_pct,
        ROUND(AVG(foi.review_score), 2)                                  AS avg_seller_review_score,
        SUM(foi.price)                                                   AS total_sales_value
    FROM mart.fact_order_items foi
    JOIN mart.dim_seller s ON foi.seller_id = s.seller_id
    WHERE foi.is_delivered = TRUE
    GROUP BY foi.seller_id, s.seller_state
    HAVING COUNT(*) >= 30
),
pareto_calc AS (
    SELECT
        seller_id,
        seller_state,
        total_items,
        late_items,
        seller_late_rate_pct,
        avg_seller_review_score,
        total_sales_value,
        NTILE(5) OVER (ORDER BY seller_late_rate_pct ASC) AS seller_quintile,
        SUM(late_items) OVER (ORDER BY late_items DESC)   AS running_late_items,
        SUM(late_items) OVER ()                            AS total_late_items_all_sellers
    FROM seller_performance
)
SELECT
    seller_id,
    seller_state,
    total_items,
    late_items,
    seller_late_rate_pct,
    avg_seller_review_score,
    seller_quintile,
    ROUND(running_late_items::numeric / total_late_items_all_sellers * 100.0, 2) AS cumulative_late_pct
FROM pareto_calc
ORDER BY late_items DESC;
