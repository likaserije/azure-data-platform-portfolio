import azure.functions as func
import logging
import json
import joblib
import pandas as pd
from pathlib import Path

app = func.FunctionApp()

MODEL_DIR = Path(__file__).parent / "models"
model = joblib.load(MODEL_DIR / "bad_review_model.pkl")
feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")


@app.route(route="predict", auth_level=func.AuthLevel.ANONYMOUS)
def predict(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Predict function triggered.")

    try:
        order = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid or missing JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    input_dict = {
        "delivery_days": order.get("delivery_days"),
        "days_vs_estimate": order.get("days_vs_estimate"),
        "total_price": order.get("total_price"),
        "total_freight": order.get("total_freight"),
        "num_items": order.get("num_items"),
        "payment_installments": order.get("payment_installments"),
    }

    category = order.get("product_category", "")
    category_col = f"product_category_name_english_{category}"
    for col in feature_cols:
        if col.startswith("product_category_name_english_"):
            input_dict[col] = 1 if col == category_col else 0

    input_df = pd.DataFrame([input_dict])
    input_df = input_df.reindex(columns=feature_cols, fill_value=0)

    probability = model.predict_proba(input_df)[0][1]
    prediction = "Bad review likely" if probability >= 0.5 else "Good review likely"

    result = {
        "prediction": prediction,
        "bad_review_probability": round(float(probability), 3)
    }

    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json"
    )