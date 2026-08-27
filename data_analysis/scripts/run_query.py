"""
Runs a .sql file against the gold layer using DuckDB and prints the result.
Usage: python data_analysis/scripts/run_query.py data_analysis/sql/01_monthly_revenue.sql
"""
import sys
import duckdb

if len(sys.argv) != 2:
    print("Usage: python run_query.py <path_to_sql_file>")
    sys.exit(1)

sql_path = sys.argv[1]
with open(sql_path, "r") as f:
    query = f.read()

con = duckdb.connect()
result = con.execute(query).fetchdf()
print(result.to_string(index=False))