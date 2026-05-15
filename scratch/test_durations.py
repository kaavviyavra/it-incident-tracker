import pandas as pd
import numpy as np

def calculate_resolution_performance(df: pd.DataFrame, priority_col: str, resolution_col: str, date_col: str = None) -> dict:
    performance = {}
    if not priority_col or not resolution_col or len(df) == 0:
        return performance
        
    if priority_col not in df.columns or resolution_col not in df.columns:
        return performance

    try:
        df_copy = df.copy()
        target_col = 'computed_duration_hours'
        
        # Step 1: Determine if the column is likely numeric or datetime
        # If it is float/int, it's numerical hours.
        is_numeric = pd.api.types.is_numeric_dtype(df_copy[resolution_col])
        is_datetime = pd.api.types.is_datetime64_any_dtype(df_copy[resolution_col])
        
        # If it is object/string, attempt to infer
        if not is_numeric and not is_datetime:
            # Check if sample parses to numeric
            sample = df_copy[resolution_col].dropna().head(10)
            if len(sample) > 0:
                try:
                    pd.to_numeric(sample, errors='raise')
                    is_numeric = True
                except Exception:
                    # If not numeric, test if it parses to datetime
                    try:
                        pd.to_datetime(sample, errors='raise')
                        is_datetime = True
                    except Exception:
                        pass

        # Step 2: Perform parsing logic
        if is_datetime and date_col and date_col in df_copy.columns:
            print("Detected timestamp-based resolution. Computing duration from Opened date.")
            start = pd.to_datetime(df_copy[date_col], errors='coerce')
            end = pd.to_datetime(df_copy[resolution_col], errors='coerce')
            df_copy[target_col] = (end - start).dt.total_seconds() / 3600.0
        else:
            print("Detected pre-computed numeric resolution.")
            df_copy[target_col] = pd.to_numeric(df_copy[resolution_col], errors='coerce')
            
        # Step 3: Clean results to avoid huge NaT numbers or Unix overflows
        # Extreme maximum boundary: 100,000 hours ≈ 11 years.
        # Min boundary: 0 hours.
        valid_rows = (
            df_copy[target_col].notna() & 
            (df_copy[target_col] >= 0) & 
            (df_copy[target_col] < 100000)
        )
        df_clean = df_copy[valid_rows]
        
        if len(df_clean) > 0:
            avg_res = df_clean.groupby(priority_col)[target_col].mean().dropna().to_dict()
            performance = {str(k): float(round(v, 2)) for k, v in avg_res.items()}
            
    except Exception as e:
        print(f"Resolution Performance Calculation Error: {e}")
        
    return performance

# Verify on all three cases now:
df1 = pd.DataFrame({
    'Priority': ['High', 'Low', 'High', 'Medium'],
    'Resolution': [2.5, 10.0, 1.5, -5.0], # Note: -5 should be filtered out
})
print("Test 1 Res:", calculate_resolution_performance(df1, 'Priority', 'Resolution'))

df2 = pd.DataFrame({
    'Priority': ['High', 'High', 'Medium'],
    'Opened': ['2023-10-20 08:00:00', '2023-10-20 10:00:00', '2023-10-20 12:00:00'],
    'Resolved': ['2023-10-20 10:30:00', '2023-10-20 11:00:00', '2023-10-20 13:00:00'], # 2.5 hrs, 1.0 hr, 1.0 hr
})
print("Test 2 Res:", calculate_resolution_performance(df2, 'Priority', 'Resolved', 'Opened'))

df3 = pd.DataFrame({
    'Priority': ['High', 'Low'],
    'Resolution': [-6343615793011272000, 1698782131], # Extremely massive and negative, should result in empty
})
print("Test 3 Res:", calculate_resolution_performance(df3, 'Priority', 'Resolution'))
