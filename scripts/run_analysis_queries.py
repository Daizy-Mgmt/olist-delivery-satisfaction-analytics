import os
import glob
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER", "olist")
password = os.getenv("POSTGRES_PASSWORD", "olist_password_local")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5433")
db = os.getenv("POSTGRES_DB", "olist")

conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"

os.makedirs("docs/results", exist_ok=True)

query_files = sorted(glob.glob("sql/analysis/*.sql"))

print(f"Found {len(query_files)} analysis SQL queries to execute:\n")

with psycopg.connect(conn_str) as conn:
    for q_path in query_files:
        fname = os.path.basename(q_path)
        print(f"--------------------------------------------------")
        print(f"Executing: {fname}")
        
        with open(q_path, "r", encoding="utf-8") as f:
            sql = f.read()
            
        df = pd.read_sql_query(sql, conn)
        
        csv_out = os.path.join("docs/results", fname.replace(".sql", ".csv"))
        df.to_csv(csv_out, index=False)
        
        print(f"Result shape: {df.shape[0]} rows x {df.shape[1]} cols | Saved to {csv_out}")
        print(df.head(5).to_string(index=False))
        print("\n")

print("All analysis queries executed successfully and saved to docs/results/!")
