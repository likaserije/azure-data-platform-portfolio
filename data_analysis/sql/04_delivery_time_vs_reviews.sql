-- Does slower delivery correlate with worse review scores?
SELECT
    CASE
        WHEN delivery_days <= 7 THEN '0-7 days'
        WHEN delivery_days <= 14 THEN '8-14 days'
        WHEN delivery_days <= 21 THEN '15-21 days'
        ELSE '22+ days'
    END AS delivery_bucket,
    CASE
        WHEN delivery_days <= 7 THEN 1
        WHEN delivery_days <= 14 THEN 2
        WHEN delivery_days <= 21 THEN 3
        ELSE 4
    END AS bucket_order,
    COUNT(*) AS num_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score
FROM (
    SELECT
        o.order_id,
        DATE_DIFF('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days,
        r.review_score
    FROM 'data_engineering/silver/olist_orders_dataset.parquet' o
    JOIN 'data_engineering/silver/olist_order_reviews_dataset.parquet' r
        ON o.order_id = r.order_id
    WHERE o.order_delivered_customer_date IS NOT NULL
) sub
GROUP BY delivery_bucket, bucket_order
ORDER BY bucket_order;