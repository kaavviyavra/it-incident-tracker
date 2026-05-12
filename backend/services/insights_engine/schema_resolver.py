import pandas as pd

def resolve_columns(df: pd.DataFrame, mapping: dict = None) -> dict:
    """
    Dynamically scans DataFrame headers against known naming conventions and 
    custom mappings to normalize metric collection points.
    """
    mapping = mapping or {}
    resolved = {}

    # Category Mapping
    cat_col = next((c for c in ["Category", "AI_Category", "category"] if c in df.columns), None)
    if not cat_col:
        mapped_cat = mapping.get("Category")
        if mapped_cat in df.columns:
            cat_col = mapped_cat
        else:
            cat_col = next((c for c in df.columns if "cat" in str(c).lower() or "type" in str(c).lower()), None)
    resolved["category"] = cat_col

    # Description Mapping
    desc_col = next((c for c in ["Description", "description", "Short_Description"] if c in df.columns), None)
    if not desc_col:
        mapped_desc = mapping.get("Description")
        if mapped_desc in df.columns:
            desc_col = mapped_desc
        else:
            desc_col = next((c for c in df.columns if "desc" in str(c).lower() or "short" in str(c).lower() or "subject" in str(c).lower()), None)
    resolved["description"] = desc_col

    # Subcategory Mapping
    sub_col = next((c for c in ["Subcategory", "AI_Subcategory", "subcategory"] if c in df.columns), None)
    if not sub_col:
        mapped_sub = mapping.get("Subcategory")
        if mapped_sub in df.columns:
            sub_col = mapped_sub
    resolved["subcategory"] = sub_col

    # Assignment Group Mapping
    grp_col = next((c for c in ["Assignment_Group", "Assignment Group", "assignment_group"] if c in df.columns), None)
    if not grp_col:
        mapped_grp = mapping.get("Assignment_Group")
        if mapped_grp in df.columns:
            grp_col = mapped_grp
    resolved["assignment_group"] = grp_col

    # Base system columns
    resolved["priority"] = next((c for c in ["Priority", "priority", "AI_Priority"] if c in df.columns), None)
    
    # Date resolution logic excluding upload timestamps
    date_col = next((c for c in df.columns if any(sub in str(c).lower() for sub in ["created", "opened", "incident_date", "incident date", "timestamp", "date"]) and str(c) != "Processed_At"), None)
    if not date_col:
        date_col = next((c for c in ["Created", "Created_At", "Opened", "Opened_At", "date", "createdAt"] if c in df.columns), None) or next((c for c in ["Processed_At"] if c in df.columns), None)
    resolved["date"] = date_col

    resolved["resolution"] = next((c for c in ["Resolution_Time", "duration", "resolve_time", "resolution_time"] if c in df.columns), None)
    resolved["sla_breach"] = next((c for c in ["SLA_Breached", "sla_breached", "breached", "SLA"] if c in df.columns), None)
    resolved["reopen"] = next((c for c in ["Reopen_Count", "reopen_count", "reopened", "reopens"] if c in df.columns), None)

    return resolved
