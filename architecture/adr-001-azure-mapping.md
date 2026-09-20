# ADR-001: Mapping the Local Pipeline to Azure Services

## Status
Proposed for decisions 1-3; decision 4 (ML model deployment) implemented and verified.

## Context
Phases 1-3 were built and validated locally (Python, DuckDB, Power BI,
scikit-learn/FastAPI) to allow fast, cost-free iteration. This ADR defines
how each component would be deployed on Azure in a production setting,
with every service choice constrained to Azure's always-free tier so the
architecture remains genuinely free to run indefinitely, not just during
a trial period.

## Decisions

### 1. Raw/Bronze/Silver/Gold storage
- **Local:** Parquet files on local disk
- **Azure:** Azure Data Lake Storage Gen2 (ADLS Gen2)
- **Rationale:** ADLS Gen2 is the standard for large-scale analytical data
  in Azure - hierarchical namespace (real folder structure, unlike flat
  blob storage), integrates natively with every other Azure analytics
  service, and has an always-free tier (5GB/12 months) suitable for a
  portfolio-scale dataset.
- **Alternative considered:** Azure SQL Database - rejected for the
  bronze/silver layers because Parquet files scale better for large raw
  data and don't require a rigid schema upfront; SQL Database's free tier
  is instead considered later for the gold layer, but ultimately not
  needed (see decision 3).

### 2. Pipeline orchestration (bronze -> silver -> gold scripts)
- **Local:** Python scripts run manually
- **Azure:** Azure Functions (Timer trigger, Consumption plan)
- **Rationale:** Azure Functions' Consumption plan includes an always-free
  grant of 1 million executions/month, which comfortably covers a daily
  or even hourly pipeline run at zero cost, indefinitely - not just during
  a trial period. Each pipeline stage (bronze, silver, gold) becomes its
  own Function, chained together, mirroring the same three Python scripts
  already built and tested locally.
- **Alternative considered:** Azure Data Factory (ADF) - the more common
  enterprise orchestration tool, offering visual pipeline design and
  richer scheduling/monitoring. Rejected here specifically due to cost:
  ADF has no meaningful always-free tier, so any real usage (even minimal)
  starts consuming the trial credit and would incur charges afterward.
  Functions was chosen to keep the architecture genuinely free to run
  long-term, while still demonstrating the same orchestration concept ADF
  would otherwise provide.

### 3. Gold layer / BI consumption
- **Local:** Parquet files queried via DuckDB, loaded into Power BI Desktop
- **Azure:** Gold Parquet files remain in ADLS Gen2; Power BI Desktop
  connects directly to ADLS Gen2 (native connector) rather than to a
  separate database service.
- **Rationale:** Power BI can read Parquet directly from ADLS Gen2 without
  needing an intermediate database, keeping the architecture simpler and
  avoiding any additional service (and cost) purely for BI access. This
  also mirrors exactly what was already proven locally - DuckDB querying
  Parquet directly - just with the storage layer moved to the cloud.
- **Alternative considered:** Azure Synapse Analytics (serverless SQL
  pool) - would allow querying the gold layer with full T-SQL and could
  serve multiple BI tools simultaneously. Rejected for this portfolio-scale
  project since it adds complexity and potential cost without a clear
  benefit over direct Parquet access at this data volume; would be
  reconsidered if the platform needed to serve many concurrent analysts
  or non-Power-BI consumers.

### 4. ML model deployment
- **Local:** FastAPI on localhost
- **Azure:** Azure Functions (HTTP trigger, Consumption plan)
- **Rationale:** Same always-free execution grant as decision #2. An HTTP-
  triggered Function can wrap the trained model exactly like the local
  FastAPI endpoint - the model logic itself barely changes, only the
  hosting mechanism. Using Functions for both orchestration and model
  serving also keeps the architecture consistent and easier to reason
  about, rather than introducing a different compute service for each
  piece.
  - **Status:** Implemented and verified. Deployed to a live Azure Function
  App (Consumption plan, Linux, Python 3.11) at
  `https://bad-review-predictor.azurewebsites.net/api/predict`, tested
  with real requests returning correct predictions.
- **Alternative considered:** Azure Machine Learning (Azure ML) managed
  endpoints - the "proper" enterprise ML deployment service, with built-in
  model versioning, monitoring, and A/B testing support. Rejected here due
  to cost (no meaningful always-free tier for real-time endpoints) and
  complexity that exceeds what this project's scale requires; would be
  the right choice for a team running many models in production with a
  need for formal MLOps practices.

## Consequences

**Positive:**
- Entire architecture runs at $0 ongoing cost using only always-free tier
  services - sustainable as a live portfolio piece indefinitely, not just
  during a trial.
- Consistent compute pattern (Azure Functions) across both orchestration
  and ML serving simplifies the mental model and reduces the number of
  distinct services to operate and secure.
- Direct Parquet access from Power BI avoids unnecessary intermediate
  services at this data scale.

**Trade-offs / limitations accepted:**
- Azure Functions' Consumption plan has a "cold start" delay (the function
  can take a few seconds to wake up if it hasn't run recently) - acceptable
  for a portfolio/demo, but would need a different plan (with cost
  attached) for a latency-sensitive production system.
- Skipping Azure Data Factory and Azure ML means this design doesn't
  demonstrate those specific enterprise tools directly - a trade-off made
  deliberately for cost reasons, and one worth being transparent about if
  asked in an interview ("I chose Functions over ADF specifically to keep
  this free-tier and long-running - in a funded production environment,
  ADF's visual pipelines and richer monitoring would likely be preferable").
- Direct-to-storage Power BI access doesn't scale well to many concurrent
  BI users or non-Power-BI consumers - Synapse would be the upgrade path
  if that need arose.