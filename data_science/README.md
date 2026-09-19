# Data Science — Phase 3

## Overview
A binary classification model predicting whether an order will receive a
bad review (1-2 stars), trained on engineered features from the Phase 1
gold layer. Deployed as a local API for real-time predictions.

## Problem framing
- **Target:** bad_review (1 = review score of 1-2 stars, 0 = 3-5 stars)
- **Class imbalance:** ~12.8% of orders receive a bad review - handled with
  `class_weight="balanced"` rather than naive accuracy optimization.

## Features
| Feature | Rationale |
|---|---|
| delivery_days | Proven correlated with satisfaction in Phase 2 analysis |
| days_vs_estimate | Captures broken promises, not just raw speed |
| total_price / total_freight | Higher-stakes orders may raise expectations |
| num_items | Order complexity |
| payment_installments | Proxy for purchase consideration |
| product_category | Some categories may have inherently different complaint rates |

## Model
Random Forest Classifier (scikit-learn), 200 trees, max depth 10.

## Results
- Recall (bad review): 0.54 - catches just over half of true bad-review orders
- Precision (bad review): 0.36 - about 1 in 3 flagged orders are true positives
- Top features: days_vs_estimate (42%) and delivery_days (31%) dominate,
  directly confirming the Phase 2 SQL finding that delivery timing drives
  customer satisfaction.

## Deployment
`api/main.py` - FastAPI service exposing a `/predict` endpoint. Run locally with: