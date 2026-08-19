"""
Quick sanity check: query the gold layer with SQL to confirm
it's structured correctly and ready for analysis.
"""
import duckdb

con = duckdb.connect()

result = con.execute("""
    SELECT
        c.customer_state,
        COUNT(*) AS num_order_items,
        ROUND(SUM(f.price), 2) AS total_revenue
    FROM 'data_engineering/gold/fact_order_items.parquet' f
    JOIN 'data_engineering/gold/dim_customers.parquet' c
        ON f.customer_id = c.customer_id
    GROUP BY c.customer_state
    ORDER BY total_revenue DESC
    LIMIT 5
""").fetchdf()

print(result)