-- Monthly revenue trend
SELECT
    strftime(order_purchase_timestamp, '%Y-%m') AS year_month,
    COUNT(DISTINCT order_id) AS num_orders,
    ROUND(SUM(price), 2) AS total_revenue
FROM 'data_engineering/gold/fact_order_items.parquet'
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY year_month
ORDER BY year_month;