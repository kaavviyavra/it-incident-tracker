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
    # Apply AI Defaults for Missing Core Fields
    # -----------------------------
    try:
        from services.local_ai.semantic_similarity import classify_texts_zero_shot
        
        # Locate description column safely
        desc_col = next((c for c in ["Description", "description", "Short_Description", "Short Description", "Short description"] if c in df.columns), None)
        if not desc_col:
            desc_col = next((c for c in df.columns if "desc" in str(c).lower() or "short" in str(c).lower()), None)
            
        if desc_col and len(df) > 0:
            # We process unique descriptions only to save massive amounts of time (runs in seconds)
            unique_descs = df[desc_col].astype(str).unique().tolist()
            
            # Predict AI_Category if no known category maps exist
            if not any(c in df.columns for c in ["Category", "category", "Company", "Request For", "Account/Department"]):
                generic_categories = ["Network & Connectivity", "Hardware & Equipment", "Software Application", "Database & Data", "Access & Identity", "General Service Request"]
                predictions = classify_texts_zero_shot(unique_descs, generic_categories)
                desc_to_cat = dict(zip(unique_descs, predictions))
                df["AI_Category"] = df[desc_col].astype(str).map(desc_to_cat)

            # Predict AI_Priority if no known priority/state maps exist
            if not any(c in df.columns for c in ["Priority", "priority", "State", "severity", "urgency"]):
                generic_priorities = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
                label_context = [
                    "Critical System Failure or Outage affecting many", 
                    "High Priority Issue", 
                    "Medium Priority standard operational issue", 
                    "Low Priority minor request or question"
                ]
                predictions_context = classify_texts_zero_shot(unique_descs, label_context)
                
                context_to_prio = dict(zip(label_context, generic_priorities))
                desc_to_prio = {desc: context_to_prio[pred] for desc, pred in zip(unique_descs, predictions_context)}
                df["AI_Priority"] = df[desc_col].astype(str).map(desc_to_prio)
    except Exception as e:
        print(f"Skipped local AI column auto-generation: {e}")

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