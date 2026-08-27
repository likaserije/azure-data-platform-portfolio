-- Distribution of order outcomes
SELECT
    order_status,
    COUNT(*) AS num_orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM 'data_engineering/silver/olist_orders_dataset.parquet'
GROUP BY order_status
ORDER BY num_orders DESC;