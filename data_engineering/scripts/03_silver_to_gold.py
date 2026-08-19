"""
Step: Silver -> Gold
Joins cleaned tables into a star schema: one fact table (order line items,
the "events" in this business) plus dimension tables (customers, products) -
the descriptive context around each event. Gold = ready for BI/ML.
"""

import pandas as pd
from pathlib import Path

SILVER_DIR = Path("data_engineering/silver")
GOLD_DIR = Path("data_engineering/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)


def load(table_name: str) -> pd.DataFrame:
    return pd.read_parquet(SILVER_DIR / f"{table_name}.parquet")


def build_fact_order_items():
    """
    One row per product purchased within an order - the core 'event'
    of this business. Joins order_items with orders (for dates/status)
    and payments (for how it was paid).
    """
    order_items = load("olist_order_items_dataset")
    orders = load("olist_orders_dataset")
    payments = load("olist_order_payments_dataset")

    # Payments can have multiple rows per order (split payments) -
    # aggregate to one row per order before joining, so we don't
    # accidentally duplicate order_items rows.
    payments_agg = (
        payments.groupby("order_id")
        .agg(total_payment_value=("payment_value", "sum"),
             payment_type=("payment_type", "first"))
        .reset_index()
    )

    fact = order_items.merge(
        orders[["order_id", "customer_id", "order_status",
                "order_purchase_timestamp", "order_delivered_customer_date"]],
        on="order_id", how="left"
    ).merge(
        payments_agg, on="order_id", how="left"
    )

    return fact


def build_dim_customers():
    customers = load("olist_customers_dataset")
    return customers.drop_duplicates(subset="customer_id")


def build_dim_products():
    products = load("olist_products_dataset")
    translation = load("product_category_name_translation")

    dim = products.merge(translation, on="product_category_name", how="left")
    return dim.drop_duplicates(subset="product_id")


def main():
    print("Building fact_order_items...")
    fact = build_fact_order_items()
    fact.to_parquet(GOLD_DIR / "fact_order_items.parquet", index=False)
    print(f"  -> {len(fact):,} rows saved.\n")

    print("Building dim_customers...")
    dim_customers = build_dim_customers()
    dim_customers.to_parquet(GOLD_DIR / "dim_customers.parquet", index=False)
    print(f"  -> {len(dim_customers):,} rows saved.\n")

    print("Building dim_products...")
    dim_products = build_dim_products()
    dim_products.to_parquet(GOLD_DIR / "dim_products.parquet", index=False)
    print(f"  -> {len(dim_products):,} rows saved.\n")

    print("Done. Gold layer ready for analysis and modeling.")


if __name__ == "__main__":
    main()