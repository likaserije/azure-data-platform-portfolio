"""
Step: Feature Engineering
Builds a modeling dataset: one row per order, with engineered features
and a binary target (1 = bad review [1-2 stars], 0 = good review [3-5 stars]).
"""

import pandas as pd
from pathlib import Path

SILVER_DIR = Path("data_engineering/silver")
GOLD_DIR = Path("data_engineering/gold")
DS_DIR = Path("data_science/data")
DS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    orders = pd.read_parquet(SILVER_DIR / "olist_orders_dataset.parquet")
    reviews = pd.read_parquet(SILVER_DIR / "olist_order_reviews_dataset.parquet")
    order_items = pd.read_parquet(GOLD_DIR / "fact_order_items.parquet")
    products = pd.read_parquet(GOLD_DIR / "dim_products.parquet")
    payments = pd.read_parquet(SILVER_DIR / "olist_order_payments_dataset.parquet")

    # One review per order (some orders have duplicate review rows -
    # same issue we hit in Power BI - so we aggregate here too)
    reviews_agg = (
        reviews.groupby("order_id")
        .agg(review_score=("review_score", "mean"))
        .reset_index()
    )

    # One row per order (order_items has one row per item - aggregate to order level)
    order_level = (
        order_items.groupby("order_id")
        .agg(
            total_price=("price", "sum"),
            total_freight=("freight_value", "sum"),
            num_items=("order_item_id", "count"),
            product_id=("product_id", "first"),  # for category lookup
        )
        .reset_index()
    )

    # Payments: installments per order (max, in case of split payments)
    payments_agg = (
        payments.groupby("order_id")
        .agg(payment_installments=("payment_installments", "max"))
        .reset_index()
    )

    # Merge everything onto orders
    df = orders.merge(order_level, on="order_id", how="inner")
    df = df.merge(payments_agg, on="order_id", how="left")
    df = df.merge(reviews_agg, on="order_id", how="inner")  # inner: need a review to have a target
    df = df.merge(
        products[["product_id", "product_category_name_english"]],
        on="product_id", how="left"
    )

    # Only orders that were actually delivered have a meaningful delivery time
    df = df[df["order_delivered_customer_date"].notna()]

    # Feature: actual delivery time in days
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # Feature: how many days early/late vs. the estimate (negative = early, positive = late)
    df["days_vs_estimate"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    # Target: 1 if review was 1 or 2 stars, else 0
    df["bad_review"] = (df["review_score"] <= 2).astype(int)

    # Final feature set
    feature_cols = [
        "order_id", "delivery_days", "days_vs_estimate", "total_price",
        "total_freight", "num_items", "payment_installments",
        "product_category_name_english", "bad_review"
    ]
    final_df = df[feature_cols].dropna(subset=[
        "delivery_days", "days_vs_estimate", "total_price", "total_freight"
    ])

    output_path = DS_DIR / "modeling_dataset.parquet"
    final_df.to_parquet(output_path, index=False)

    print(f"Final modeling dataset: {len(final_df):,} rows")
    print(f"Bad review rate: {final_df['bad_review'].mean():.2%}")
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()