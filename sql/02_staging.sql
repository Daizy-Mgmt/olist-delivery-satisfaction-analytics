-- 02_staging.sql
-- Creates typed, cleaned staging views in the staging schema.
-- Re-runnable script.

CREATE SCHEMA IF NOT EXISTS staging;

-- 1. Orders staging: cast timestamps
CREATE OR REPLACE VIEW staging.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp       AS purchase_ts,
    order_approved_at::timestamp              AS approved_ts,
    order_delivered_carrier_date::timestamp   AS carrier_ts,
    order_delivered_customer_date::timestamp  AS delivered_ts,
    order_estimated_delivery_date::timestamp  AS estimated_ts
FROM raw.orders;

-- 2. Order items staging: cast numeric price/freight, integer item id
CREATE OR REPLACE VIEW staging.order_items AS
SELECT
    order_id,
    order_item_id::integer                    AS order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp            AS shipping_limit_ts,
    price::numeric(10,2)                      AS price,
    freight_value::numeric(10,2)              AS freight_value
FROM raw.order_items;

-- 3. Payments aggregated per order: 1 row per order to prevent fanout
CREATE OR REPLACE VIEW staging.payments_per_order AS
SELECT
    order_id,
    SUM(payment_value::numeric(10,2))                  AS total_payment_value,
    MAX(payment_installments::integer)                 AS max_installments,
    MODE() WITHIN GROUP (ORDER BY payment_type)        AS primary_payment_type
FROM raw.order_payments
GROUP BY order_id;

-- 4. Latest review per order: deduplicate using ROW_NUMBER()
CREATE OR REPLACE VIEW staging.reviews_latest AS
WITH ranked_reviews AS (
    SELECT
        review_id,
        order_id,
        review_score::integer                         AS review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date::timestamp               AS creation_ts,
        review_answer_timestamp::timestamp             AS answer_ts,
        ROW_NUMBER() OVER (
            PARTITION BY order_id 
            ORDER BY review_creation_date DESC, review_answer_timestamp DESC
        ) AS rn
    FROM raw.order_reviews
)
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    creation_ts,
    answer_ts
FROM ranked_reviews
WHERE rn = 1;

-- 5. Products staging: cast types, fix column spelling, map category translations
CREATE OR REPLACE VIEW staging.products AS
SELECT
    p.product_id,
    COALESCE(p.product_category_name, 'unknown') AS category_name_pt,
    COALESCE(
        t.product_category_name_english,
        CASE p.product_category_name
            WHEN 'pc_gamer' THEN 'pc_gamer'
            WHEN 'portateis_cozinha_e_preparadores_de_alimentos' THEN 'portable_kitchen_food_processors'
            ELSE 'unknown'
        END
    ) AS category_name_en,
    p.product_name_lenght::integer             AS product_name_length,
    p.product_description_lenght::integer      AS product_description_length,
    p.product_photos_qty::integer              AS product_photos_qty,
    p.product_weight_g::numeric(10,2)          AS product_weight_g,
    p.product_length_cm::numeric(10,2)         AS product_length_cm,
    p.product_height_cm::numeric(10,2)         AS product_height_cm,
    p.product_width_cm::numeric(10,2)          AS product_width_cm
FROM raw.products p
LEFT JOIN raw.category_translation t ON p.product_category_name = t.product_category_name;

-- 6. Customers staging
CREATE OR REPLACE VIEW staging.customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM raw.customers;

-- 7. Sellers staging
CREATE OR REPLACE VIEW staging.sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM raw.sellers;
