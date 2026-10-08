-- Question: How strongly do delivery delays impact customer review scores, and what is the share of 1-2 star negative reviews per delay bucket?
-- Grain: Delay bucket ('On time / early', '1-3 days late', '4-7 days late', '8+ days late', 'Not delivered')
-- Definitions used: Low Score Share % = (Count of reviews with score 1 or 2) / Total Reviews in bucket.
-- Filters and why: Include all valid orders with review scores to quantify the full satisfaction drop off.
-- Finding: On-time or early deliveries achieve an average review score of 4.25 (only 10.3% low scores). When delivery is 1-3 days late, average score drops to 2.99 (39.8% low scores). Orders 8+ days late collapse to an average score of 1.60 with 77.2% 1-star or 2-star reviews!

SELECT
    delay_bucket,
    COUNT(order_id)                                           AS total_orders,
    COUNT(review_score)                                       AS total_reviews,
    ROUND(AVG(review_score), 2)                               AS avg_review_score,
    COUNT(CASE WHEN review_score IN (1, 2) THEN 1 END)        AS low_score_reviews_count,
    ROUND(
        COUNT(CASE WHEN review_score IN (1, 2) THEN 1 END)::numeric / NULLIF(COUNT(review_score), 0) * 100.0, 
        2
    ) AS low_score_share_pct,
    ROUND(
        COUNT(CASE WHEN review_score = 5 THEN 1 END)::numeric / NULLIF(COUNT(review_score), 0) * 100.0, 
        2
    ) AS five_star_share_pct
FROM mart.fact_orders
GROUP BY delay_bucket
ORDER BY 
    CASE delay_bucket
        WHEN 'On time / early' THEN 1
        WHEN '1-3 days late' THEN 2
        WHEN '4-7 days late' THEN 3
        WHEN '8+ days late' THEN 4
        WHEN 'Not delivered' THEN 5
    END;
