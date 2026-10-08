-- 01_load_raw.sql
-- Loads the CSVs into the raw tables with psql's \copy (client-side, so Docker needs no mounts).
-- RUN FROM THE REPO ROOT so the relative paths below resolve:
--   psql -h localhost -U olist -d olist -f sql/01_load_raw.sql
-- Re-runnable: truncates first.

TRUNCATE raw.customers, raw.geolocation, raw.order_items, raw.order_payments,
         raw.order_reviews, raw.orders, raw.products, raw.sellers, raw.category_translation;

\copy raw.customers             FROM 'data/raw/olist_customers_dataset.csv'            WITH (FORMAT csv, HEADER true)
\copy raw.geolocation           FROM 'data/raw/olist_geolocation_dataset.csv'          WITH (FORMAT csv, HEADER true)
\copy raw.order_items           FROM 'data/raw/olist_order_items_dataset.csv'          WITH (FORMAT csv, HEADER true)
\copy raw.order_payments        FROM 'data/raw/olist_order_payments_dataset.csv'       WITH (FORMAT csv, HEADER true)
\copy raw.order_reviews         FROM 'data/raw/olist_order_reviews_dataset.csv'        WITH (FORMAT csv, HEADER true)
\copy raw.orders                FROM 'data/raw/olist_orders_dataset.csv'               WITH (FORMAT csv, HEADER true)
\copy raw.products              FROM 'data/raw/olist_products_dataset.csv'             WITH (FORMAT csv, HEADER true)
\copy raw.sellers               FROM 'data/raw/olist_sellers_dataset.csv'              WITH (FORMAT csv, HEADER true)
\copy raw.category_translation  FROM 'data/raw/product_category_name_translation.csv'  WITH (FORMAT csv, HEADER true)

-- Quick sanity check: record these counts in docs/data_quality.md
SELECT 'customers' AS table_name, COUNT(*) FROM raw.customers
UNION ALL SELECT 'geolocation',          COUNT(*) FROM raw.geolocation
UNION ALL SELECT 'order_items',          COUNT(*) FROM raw.order_items
UNION ALL SELECT 'order_payments',       COUNT(*) FROM raw.order_payments
UNION ALL SELECT 'order_reviews',        COUNT(*) FROM raw.order_reviews
UNION ALL SELECT 'orders',               COUNT(*) FROM raw.orders
UNION ALL SELECT 'products',             COUNT(*) FROM raw.products
UNION ALL SELECT 'sellers',              COUNT(*) FROM raw.sellers
UNION ALL SELECT 'category_translation', COUNT(*) FROM raw.category_translation;
