-- Question: Does experiencing a delivery delay on a customer's FIRST order reduce their likelihood of making a repeat purchase?
-- Grain: First-order delay status ('On time / early' vs 'Late')
-- Definitions used: Repeat Buyer = customer_unique_id with total_orders > 1.
-- Filters and why: Join customer dimension to identify first purchase experience.
-- Finding: Repeat purchase rate across Olist is low overall (3.12% unique customer repeat rate). However, customers whose VERY FIRST order arrived late had a repeat purchase rate of only 1.82%, compared to 3.24% for customers whose first order arrived on time (a ~44% relative drop in repeat customer conversion).

WITH first_orders AS (
    SELECT
        c.customer_unique_id,
        c.total_orders,
        c.is_repeat_customer,
        fo.order_id AS first_order_id,
        fo.is_late  AS first_order_is_late,
        fo.delay_bucket AS first_order_delay_bucket,
        fo.review_score AS first_order_review_score
    FROM mart.dim_customer c
    JOIN mart.fact_orders fo ON c.customer_unique_id = fo.customer_unique_id
      AND c.first_order_ts = fo.purchase_ts
)
SELECT
    first_order_delay_bucket,
    COUNT(*)                                                               AS total_customers,
    COUNT(CASE WHEN is_repeat_customer = TRUE THEN 1 END)                  AS repeat_customers,
    ROUND(
        COUNT(CASE WHEN is_repeat_customer = TRUE THEN 1 END)::numeric / COUNT(*) * 100.0, 
        2
    ) AS repeat_purchase_rate_pct,
    ROUND(AVG(first_order_review_score), 2)                                AS avg_first_review_score
FROM first_orders
GROUP BY first_order_delay_bucket
ORDER BY 
    CASE first_order_delay_bucket
        WHEN 'On time / early' THEN 1
        WHEN '1-3 days late' THEN 2
        WHEN '4-7 days late' THEN 3
        WHEN '8+ days late' THEN 4
        WHEN 'Not delivered' THEN 5
    END;
