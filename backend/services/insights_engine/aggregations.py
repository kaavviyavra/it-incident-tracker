import pandas as pd

def calculate_distributions(df: pd.DataFrame, cols: dict) -> dict:
    """Compiles basic counts across categories, subcategories, groups and priorities."""
    dist = {
        "categories": {},
        "subcategories": {},
        "assignment_groups": {},
        "priority_distribution": {}
    }
    
    if len(df) == 0:
        return dist
        
    mapping = {
        "categories": cols.get("category"),
        "subcategories": cols.get("subcategory"),
        "assignment_groups": cols.get("assignment_group"),
        "priority_distribution": cols.get("priority")
    }
    
    for key, target_col in mapping.items():
        if target_col and target_col in df.columns:
            dist[key] = {str(k): int(v) for k, v in df[target_col].value_counts().dropna().to_dict().items()}
            
    return dist

def calculate_resolution_performance(df: pd.DataFrame, priority_col: str, resolution_col: str) -> dict:
    """Correlates priority tiers against duration averages."""
    performance = {}
    if not priority_col or not resolution_col or len(df) == 0:
        return performance
        
    if priority_col in df.columns and resolution_col in df.columns:
        try:
            temp_res = pd.to_numeric(df[resolution_col], errors='coerce')
            valid_res = temp_res.notna()
            if valid_res.any():
                df_res = df[valid_res].copy()
                df_res[resolution_col] = temp_res[valid_res]
                avg_res = df_res.groupby(priority_col)[resolution_col].mean().dropna().to_dict()
                performance = {str(k): float(round(v, 2)) for k, v in avg_res.items()}
        except Exception:
            pass
            
    return performance
