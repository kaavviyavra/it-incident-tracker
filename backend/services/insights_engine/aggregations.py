import pandas as pd

def calculate_distributions(df: pd.DataFrame, cols: dict) -> dict:
    """Compiles basic counts across categories, subcategories, groups, priorities and status."""
    dist = {
        "categories": {},
        "subcategories": {},
        "assignment_groups": {},
        "priority_distribution": {},
        "status_distribution": {}
    }
    
    if len(df) == 0:
        return dist
        
    mapping = {
        "categories": cols.get("category"),
        "subcategories": cols.get("subcategory"),
        "assignment_groups": cols.get("assignment_group"),
        "priority_distribution": cols.get("priority"),
        "status_distribution": cols.get("status")
    }
    
    for key, target_col in mapping.items():
        if target_col and target_col in df.columns:
            dist[key] = {str(k): int(v) for k, v in df[target_col].value_counts().dropna().to_dict().items()}
            
    return dist

def calculate_resolution_performance(df: pd.DataFrame, priority_col: str, resolution_col: str, date_col: str = None) -> dict:
    """
    Correlates priority tiers against duration averages. Intelligently intercepts
    timestamps to calculate dynamic intervals and sanitizes against huge negative/epoch durations.
    """
    performance = {}
    if not priority_col or not resolution_col or len(df) == 0:
        return performance
        
    if priority_col not in df.columns or resolution_col not in df.columns:
        return performance

    try:
        df_copy = df.copy()
        target_col = 'computed_duration_hours'
        
        # Determine if resolution_col contains datetimes or pre-computed numbers
        is_numeric = pd.api.types.is_numeric_dtype(df_copy[resolution_col])
        is_datetime = pd.api.types.is_datetime64_any_dtype(df_copy[resolution_col])
        
        if not is_numeric and not is_datetime:
            # Run non-destructive sample check on object arrays
            sample = df_copy[resolution_col].dropna().head(10)
            if len(sample) > 0:
                try:
                    pd.to_numeric(sample, errors='raise')
                    is_numeric = True
                except Exception:
                    try:
                        pd.to_datetime(sample, errors='raise')
                        is_datetime = True
                    except Exception:
                        pass
                        
        # Process based on identified layout
        if is_datetime and date_col and date_col in df_copy.columns:
            start = pd.to_datetime(df_copy[date_col], errors='coerce')
            end = pd.to_datetime(df_copy[resolution_col], errors='coerce')
            df_copy[target_col] = (end - start).dt.total_seconds() / 3600.0
        else:
            df_copy[target_col] = pd.to_numeric(df_copy[resolution_col], errors='coerce')
            
        # Prevent epoch artifacts / extreme floats / negative durations (NaT converts to negative mins)
        # High threshold: 100,000 hours (~11 years) is safe guardrail for real operations
        valid_filter = (
            df_copy[target_col].notna() & 
            (df_copy[target_col] >= 0) & 
            (df_copy[target_col] < 100000)
        )
        df_clean = df_copy[valid_filter]
        
        if len(df_clean) > 0:
            avg_res = df_clean.groupby(priority_col)[target_col].mean().dropna().to_dict()
            performance = {str(k): float(round(v, 2)) for k, v in avg_res.items()}
    except Exception:
        pass
            
    return performance
