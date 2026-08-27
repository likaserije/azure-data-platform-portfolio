-- Top revenue-generating product categories (English names)
SELECT
    p.product_category_name_english AS category,
    COUNT(*) AS num_items_sold,
    ROUND(SUM(f.price), 2) AS total_revenue
FROM 'data_engineering/gold/fact_order_items.parquet' f
JOIN 'data_engineering/gold/dim_products.parquet' p
    ON f.product_id = p.product_id
WHERE p.product_category_name_english IS NOT NULL
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;