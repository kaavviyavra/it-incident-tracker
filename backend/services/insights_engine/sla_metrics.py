import pandas as pd

def check_sla_breaches(df: pd.DataFrame, sla_col: str, cat_col: str) -> list:
    """Elevates systemic categories exceeding resolution ceilings as problem nodes."""
    issues = []
    if not sla_col or sla_col not in df.columns or len(df) == 0:
        return issues

    try:
        breached_df = df[df[sla_col].astype(str).str.lower().isin(['true', 'yes', 'y', '1'])]
        if len(breached_df) > 0 and cat_col and cat_col in df.columns:
            top_breach_cat = breached_df[cat_col].value_counts().idxmax()
            issues.append({
                "id": "PROB-201",
                "type": "Chronic SLA Breaches",
                "description": f"Repeated SLA breaches observed under category: {top_breach_cat}",
                "frequency": int(len(breached_df)),
                "impacted_priority": "High",
                "sla_status": "Breached"
            })
    except Exception:
        pass
    return issues

def check_reopens(df: pd.DataFrame, reopen_col: str) -> list:
    """Flags systemic high rates of resolution reversion."""
    issues = []
    if not reopen_col or reopen_col not in df.columns or len(df) == 0:
        return issues

    try:
        reopened_df = df[pd.to_numeric(df[reopen_col], errors='coerce') > 1]
        if len(reopened_df) > 0:
            issues.append({
                "id": "PROB-301",
                "type": "Frequent Reopenings",
                "description": "High ticket reopen rate, indicating potential resolution quality issues.",
                "frequency": int(len(reopened_df)),
                "impacted_priority": "Medium",
                "sla_status": "Within SLA"
            })
    except Exception:
        pass
    return issues
