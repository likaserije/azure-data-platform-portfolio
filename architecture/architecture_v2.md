# Architecture v2 — Azure Deployment

## Diagram

```mermaid
flowchart LR
    A[Raw CSVs] --> B[ADLS Gen2<br/>Bronze]
    B -->|Azure Function<br/>Timer trigger| C[ADLS Gen2<br/>Silver]
    C -->|Azure Function<br/>Timer trigger| D[ADLS Gen2<br/>Gold]
    D --> E[Power BI<br/>Direct Parquet connector]
    D --> F[Azure Function<br/>HTTP trigger<br/>ML model serving]
```

## Notes
See `adr-001-azure-mapping.md` for full rationale behind each service choice.
This v2 diagram maps directly onto the local v1 medallion pipeline - same 
logical flow, cloud-hosted compute and storage.