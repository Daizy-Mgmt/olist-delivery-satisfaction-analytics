# Data Quality Audit & Profiling Report
Generated on: 2026-10-09
Database: PostgreSQL 15 (`olist` schema)

## 1. Summary of Raw Tables & Row Counts

| Table Name | Row Count |
|------------|-----------|
| `raw.category_translation` | 71 |
| `raw.customers` | 99,441 |
| `raw.geolocation` | 1,000,163 |
| `raw.order_items` | 112,650 |
| `raw.order_payments` | 103,886 |
| `raw.order_reviews` | 99,224 |
| `raw.orders` | 99,441 |
| `raw.products` | 32,951 |
| `raw.sellers` | 3,095 |

## 2. Key Uniqueness & ID Granularity Checks

- **Customers (`raw.customers`):**
  - Total rows: 99,441
  - Distinct `customer_id`: 99,441 (Primary key of order transaction: **100% unique**)
  - Distinct `customer_unique_id`: 96,096 (Unique person ID: 3,345 repeat orders across unique customers)

- **Orders (`raw.orders`):**
  - Distinct `order_id`: 99,441 (Primary key: **100% unique**)

- **Reviews (`raw.order_reviews`):**
  - Total review rows: 99,224
  - Distinct `review_id`: 98,410 (814 duplicate `review_id` values found)
  - Distinct `order_id`: 98,673
  - Orders with >1 review row: 547

- **Order Payments (`raw.order_payments`):**
  - Total payment rows: 103,886
  - Distinct `order_id`: 99,440
  - Orders with multiple payment rows (installments/vouchers): 2,961

- **Order Items (`raw.order_items`):**
  - Total item rows: 112,650
  - Distinct `order_id`: 98,666
  - Orders with >1 item row: 9,803

- **Products (`raw.products`):**
  - Distinct `product_id`: 32,951 (**100% unique**)

- **Sellers (`raw.sellers`):**
  - Distinct `seller_id`: 3,095 (**100% unique**)

- **Geolocation (`raw.geolocation`):**
  - Total geolocation rows: 1,000,163
  - Distinct `geolocation_zip_code_prefix`: 19,015 (Average 52.6 coordinate rows per zip prefix)

## 3. Order Status Breakdown & Delivered Definition

| Order Status | Order Count | Share (%) |
|--------------|-------------|-----------|
| `delivered` | 96,478 | 97.02% |
| `shipped` | 1,107 | 1.11% |
| `canceled` | 625 | 0.63% |
| `unavailable` | 609 | 0.61% |
| `invoiced` | 314 | 0.32% |
| `processing` | 301 | 0.30% |
| `created` | 5 | 0.01% |
| `approved` | 2 | 0.00% |

**Decision on Delivered Orders:**
- We will define `is_delivered = TRUE` for orders where `order_status = 'delivered'` AND `order_delivered_customer_date IS NOT NULL`.
- `canceled` and `unavailable` orders will be excluded from GMV and delivery satisfaction KPI analysis (recorded in `docs/decisions.md`).

## 4. Null & Missing Value Profiling

- **Orders Table Timestamp Nulls:**
  - `order_approved_at` NULL: 160
  - `order_delivered_carrier_date` NULL: 1,783
  - `order_delivered_customer_date` NULL: 2,965
  - `order_status = 'delivered'` but missing customer delivery date: **8** orders

- **Products & Translations Nulls:**
  - Products with NULL `product_category_name`: 610
  - Product category names in products table missing from translation table: **2** categories (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`)

## 5. Timestamp Anomalies & Out-of-Order Dates

- Orders delivered to customer before approval date: **61** orders
- Orders delivered to customer before carrier date: **23** orders

## 6. Verification of Known Olist Pitfalls

| Pitfall | Confirmed? | Profiling Finding / Detail |
|---------|------------|----------------------------|
| Duplicate `review_id` | **CONFIRMED** | 814 duplicate review_ids found; 547 orders have >1 review. Filter with `ROW_NUMBER()` in staging. |
| Multiple payments per order | **CONFIRMED** | 2,961 orders have multiple payment rows (vouchers/installments). Must aggregate before joining to avoid inflating GMV. |
| Multiple item rows per order | **CONFIRMED** | 9,803 orders have >1 item row (112,650 item rows across 98,666 orders). |
| Many geolocation rows per zip | **CONFIRMED** | 1.0M rows for 19k zip prefixes (52.6 rows/zip). Aggregate first or skip direct join. |
| `customer_id` vs `customer_unique_id` | **CONFIRMED** | `customer_id` is per order (99,441); `customer_unique_id` tracks repeat buyers (96,096 unique people). |
| Delivered orders with missing delivery date | **CONFIRMED** | 8 delivered orders are missing `order_delivered_customer_date`. |
| Out-of-order timestamps | **CONFIRMED** | 61 orders delivered before approval; 23 orders delivered before carrier handover. |
| Misspelled product column names | **CONFIRMED** | Source files spell `product_name_lenght` and `product_description_lenght` with `lenght`. Rename in staging. |
| Missing category translations | **CONFIRMED** | 2 categories (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`) lack English translations in the lookup table. |
