"""
Proves the Azure Data Lake Storage account is real and reachable:
connects to it, lists what's in the gold/ folder, and reads one
Parquet file's row count directly from the cloud (not local disk).
"""

import os
import io
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()  # reads variables from your local .env file

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "data-platform"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

print("=== Files found in Azure Storage (gold/ folder) ===")
blobs = list(container_client.list_blobs(name_starts_with="gold/"))
for blob in blobs:
    size_kb = blob.size / 1024
    print(f"  {blob.name}  ({size_kb:.1f} KB)")

print("\n=== Reading one file directly from the cloud ===")
blob_client = container_client.get_blob_client("gold/fact_order_items.parquet")
downloaded = blob_client.download_blob().readall()

df = pd.read_parquet(io.BytesIO(downloaded))
print(f"fact_order_items.parquet read from Azure: {len(df):,} rows")
print(df.head(3))