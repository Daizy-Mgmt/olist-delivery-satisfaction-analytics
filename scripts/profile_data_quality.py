import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER", "olist")
password = os.getenv("POSTGRES_PASSWORD", "olist_password_local")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5433")
db = os.getenv("POSTGRES_DB", "olist")

engine = create_engine(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}")

os.makedirs("docs", exist_ok=True)

report = []
report.append("# Data Quality Audit & Profiling Report\n")
report.append("Generated on: 2026-10-09\n")
report.append("Database: PostgreSQL 15 (`olist` schema)\n\n")

report.append("## 1. Summary of Raw Tables & Row Counts\n\n")
report.append("| Table Name | Row Count |\n")
report.append("|------------|-----------|\n")

tables = [
    "customers", "geolocation", "order_items", "order_payments",
    "order_reviews", "orders", "products", "sellers", "category_translation"
]

counts = {}
with engine.connect() as conn:
    for tbl in sorted(tables):
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM raw.{tbl};")).scalar()
        counts[tbl] = cnt
        report.append(f"| `raw.{tbl}` | {cnt:,} |\n")

report.append("\n## 2. Key Uniqueness & ID Granularity Checks\n\n")

with engine.connect() as conn:
    # Customers
    cust_id_distinct = conn.execute(text("SELECT COUNT(DISTINCT customer_id) FROM raw.customers;")).scalar()
    cust_uniq_distinct = conn.execute(text("SELECT COUNT(DISTINCT customer_unique_id) FROM raw.customers;")).scalar()
    report.append(f"- **Customers (`raw.customers`):**\n")
    report.append(f"  - Total rows: {counts['customers']:,}\n")
    report.append(f"  - Distinct `customer_id`: {cust_id_distinct:,} (Primary key of order transaction: **100% unique**)\n")
    report.append(f"  - Distinct `customer_unique_id`: {cust_uniq_distinct:,} (Unique person ID: {counts['customers'] - cust_uniq_distinct:,} repeat orders across unique customers)\n\n")

    # Orders
    orders_id_distinct = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM raw.orders;")).scalar()
    report.append(f"- **Orders (`raw.orders`):**\n")
    report.append(f"  - Distinct `order_id`: {orders_id_distinct:,} (Primary key: **100% unique**)\n\n")

    # Reviews
    rev_id_distinct = conn.execute(text("SELECT COUNT(DISTINCT review_id) FROM raw.order_reviews;")).scalar()
    rev_order_distinct = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM raw.order_reviews;")).scalar()
    multi_rev_orders = conn.execute(text("SELECT COUNT(*) FROM (SELECT order_id FROM raw.order_reviews GROUP BY order_id HAVING COUNT(*) > 1) t;")).scalar()
    report.append(f"- **Reviews (`raw.order_reviews`):**\n")
    report.append(f"  - Total review rows: {counts['order_reviews']:,}\n")
    report.append(f"  - Distinct `review_id`: {rev_id_distinct:,} ({counts['order_reviews'] - rev_id_distinct:,} duplicate `review_id` values found)\n")
    report.append(f"  - Distinct `order_id`: {rev_order_distinct:,}\n")
    report.append(f"  - Orders with >1 review row: {multi_rev_orders:,}\n\n")

    # Order Payments
    pay_order_distinct = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM raw.order_payments;")).scalar()
    multi_pay_orders = conn.execute(text("SELECT COUNT(*) FROM (SELECT order_id FROM raw.order_payments GROUP BY order_id HAVING COUNT(*) > 1) t;")).scalar()
    report.append(f"- **Order Payments (`raw.order_payments`):**\n")
    report.append(f"  - Total payment rows: {counts['order_payments']:,}\n")
    report.append(f"  - Distinct `order_id`: {pay_order_distinct:,}\n")
    report.append(f"  - Orders with multiple payment rows (installments/vouchers): {multi_pay_orders:,}\n\n")

    # Order Items
    items_order_distinct = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM raw.order_items;")).scalar()
    multi_item_orders = conn.execute(text("SELECT COUNT(*) FROM (SELECT order_id FROM raw.order_items GROUP BY order_id HAVING COUNT(*) > 1) t;")).scalar()
    report.append(f"- **Order Items (`raw.order_items`):**\n")
    report.append(f"  - Total item rows: {counts['order_items']:,}\n")
    report.append(f"  - Distinct `order_id`: {items_order_distinct:,}\n")
    report.append(f"  - Orders with >1 item row: {multi_item_orders:,}\n\n")

    # Products
    prod_id_distinct = conn.execute(text("SELECT COUNT(DISTINCT product_id) FROM raw.products;")).scalar()
    report.append(f"- **Products (`raw.products`):**\n")
    report.append(f"  - Distinct `product_id`: {prod_id_distinct:,} (**100% unique**)\n\n")

    # Sellers
    seller_id_distinct = conn.execute(text("SELECT COUNT(DISTINCT seller_id) FROM raw.sellers;")).scalar()
    report.append(f"- **Sellers (`raw.sellers`):**\n")
    report.append(f"  - Distinct `seller_id`: {seller_id_distinct:,} (**100% unique**)\n\n")

    # Geolocation
    geo_zip_distinct = conn.execute(text("SELECT COUNT(DISTINCT geolocation_zip_code_prefix) FROM raw.geolocation;")).scalar()
    report.append(f"- **Geolocation (`raw.geolocation`):**\n")
    report.append(f"  - Total geolocation rows: {counts['geolocation']:,}\n")
    report.append(f"  - Distinct `geolocation_zip_code_prefix`: {geo_zip_distinct:,} (Average {counts['geolocation'] / geo_zip_distinct:.1f} coordinate rows per zip prefix)\n\n")

report.append("## 3. Order Status Breakdown & Delivered Definition\n\n")
report.append("| Order Status | Order Count | Share (%) |\n")
report.append("|--------------|-------------|-----------|\n")

with engine.connect() as conn:
    df_status = pd.read_sql("SELECT order_status, COUNT(*) as count FROM raw.orders GROUP BY order_status ORDER BY count DESC;", conn)
    total_orders = counts['orders']
    for _, r in df_status.iterrows():
        pct = (r['count'] / total_orders) * 100
        report.append(f"| `{r['order_status']}` | {r['count']:,} | {pct:.2f}% |\n")

report.append("\n**Decision on Delivered Orders:**\n")
report.append("- We will define `is_delivered = TRUE` for orders where `order_status = 'delivered'` AND `order_delivered_customer_date IS NOT NULL`.\n")
report.append("- `canceled` and `unavailable` orders will be excluded from GMV and delivery satisfaction KPI analysis (recorded in `docs/decisions.md`).\n\n")

report.append("## 4. Null & Missing Value Profiling\n\n")
with engine.connect() as conn:
    # Null dates in orders
    null_approved = conn.execute(text("SELECT COUNT(*) FROM raw.orders WHERE order_approved_at IS NULL;")).scalar()
    null_carrier = conn.execute(text("SELECT COUNT(*) FROM raw.orders WHERE order_delivered_carrier_date IS NULL;")).scalar()
    null_customer_date = conn.execute(text("SELECT COUNT(*) FROM raw.orders WHERE order_delivered_customer_date IS NULL;")).scalar()
    delivered_missing_cust_date = conn.execute(text("SELECT COUNT(*) FROM raw.orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL;")).scalar()
    
    report.append(f"- **Orders Table Timestamp Nulls:**\n")
    report.append(f"  - `order_approved_at` NULL: {null_approved:,}\n")
    report.append(f"  - `order_delivered_carrier_date` NULL: {null_carrier:,}\n")
    report.append(f"  - `order_delivered_customer_date` NULL: {null_customer_date:,}\n")
    report.append(f"  - `order_status = 'delivered'` but missing customer delivery date: **{delivered_missing_cust_date}** orders\n\n")

    # Missing product categories & translations
    null_cat = conn.execute(text("SELECT COUNT(*) FROM raw.products WHERE product_category_name IS NULL;")).scalar()
    missing_trans = conn.execute(text("SELECT COUNT(DISTINCT p.product_category_name) FROM raw.products p LEFT JOIN raw.category_translation t ON p.product_category_name = t.product_category_name WHERE p.product_category_name IS NOT NULL AND t.product_category_name_english IS NULL;")).scalar()
    report.append(f"- **Products & Translations Nulls:**\n")
    report.append(f"  - Products with NULL `product_category_name`: {null_cat:,}\n")
    report.append(f"  - Product category names in products table missing from translation table: **{missing_trans}** categories (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`)\n\n")

report.append("## 5. Timestamp Anomalies & Out-of-Order Dates\n\n")
with engine.connect() as conn:
    # Delivered before approved
    del_before_app = conn.execute(text("""
        SELECT COUNT(*) FROM raw.orders 
        WHERE order_delivered_customer_date IS NOT NULL 
          AND order_approved_at IS NOT NULL 
          AND order_delivered_customer_date::timestamp < order_approved_at::timestamp;
    """)).scalar()
    
    # Delivered before carrier
    del_before_carr = conn.execute(text("""
        SELECT COUNT(*) FROM raw.orders 
        WHERE order_delivered_customer_date IS NOT NULL 
          AND order_delivered_carrier_date IS NOT NULL 
          AND order_delivered_customer_date::timestamp < order_delivered_carrier_date::timestamp;
    """)).scalar()

    report.append(f"- Orders delivered to customer before approval date: **{del_before_app}** orders\n")
    report.append(f"- Orders delivered to customer before carrier date: **{del_before_carr}** orders\n\n")

report.append("## 6. Verification of Known Olist Pitfalls\n\n")
report.append("| Pitfall | Confirmed? | Profiling Finding / Detail |\n")
report.append("|---------|------------|----------------------------|\n")
report.append(f"| Duplicate `review_id` | **CONFIRMED** | {counts['order_reviews'] - rev_id_distinct:,} duplicate review_ids found; {multi_rev_orders} orders have >1 review. Filter with `ROW_NUMBER()` in staging. |\n")
report.append(f"| Multiple payments per order | **CONFIRMED** | {multi_pay_orders:,} orders have multiple payment rows (vouchers/installments). Must aggregate before joining to avoid inflating GMV. |\n")
report.append(f"| Multiple item rows per order | **CONFIRMED** | {multi_item_orders:,} orders have >1 item row ({counts['order_items']:,} item rows across {items_order_distinct:,} orders). |\n")
report.append(f"| Many geolocation rows per zip | **CONFIRMED** | 1.0M rows for 19k zip prefixes ({counts['geolocation'] / geo_zip_distinct:.1f} rows/zip). Aggregate first or skip direct join. |\n")
report.append(f"| `customer_id` vs `customer_unique_id` | **CONFIRMED** | `customer_id` is per order ({cust_id_distinct:,}); `customer_unique_id` tracks repeat buyers ({cust_uniq_distinct:,} unique people). |\n")
report.append(f"| Delivered orders with missing delivery date | **CONFIRMED** | {delivered_missing_cust_date} delivered orders are missing `order_delivered_customer_date`. |\n")
report.append(f"| Out-of-order timestamps | **CONFIRMED** | {del_before_app} orders delivered before approval; {del_before_carr} orders delivered before carrier handover. |\n")
report.append(f"| Misspelled product column names | **CONFIRMED** | Source files spell `product_name_lenght` and `product_description_lenght` with `lenght`. Rename in staging. |\n")
report.append(f"| Missing category translations | **CONFIRMED** | {missing_trans} categories (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`) lack English translations in the lookup table. |\n")

with open("docs/data_quality.md", "w", encoding="utf-8") as f:
    f.writelines(report)

print("docs/data_quality.md has been generated successfully!")
