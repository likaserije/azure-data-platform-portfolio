# Data Engineering — Phase 1

## Overview
Local-first ELT pipeline implementing a medallion architecture (bronze/silver/gold)
on the Olist Brazilian E-Commerce dataset, simulating a retail data platform.

## Pipeline
1. **Bronze** (`01_raw_to_bronze.py`) — raw CSVs converted to Parquet, no transformation.
2. **Silver** (`02_bronze_to_silver.py`) — cleaned: standardized column names,
   removed duplicates, converted date columns, stripped whitespace.
3. **Gold** (`03_silver_to_gold.py`) — joined into a star schema:
   - `fact_order_items` — one row per product purchased (the core business event)
   - `dim_customers`, `dim_products` — descriptive context

## Tech stack
Python, pandas, PyArrow (Parquet), DuckDB (SQL validation)

## Validation
`04_validate_gold.py` runs a sample SQL query against the gold layer to confirm
it's correctly joined and analysis-ready.

## Next steps
Phase 2 (data analysis / BI) and Phase 3 (ML modeling) will consume this gold layer.
Phase 4 will remap this local pipeline onto Azure services (Data Lake, Data Factory/
Databricks) for the cloud-deployed version.