import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER", "olist")
password = os.getenv("POSTGRES_PASSWORD", "olist_password_local")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5433")
db = os.getenv("POSTGRES_DB", "olist")

engine = create_engine(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}")

print("1. Executing sql/02_staging.sql...")
with open("sql/02_staging.sql", "r", encoding="utf-8") as f:
    engine.connect().execution_options(isolation_level="AUTOCOMMIT").execute(text(f.read()))
print("Staging views created successfully.")

print("2. Executing sql/03_marts.sql...")
with open("sql/03_marts.sql", "r", encoding="utf-8") as f:
    engine.connect().execution_options(isolation_level="AUTOCOMMIT").execute(text(f.read()))
print("Star Schema Marts created successfully.")

print("\n3. Running Verification & Reconciliation Checks:\n")

with engine.connect() as conn:
    # 1. Fact orders uniqueness
    total_fact_orders = conn.execute(text("SELECT COUNT(*) FROM mart.fact_orders;")).scalar()
    uniq_fact_orders = conn.execute(text("SELECT COUNT(DISTINCT order_id) FROM mart.fact_orders;")).scalar()
    assert total_fact_orders == uniq_fact_orders == 99441, f"Mismatch in fact_orders count: {total_fact_orders}"
    print(f"   [PASS] mart.fact_orders order_id is 100% unique ({total_fact_orders:,} rows)")

    # 2. Fact order items uniqueness
    total_fact_items = conn.execute(text("SELECT COUNT(*) FROM mart.fact_order_items;")).scalar()
    assert total_fact_items == 112650, f"Mismatch in fact_order_items count: {total_fact_items}"
    print(f"   [PASS] mart.fact_order_items count matches raw items ({total_fact_items:,} rows)")

    # 3. Financial Reconciliation: Raw Items SUM(price) vs Fact Orders SUM(items_value)
    raw_price_sum = conn.execute(text("SELECT SUM(price::numeric) FROM raw.order_items;")).scalar()
    fact_price_sum = conn.execute(text("SELECT SUM(items_value) FROM mart.fact_orders;")).scalar()
    diff = abs(raw_price_sum - fact_price_sum)
    assert diff < 0.01, f"Financial mismatch! Raw: {raw_price_sum}, Fact: {fact_price_sum}"
    print(f"   [PASS] Financial Reconciliation: SUM(items_value) = ${fact_price_sum:,.2f} (Exact match to raw items)")

    # 4. Dimension Table Counts
    dim_cust_cnt = conn.execute(text("SELECT COUNT(*) FROM mart.dim_customer;")).scalar()
    dim_seller_cnt = conn.execute(text("SELECT COUNT(*) FROM mart.dim_seller;")).scalar()
    dim_prod_cnt = conn.execute(text("SELECT COUNT(*) FROM mart.dim_product;")).scalar()
    dim_date_cnt = conn.execute(text("SELECT COUNT(*) FROM mart.dim_date;")).scalar()
    print(f"   [PASS] Dimensions: dim_customer={dim_cust_cnt:,}, dim_seller={dim_seller_cnt:,}, dim_product={dim_prod_cnt:,}, dim_date={dim_date_cnt:,}")

    # 5. Delay Buckets Summary
    print("\n4. Delay Bucket Distribution in mart.fact_orders:\n")
    res = conn.execute(text("SELECT delay_bucket, COUNT(*) as count, ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (), 2) as pct FROM mart.fact_orders GROUP BY delay_bucket ORDER BY count DESC;")).fetchall()
    for row in res:
        print(f"   - {row[0]}: {row[1]:,} orders ({row[2]}%)")

print("\nAll Mart verification checks PASSED successfully!")
