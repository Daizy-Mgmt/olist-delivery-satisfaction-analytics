# Data Cleaning & Modeling Architecture Decisions

Documented on: 2026-10-09

## 1. GMV & Delivered Order Scope
- **GMV Scope:** Exclude orders with status `canceled` or `unavailable`. GMV is computed as `SUM(price)` for non-canceled/unavailable orders.
- **Delivered Orders Scope:** An order is classified as `is_delivered = TRUE` if `order_status = 'delivered'` AND `order_delivered_customer_date IS NOT NULL` (excludes 8 orders marked `delivered` but missing timestamp).

## 2. Review Deduplication Strategy
- An order can have multiple review rows (547 orders affected; 814 duplicate review_ids).
- In `staging.reviews_latest`, deduplicate reviews per order using:
  `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC, review_answer_timestamp DESC)`
  taking the latest submitted review for each order.

## 3. Order Payments Aggregation
- 2,961 orders have multiple payment records (split across installments or multiple payment types/vouchers).
- In `staging.payments_per_order`, aggregate payment values to 1 row per order (`SUM(payment_value)`, max payment installments, primary payment type) before joining to `fact_orders` to avoid fanout / revenue multiplication.

## 4. Product Category Translations
- 610 products have `product_category_name IS NULL`. Categorize as `'unknown'`.
- 2 category names (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`) are missing from the English translation table.
- Map them explicitly in staging:
  - `pc_gamer` -> `'pc_gamer'`
  - `portateis_cozinha_e_preparadores_de_alimentos` -> `'portable_kitchen_food_processors'`
  - Misspelled source column names (`product_name_lenght`, `product_description_lenght`) renamed to standard spelling (`product_name_length`, `product_description_length`).

## 5. Delay Buckets Definition
- Delay calculated as `(delivered_customer_date::date - estimated_delivery_date::date)` in whole days.
- Delay buckets:
  - `On time / early`: `delay_days <= 0`
  - `1-3 days late`: `delay_days BETWEEN 1 AND 3`
  - `4-7 days late`: `delay_days BETWEEN 4 AND 7`
  - `8+ days late`: `delay_days >= 8`
  - `Not delivered`: `is_delivered = FALSE` or missing customer delivery date.
