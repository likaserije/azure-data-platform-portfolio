"""
Step: Visualize one decision tree from the trained Random Forest.
This shows the actual, human-readable rules the model learned -
useful for understanding (and explaining) how it makes decisions.
"""

import joblib
from pathlib import Path
from sklearn.tree import export_text, plot_tree
import matplotlib.pyplot as plt

MODEL_DIR = Path("data_science/models")

model = joblib.load(MODEL_DIR / "bad_review_model.pkl")
feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")

# Pull out just ONE tree from the forest of 200 - e.g. the very first one
single_tree = model.estimators_[0]

# --- Option A: text version, printed to console (easiest to read) ---
# max_depth=3 here just limits how much we print - the real tree goes
# deeper (up to 10, from training), but the first few splits are the
# most important/general ones.
tree_text = export_text(single_tree, feature_names=feature_cols, max_depth=3)
print("=== First few levels of Tree #1 (of 200) ===\n")
print(tree_text)

# --- Option B: visual diagram, saved as an image ---
plt.figure(figsize=(20, 10))
plot_tree(
    single_tree,
    feature_names=feature_cols,
    class_names=["Good review", "Bad review"],
    filled=True,
    max_depth=3,   # same depth limit, so the image stays readable
    fontsize=8
)
output_path = "data_science/models/tree_visualization.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"\nTree diagram saved to {output_path}")