-- Which states spend the most per order, on average
SELECT
    c.customer_state,
    COUNT(DISTINCT f.order_id) AS num_orders,
    ROUND(SUM(f.price) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value
FROM 'data_engineering/gold/fact_order_items.parquet' f
JOIN 'data_engineering/gold/dim_customers.parquet' c
    ON f.customer_id = c.customer_id
GROUP BY c.customer_state
HAVING COUNT(DISTINCT f.order_id) >= 30  -- ignore states with too few orders to be meaningful
ORDER BY avg_order_value DESC
LIMIT 10;