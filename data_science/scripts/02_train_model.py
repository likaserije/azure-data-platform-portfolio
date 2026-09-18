"""
Step: Train a classifier to predict bad reviews (1-2 stars).
Uses a Random Forest - handles mixed numeric/categorical features well,
and gives us interpretable feature importances for free.
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

DATA_PATH = Path("data_science/data/modeling_dataset.parquet")
MODEL_DIR = Path("data_science/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_parquet(DATA_PATH)

    # One-hot encode the categorical feature (product category) -
    # models need numbers, not text categories, so each category
    # becomes its own 0/1 column.
    df = pd.get_dummies(df, columns=["product_category_name_english"], dummy_na=True)

    feature_cols = [c for c in df.columns if c not in ("order_id", "bad_review")]
    X = df[feature_cols]
    y = df["bad_review"]

    # Split: 80% to train on, 20% held back to test on unseen data.
    # stratify=y keeps the same 12.77% bad-review ratio in both splits -
    # important for imbalanced data, so the test set is representative.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # class_weight="balanced" tells the model to pay more attention to
    # the minority class (bad reviews) during training, countering the
    # imbalance instead of letting it default to "always predict good."
    model = RandomForestClassifier(
        n_estimators=200, max_depth=10, class_weight="balanced",
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["Good review", "Bad review"]))

    print("=== Confusion Matrix ===")
    print("           Predicted Good  Predicted Bad")
    cm = confusion_matrix(y_test, y_pred)
    print(f"Actual Good      {cm[0][0]:>6}         {cm[0][1]:>6}")
    print(f"Actual Bad       {cm[1][0]:>6}         {cm[1][1]:>6}")

    # Feature importance: which signals mattered most to the model
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    print("\n=== Top 10 Most Important Features ===")
    print(importances.sort_values(ascending=False).head(10))

    joblib.dump(model, MODEL_DIR / "bad_review_model.pkl")
    joblib.dump(feature_cols, MODEL_DIR / "feature_columns.pkl")
    print(f"\nModel saved to {MODEL_DIR}")


if __name__ == "__main__":
    main()