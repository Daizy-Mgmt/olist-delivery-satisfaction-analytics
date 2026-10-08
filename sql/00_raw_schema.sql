-- 00_raw_schema.sql
-- Creates the three schemas and the raw tables. Re-runnable.
-- Raw tables are loaded as TEXT on purpose: typing and cleaning happen in staging,
-- so a bad value never blocks the load and the raw layer stays an exact copy of the CSVs.
-- Column order must match the CSV header order. Check your CSV headers before loading.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

DROP TABLE IF EXISTS raw.customers, raw.geolocation, raw.order_items, raw.order_payments,
                     raw.order_reviews, raw.orders, raw.products, raw.sellers,
                     raw.category_translation CASCADE;

CREATE TABLE raw.customers (
    customer_id              TEXT,
    customer_unique_id       TEXT,
    customer_zip_code_prefix TEXT,
    customer_city            TEXT,
    customer_state           TEXT
);

CREATE TABLE raw.geolocation (
    geolocation_zip_code_prefix TEXT,
    geolocation_lat             TEXT,
    geolocation_lng             TEXT,
    geolocation_city            TEXT,
    geolocation_state           TEXT
);

CREATE TABLE raw.order_items (
    order_id            TEXT,
    order_item_id       TEXT,
    product_id          TEXT,
    seller_id           TEXT,
    shipping_limit_date TEXT,
    price               TEXT,
    freight_value       TEXT
);

CREATE TABLE raw.order_payments (
    order_id             TEXT,
    payment_sequential   TEXT,
    payment_type         TEXT,
    payment_installments TEXT,
    payment_value        TEXT
);

CREATE TABLE raw.order_reviews (
    review_id               TEXT,
    order_id                TEXT,
    review_score            TEXT,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TEXT,
    review_answer_timestamp TEXT
);

CREATE TABLE raw.orders (
    order_id                      TEXT,
    customer_id                   TEXT,
    order_status                  TEXT,
    order_purchase_timestamp      TEXT,
    order_approved_at             TEXT,
    order_delivered_carrier_date  TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT
);

CREATE TABLE raw.products (
    product_id                 TEXT,
    product_category_name      TEXT,
    product_name_lenght        TEXT,  -- sic: the source file spells it this way
    product_description_lenght TEXT,  -- sic
    product_photos_qty         TEXT,
    product_weight_g           TEXT,
    product_length_cm          TEXT,
    product_height_cm          TEXT,
    product_width_cm           TEXT
);

CREATE TABLE raw.sellers (
    seller_id              TEXT,
    seller_zip_code_prefix TEXT,
    seller_city            TEXT,
    seller_state           TEXT
);

CREATE TABLE raw.category_translation (
    product_category_name         TEXT,
    product_category_name_english TEXT
);
