# Architecture — Phase 4 (Capstone)

## Overview
This phase maps the locally-built and validated data platform (Phases 1-3)
onto real Azure infrastructure, using only always-free-tier services, and
proves the deployment works with live, verified code - not just a diagram.

## Deliverables
- `adr-001-azure-mapping.md` - Architecture Decision Record documenting
  every Azure service choice, the alternatives considered, and the
  trade-offs accepted.
- `architecture_v1.md` - local pipeline diagram (Phase 1 baseline).
- `architecture_v2.md` - Azure-deployed architecture diagram.
- `scripts/verify_azure_storage.py` - proves live read access to the
  deployed gold layer in Azure Data Lake Storage Gen2.
- `azure_storage_screenshot.png` - visual confirmation of the uploaded
  gold layer in the Azure Portal.

## What was actually deployed (hands-on, not just designed)
- A real Azure Storage Account with hierarchical namespace enabled
  (true ADLS Gen2), created inside the Azure free tier.
- Gold layer Parquet files (`fact_order_items`, `dim_customers`,
  `dim_products`) uploaded and verified as readable directly from the
  cloud via Python - confirmed matching row counts against the local
  version (112,650 rows).

## What was designed but not provisioned (documented, cost-conscious)
- Azure Functions for pipeline orchestration and ML model serving -
  fully specified in the ADR with rationale, using the always-free
  execution grant, but not provisioned in this iteration to keep the
  project scope manageable within the learning timeline.
- Azure Synapse Analytics was evaluated and explicitly rejected in favor
  of direct Parquet access, documented as a scaling decision.

## Full platform summary (all 4 phases)
1. **Data Engineering** - medallion pipeline (bronze/silver/gold), star
   schema, validated with SQL.
2. **Data Analysis** - 5 business questions answered via SQL, interactive
   Power BI dashboard.
3. **Data Science** - bad-review prediction model (Random Forest),
   deployed locally as a FastAPI service.
4. **Architecture** - Azure service mapping via ADR, live deployment and
   verification of the storage layer.

## Key architectural takeaway
Every decision in this project was made under a real constraint - zero
budget - which mirrors a genuine business scenario (a startup or small
team with a limited cloud budget). Each ADR decision explicitly documents
what was traded off to meet that constraint, and what the recommended
next step would be if budget were available (e.g. Data Factory over
Functions, Synapse over direct Parquet access, Azure ML over a custom
FastAPI/Functions deployment).