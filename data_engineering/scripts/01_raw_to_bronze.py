"""
Step: Raw -> Bronze
Reads all raw CSV files and writes them out as Parquet files,
with zero transformation. Bronze = faithful copy of the source.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data_engineering/raw_data")
BRONZE_DIR = Path("data_engineering/bronze")

BRONZE_DIR.mkdir(parents=True, exist_ok=True)

csv_files = list(RAW_DIR.glob("*.csv"))
print(f"Found {len(csv_files)} CSV files to process.\n")

for csv_path in csv_files:
    table_name = csv_path.stem  # filename without .csv
    df = pd.read_csv(csv_path)

    output_path = BRONZE_DIR / f"{table_name}.parquet"
    df.to_parquet(output_path, index=False)

    print(f"{table_name}: {len(df):,} rows -> {output_path}")

print("\nDone. Raw data copied to bronze layer as Parquet.")