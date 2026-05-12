import io
from datetime import datetime

import pandas as pd


def process_batch_file(file_content, filename, mapping=None):
    """
    Process uploaded ticket dump file (Excel/CSV)
    without AI classification.

    Keeps original ticket data intact and prepares
    it for analytics/insight generation.
    """

    # -----------------------------
    # Read File
    # -----------------------------
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_content))
    else:
        df = pd.read_excel(io.BytesIO(file_content))

    # -----------------------------
    # Validate File
    # -----------------------------
    if df.empty:
        raise ValueError("Uploaded file is empty.")

    # -----------------------------
    # Standardize Columns
    # -----------------------------
    df.columns = [col.strip() for col in df.columns]

    # -----------------------------
    # Apply Column Mapping
    # -----------------------------
    if mapping:
        reverse_mapping = {
            v: k for k, v in mapping.items()
            if v in df.columns
        }

        df.rename(columns=reverse_mapping, inplace=True)

    # -----------------------------
    # Add Processing Metadata
    # -----------------------------
    df["Processed_At"] = datetime.now().isoformat()

    df["Processing_Status"] = "SUCCESS"

    # -----------------------------
    # Basic Cleanup
    # -----------------------------
    df = df.astype(object).fillna("")

    # -----------------------------
    # Export Processed File
    # -----------------------------
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return output