"""
Simple API wrapping the trained bad-review prediction model.
Run with: uvicorn data_science.api.main:app --reload
Then visit http://127.0.0.1:8000/docs for interactive testing.
"""

import joblib
import pandas as pd
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_DIR = Path("data_science/models")

app = FastAPI(title="Bad Review Prediction API")

# Load the trained model + the exact list of columns it expects, once,
# when the API starts up (not on every request - that would be slow).
model = joblib.load(MODEL_DIR / "bad_review_model.pkl")
feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")


class OrderInput(BaseModel):
    """
    Defines exactly what data the API expects in a request, with types.
    FastAPI uses this to auto-validate incoming requests and reject
    malformed ones automatically, and to generate the docs page.
    """
    delivery_days: float
    days_vs_estimate: float
    total_price: float
    total_freight: float
    num_items: int
    payment_installments: float
    product_category: str


@app.get("/")
def root():
    return {"message": "Bad Review Prediction API is running. Visit /docs to test it."}


@app.post("/predict")
def predict(order: OrderInput):
    # Build a single-row dataframe matching the model's expected input shape
    input_dict = {
        "delivery_days": order.delivery_days,
        "days_vs_estimate": order.days_vs_estimate,
        "total_price": order.total_price,
        "total_freight": order.total_freight,
        "num_items": order.num_items,
        "payment_installments": order.payment_installments,
    }

    # Recreate the one-hot encoded category columns, same as training.
    # Every category column starts at 0, then we set the matching one to 1.
    category_col = f"product_category_name_english_{order.product_category}"
    for col in feature_cols:
        if col.startswith("product_category_name_english_"):
            input_dict[col] = 1 if col == category_col else 0

    input_df = pd.DataFrame([input_dict])

    # Ensure column order exactly matches what the model was trained on
    input_df = input_df.reindex(columns=feature_cols, fill_value=0)

    probability = model.predict_proba(input_df)[0][1]  # probability of "bad review"
    prediction = "Bad review likely" if probability >= 0.5 else "Good review likely"

    return {
        "prediction": prediction,
        "bad_review_probability": round(float(probability), 3)
    }