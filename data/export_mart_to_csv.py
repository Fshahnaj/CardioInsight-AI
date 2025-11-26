import duckdb
import pandas as pd
from pathlib import Path

# --- IMPORTANT: correct warehouse path ---
WAREHOUSE_PATH = Path("C:/Users/fujai/CardioInsight-AI/cardioinsight_dbt/dev.duckdb")

EXPORT_PATH = Path("data/exports/mart_cardio_risk.csv")
EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

def main():
    print(f"[EXPORT] Connecting to {WAREHOUSE_PATH} ...")
    con = duckdb.connect(str(WAREHOUSE_PATH))

    print("[EXPORT] Checking available tables...")
    tables = con.execute("SHOW TABLES").df()
    print(tables)

    print("[EXPORT] Loading mart_cardio_risk ...")
    df = con.execute("SELECT * FROM mart_cardio_risk").df()

    print(f"[EXPORT] Writing CSV to {EXPORT_PATH} ...")
    df.to_csv(EXPORT_PATH, index=False)

    print("[EXPORT] Done!")

if __name__ == "__main__":
    main()
