import duckdb

DB_PATH = r"C:/Users/fujai/CardioInsight-AI/cardioinsight_dbt/dev.duckdb"

con = duckdb.connect(DB_PATH)

print(f"Connected to DuckDB at: {DB_PATH}")

tables_df = con.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    ORDER BY table_schema, table_name
""").df()

print("\n=== TABLES IN DATABASE ===")
print(tables_df)

try:
    mart_preview = con.execute("SELECT * FROM main.mart_cardio_risk LIMIT 5").df()
    print("\n=== mart_cardio_risk (first 5 rows) ===")
    print(mart_preview)
except Exception as e:
    print("\n[!] Could not read mart_cardio_risk:")
    print(e)

con.close()
