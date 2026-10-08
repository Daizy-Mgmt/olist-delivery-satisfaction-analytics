-- 03_marts.sql
-- Builds the Star Schema Dimensional Marts (mart schema).
-- Re-runnable: drops and recreates tables, adds PKs and indexes.

CREATE SCHEMA IF NOT EXISTS mart;

-- -----------------------------------------------------------------------------
-- 1. mart.dim_date
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.dim_date CASCADE;

CREATE TABLE mart.dim_date AS
SELECT
    d::date                                        AS date_actual,
    TO_CHAR(d, 'YYYYMMDD')::integer               AS date_key,
    EXTRACT(YEAR FROM d)::integer                 AS year,
    EXTRACT(QUARTER FROM d)::integer              AS quarter,
    EXTRACT(MONTH FROM d)::integer                AS month,
    TO_CHAR(d, 'TMMonth')                         AS month_name,
    TO_CHAR(d, 'YYYY-MM')                         AS year_month,
    EXTRACT(ISODOW FROM d)::integer               AS day_of_week,
    TO_CHAR(d, 'TMDay')                           AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series(
    '2016-01-01'::date,
    '2018-12-31'::date,
    '1 day'::interval
) AS d;

ALTER TABLE mart.dim_date ADD PRIMARY KEY (date_actual);
CREATE UNIQUE INDEX idx_dim_date_key ON mart.dim_date(date_key);


-- -----------------------------------------------------------------------------
-- 2. mart.dim_customer (Grain: 1 row per customer_unique_id)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.dim_customer CASCADE;

CREATE TABLE mart.dim_customer AS
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        MIN(o.purchase_ts) AS first_order_ts,
        COUNT(DISTINCT o.order_id) AS total_orders,
        (ARRAY_AGG(c.customer_state ORDER BY o.purchase_ts ASC))[1] AS first_order_state,
        (ARRAY_AGG(c.customer_city ORDER BY o.purchase_ts ASC))[1] AS first_order_city
    FROM staging.customers c
    JOIN staging.orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    customer_unique_id,
    first_order_ts,
    total_orders,
    first_order_state,
    first_order_city,
    CASE WHEN total_orders > 1 THEN TRUE ELSE FALSE END AS is_repeat_customer
FROM customer_orders;

ALTER TABLE mart.dim_customer ADD PRIMARY KEY (customer_unique_id);


-- -----------------------------------------------------------------------------
-- 3. mart.dim_seller (Grain: 1 row per seller_id)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.dim_seller CASCADE;

CREATE TABLE mart.dim_seller AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM staging.sellers;

ALTER TABLE mart.dim_seller ADD PRIMARY KEY (seller_id);


-- -----------------------------------------------------------------------------
-- 4. mart.dim_product (Grain: 1 row per product_id)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.dim_product CASCADE;

CREATE TABLE mart.dim_product AS
SELECT
    product_id,
    category_name_pt,
    category_name_en,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM staging.products;

ALTER TABLE mart.dim_product ADD PRIMARY KEY (product_id);


-- -----------------------------------------------------------------------------
-- 5. mart.fact_orders (Grain: 1 row per order_id)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.fact_orders CASCADE;

CREATE TABLE mart.fact_orders AS
WITH order_item_aggregates AS (
    SELECT
        order_id,
        COUNT(order_item_id) AS items_count,
        SUM(price)          AS items_value,
        SUM(freight_value)  AS freight_value
    FROM staging.order_items
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_status,
    o.purchase_ts,
    o.approved_ts,
    o.carrier_ts,
    o.delivered_ts,
    o.estimated_ts,
    
    -- Delivery metrics
    CASE 
        WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL 
        THEN TRUE ELSE FALSE 
    END AS is_delivered,
    
    CASE 
        WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL 
        THEN (o.delivered_ts::date - o.purchase_ts::date)
        ELSE NULL 
    END AS delivery_days,
    
    CASE 
        WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL 
        THEN (o.delivered_ts::date - o.estimated_ts::date)
        ELSE NULL 
    END AS delay_days,
    
    CASE 
        WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL AND (o.delivered_ts::date > o.estimated_ts::date)
        THEN TRUE 
        WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL 
        THEN FALSE 
        ELSE NULL 
    END AS is_late,
    
    CASE 
        WHEN o.order_status != 'delivered' OR o.delivered_ts IS NULL THEN 'Not delivered'
        WHEN (o.delivered_ts::date <= o.estimated_ts::date) THEN 'On time / early'
        WHEN (o.delivered_ts::date - o.estimated_ts::date) BETWEEN 1 AND 3 THEN '1-3 days late'
        WHEN (o.delivered_ts::date - o.estimated_ts::date) BETWEEN 4 AND 7 THEN '4-7 days late'
        WHEN (o.delivered_ts::date - o.estimated_ts::date) >= 8 THEN '8+ days late'
        ELSE 'Not delivered'
    END AS delay_bucket,
    
    -- Review Score (from deduplicated latest review)
    r.review_score,
    
    -- Financials & Item counts
    COALESCE(i.items_count, 0)                 AS items_count,
    COALESCE(i.items_value, 0.00)              AS items_value,
    COALESCE(i.freight_value, 0.00)            AS freight_value,
    COALESCE(p.total_payment_value, 0.00)      AS payment_value,
    p.max_installments,
    p.primary_payment_type
FROM staging.orders o
JOIN staging.customers c ON o.customer_id = c.customer_id
LEFT JOIN order_item_aggregates i ON o.order_id = i.order_id
LEFT JOIN staging.payments_per_order p ON o.order_id = p.order_id
LEFT JOIN staging.reviews_latest r ON o.order_id = r.order_id;

ALTER TABLE mart.fact_orders ADD PRIMARY KEY (order_id);
CREATE INDEX idx_fact_orders_customer ON mart.fact_orders(customer_unique_id);
CREATE INDEX idx_fact_orders_purchase_ts ON mart.fact_orders(purchase_ts);
CREATE INDEX idx_fact_orders_is_late ON mart.fact_orders(is_late);


-- -----------------------------------------------------------------------------
-- 6. mart.fact_order_items (Grain: 1 row per order_item_id per order_id)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.fact_order_items CASCADE;

CREATE TABLE mart.fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    fo.customer_unique_id,
    fo.purchase_ts,
    oi.product_id,
    oi.seller_id,
    oi.shipping_limit_ts,
    oi.price,
    oi.freight_value,
    fo.is_delivered,
    fo.is_late,
    fo.delay_bucket,
    fo.review_score
FROM staging.order_items oi
JOIN mart.fact_orders fo ON oi.order_id = fo.order_id;

ALTER TABLE mart.fact_order_items ADD PRIMARY KEY (order_id, order_item_id);
CREATE INDEX idx_fact_items_product ON mart.fact_order_items(product_id);
CREATE INDEX idx_fact_items_seller ON mart.fact_order_items(seller_id);
