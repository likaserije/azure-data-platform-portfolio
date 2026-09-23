"""
Step: Batch scoring for new orders.
Simulates a batch of newly-delivered orders arriving, applies the exact
same feature engineering used during training, and scores them with the
saved model - producing a predictions file ready for a business system
(e.g. flagging at-risk orders for customer service).
"""

import pandas as pd
import joblib
from pathlib import Path

SILVER_DIR = Path("data_engineering/silver")
GOLD_DIR = Path("data_engineering/gold")
MODEL_DIR = Path("data_science/models")
OUTPUT_DIR = Path("data_science/predictions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_features_for_new_orders(order_ids: list[str]) -> pd.DataFrame:
    """
    Rebuilds the exact same features as 01_feature_engineering.py,
    but only for a specific set of order_ids - simulating "new" orders
    that just need scoring, not a full historical rebuild.
    """
    orders = pd.read_parquet(SILVER_DIR / "olist_orders_dataset.parquet")
    order_items = pd.read_parquet(GOLD_DIR / "fact_order_items.parquet")
    products = pd.read_parquet(GOLD_DIR / "dim_products.parquet")
    payments = pd.read_parquet(SILVER_DIR / "olist_order_payments_dataset.parquet")

    # Filter down to just the "new" orders we're scoring
    orders = orders[orders["order_id"].isin(order_ids)]
    order_items = order_items[order_items["order_id"].isin(order_ids)]

    order_level = (
        order_items.groupby("order_id")
        .agg(
            total_price=("price", "sum"),
            total_freight=("freight_value", "sum"),
            num_items=("order_item_id", "count"),
            product_id=("product_id", "first"),
        )
        .reset_index()
    )

    payments_agg = (
        payments[payments["order_id"].isin(order_ids)]
        .groupby("order_id")
        .agg(payment_installments=("payment_installments", "max"))
        .reset_index()
    )

    df = orders.merge(order_level, on="order_id", how="inner")
    df = df.merge(payments_agg, on="order_id", how="left")
    df = df.merge(
        products[["product_id", "product_category_name_english"]],
        on="product_id", how="left"
    )

    df = df[df["order_delivered_customer_date"].notna()]

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days
    df["days_vs_estimate"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    feature_cols = [
        "order_id", "delivery_days", "days_vs_estimate", "total_price",
        "total_freight", "num_items", "payment_installments",
        "product_category_name_english"
    ]
    return df[feature_cols].dropna(subset=[
        "delivery_days", "days_vs_estimate", "total_price", "total_freight"
    ])


def main():
    # --- Simulate "new" orders: sample 20 random real orders ---
    all_orders = pd.read_parquet(SILVER_DIR / "olist_orders_dataset.parquet")
    new_order_ids = (
        all_orders[all_orders["order_delivered_customer_date"].notna()]
        ["order_id"].sample(20, random_state=7).tolist()
    )
    print(f"Simulating {len(new_order_ids)} newly-delivered orders to score...\n")

    # --- Apply the same feature engineering as training ---
    new_df = build_features_for_new_orders(new_order_ids)

    # --- Load the trained model + its expected columns ---
    model = joblib.load(MODEL_DIR / "bad_review_model.pkl")
    feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")

    # --- One-hot encode categories, same way as training ---
    scoring_df = pd.get_dummies(
        new_df, columns=["product_category_name_english"], dummy_na=True
    )

    # --- CRITICAL: align columns to exactly match training.
    # New data may be missing some category columns (if none of these
    # 20 orders happen to be, say, "furniture"), and reindex fills those
    # missing columns with 0 - this is exactly the training/serving skew
    # risk mentioned earlier, handled correctly here. ---
    X_new = scoring_df.reindex(columns=feature_cols, fill_value=0)

    # --- Predict ---
    probabilities = model.predict_proba(X_new)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    results = pd.DataFrame({
        "order_id": new_df["order_id"].values,
        "bad_review_probability": probabilities.round(3),
        "predicted_bad_review": predictions
    }).sort_values("bad_review_probability", ascending=False)

    output_path = OUTPUT_DIR / "new_order_predictions.parquet"
    results.to_parquet(output_path, index=False)

    print("=== Scored Orders (highest risk first) ===")
    print(results.to_string(index=False))
    print(f"\nSaved to {output_path}")
    print(f"\n{predictions.sum()} of {len(predictions)} orders flagged as at-risk of a bad review.")


if __name__ == "__main__":
    main()