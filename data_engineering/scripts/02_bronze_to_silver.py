"""
Step: Bronze -> Silver
Cleans raw data: fixes data types, removes duplicates, handles nulls,
standardizes column names. Silver = trustworthy, analysis-ready data
(but not yet joined/aggregated - that's gold).
"""

import pandas as pd
from pathlib import Path

BRONZE_DIR = Path("data_engineering/bronze")
SILVER_DIR = Path("data_engineering/silver")
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# Columns that look like dates based on their name (common naming pattern
# in this dataset - anything with "date" or "timestamp" in it)
DATE_KEYWORDS = ["date", "timestamp"]


def clean_generic(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Apply cleaning rules that make sense for every table."""

    before_rows = len(df)

    # 1. Standardize column names: lowercase, no leading/trailing spaces
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. Remove fully duplicate rows
    df = df.drop_duplicates()

    # 3. Auto-detect and convert date-like columns from text to real dates
    for col in df.columns:
        if any(keyword in col for keyword in DATE_KEYWORDS):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 4. Strip whitespace from text columns (common source of "duplicate"
    #    categories like "Sao Paulo" vs "Sao Paulo ")
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    after_rows = len(df)
    dropped = before_rows - after_rows
    if dropped > 0:
        print(f"  -> Removed {dropped} duplicate rows")

    return df


def main():
    parquet_files = list(BRONZE_DIR.glob("*.parquet"))
    print(f"Found {len(parquet_files)} bronze tables to clean.\n")

    for path in parquet_files:
        table_name = path.stem
        df = pd.read_parquet(path)

        print(f"Cleaning {table_name} ({len(df):,} rows)...")
        df_clean = clean_generic(df, table_name)

        output_path = SILVER_DIR / f"{table_name}.parquet"
        df_clean.to_parquet(output_path, index=False)
        print(f"  -> Saved {len(df_clean):,} rows to {output_path}\n")

    print("Done. All tables cleaned and saved to silver layer.")


if __name__ == "__main__":
    main()