import os
import glob
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

print("1. Running 00_raw_schema.sql...")
with open("sql/00_raw_schema.sql", "r", encoding="utf-8") as f:
    schema_sql = f.read()

with engine.begin() as conn:
    conn.execute(text(schema_sql))
print("Schemas and raw tables created successfully.")

print("2. Loading CSV data into raw tables...")

file_table_mapping = {
    "data/raw/olist_customers_dataset.csv": "customers",
    "data/raw/olist_geolocation_dataset.csv": "geolocation",
    "data/raw/olist_order_items_dataset.csv": "order_items",
    "data/raw/olist_order_payments_dataset.csv": "order_payments",
    "data/raw/olist_order_reviews_dataset.csv": "order_reviews",
    "data/raw/olist_orders_dataset.csv": "orders",
    "data/raw/olist_products_dataset.csv": "products",
    "data/raw/olist_sellers_dataset.csv": "sellers",
    "data/raw/product_category_name_translation.csv": "category_translation",
}

for csv_path, table_name in file_table_mapping.items():
    print(f"   Loading {csv_path} into raw.{table_name}...")
    df = pd.read_csv(csv_path, dtype=str)
    
    # Clean column names to match DDL
    df.columns = [c.strip() for c in df.columns]
    
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE raw.{table_name} CASCADE;"))
    
    df.to_sql(table_name, engine, schema="raw", if_exists="append", index=False, method="multi", chunksize=5000)
    print(f"   Loaded {len(df):,} rows into raw.{table_name}")

print("\n3. Verifying raw table row counts:")
tables = [
    "customers", "geolocation", "order_items", "order_payments",
    "order_reviews", "orders", "products", "sellers", "category_translation"
]

with engine.connect() as conn:
    for tbl in sorted(tables):
        res = conn.execute(text(f"SELECT COUNT(*) FROM raw.{tbl};")).scalar()
        print(f"   raw.{tbl}: {res:,} rows")
