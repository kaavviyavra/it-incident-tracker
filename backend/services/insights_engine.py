import pandas as pd

def generate_full_insights(df: pd.DataFrame, mapping: dict = None, start_date: str = None, end_date: str = None) -> dict:
    """
    Generates rich, schema-flexible analytical insights and AIOps metrics from the batch dataframe.
    Respects custom column mapping and handles missing columns gracefully with safe fallbacks.
    """
    mapping = mapping or {}
    
    # 1. Resolve columns from dynamic mapping or fallbacks
    # 1. Resolve columns safely, prioritizing standardized names (or fallbacks) if already renamed
    cat_col = next((c for c in ["Category", "AI_Category", "category"] if c in df.columns), None)
    if not cat_col:
        mapped_cat = mapping.get("Category")
        if mapped_cat in df.columns:
            cat_col = mapped_cat
        else:
            cat_col = next((c for c in df.columns if "cat" in str(c).lower() or "type" in str(c).lower()), None)

    desc_col = next((c for c in ["Description", "description", "Short_Description"] if c in df.columns), None)
    if not desc_col:
        mapped_desc = mapping.get("Description")
        if mapped_desc in df.columns:
            desc_col = mapped_desc
        else:
            desc_col = next((c for c in df.columns if "desc" in str(c).lower() or "short" in str(c).lower() or "subject" in str(c).lower()), None)

    sub_col = next((c for c in ["Subcategory", "AI_Subcategory", "subcategory"] if c in df.columns), None)
    if not sub_col:
        mapped_sub = mapping.get("Subcategory")
        if mapped_sub in df.columns:
            sub_col = mapped_sub

    grp_col = next((c for c in ["Assignment_Group", "Assignment Group", "assignment_group"] if c in df.columns), None)
    if not grp_col:
        mapped_grp = mapping.get("Assignment_Group")
        if mapped_grp in df.columns:
            grp_col = mapped_grp
    
    priority_col = next((c for c in ["Priority", "priority", "AI_Priority"] if c in df.columns), None)
    # Prioritize actual dataset date columns (ignoring the upload metadata timestamp 'Processed_At')
    date_col = next((c for c in df.columns if any(sub in str(c).lower() for sub in ["created", "opened", "incident_date", "incident date", "timestamp", "date"]) and str(c) != "Processed_At"), None)
    if not date_col:
        date_col = next((c for c in ["Created", "Created_At", "Opened", "Opened_At", "date", "createdAt"] if c in df.columns), None) or next((c for c in ["Processed_At"] if c in df.columns), None)
    resolution_col = next((c for c in ["Resolution_Time", "duration", "resolve_time", "resolution_time"] if c in df.columns), None)
    sla_breached_col = next((c for c in ["SLA_Breached", "sla_breached", "breached", "SLA"] if c in df.columns), None)
    reopen_col = next((c for c in ["Reopen_Count", "reopen_count", "reopened", "reopens"] if c in df.columns), None)

    # 2. Apply Date Range Filtering (Analysis Interval)
    actual_start, actual_end = None, None
    if date_col and len(df) > 0:
        try:
            # Coerce dates safely
            temp_dates = pd.to_datetime(df[date_col], errors='coerce')
            valid_indices = temp_dates.notna()
            if valid_indices.any():
                df = df[valid_indices].copy()
                df[date_col] = temp_dates[valid_indices]
                
                # Sort chronologically
                df = df.sort_values(by=date_col)
                
                if start_date:
                    df = df[df[date_col] >= pd.to_datetime(start_date)]
                if end_date:
                    df = df[df[date_col] <= pd.to_datetime(end_date)]
                    
                if len(df) > 0:
                    actual_start = df[date_col].min().isoformat()
                    actual_end = df[date_col].max().isoformat()
        except Exception:
            pass

    insights = {
        "total_tickets": len(df),
        "analysis_interval": {"start": actual_start, "end": actual_end},
        "categories": {},
        "subcategories": {},
        "assignment_groups": {},
        "priority_distribution": {},
        "priority_vs_resolution_time": {},
        "trends": [],
        "spikes": [],
        "problem_candidates": []
    }
    
    if len(df) == 0:
        return insights

    # 3. Distributions
    if cat_col and cat_col in df.columns:
        insights["categories"] = {str(k): int(v) for k, v in df[cat_col].value_counts().dropna().to_dict().items()}
    if sub_col and sub_col in df.columns:
        insights["subcategories"] = {str(k): int(v) for k, v in df[sub_col].value_counts().dropna().to_dict().items()}
    if grp_col and grp_col in df.columns:
        insights["assignment_groups"] = {str(k): int(v) for k, v in df[grp_col].value_counts().dropna().to_dict().items()}
    if priority_col and priority_col in df.columns:
        insights["priority_distribution"] = {str(k): int(v) for k, v in df[priority_col].value_counts().dropna().to_dict().items()}

    # 4. Priority vs Average Resolution Time
    if priority_col and priority_col in df.columns and resolution_col and resolution_col in df.columns:
        try:
            temp_res = pd.to_numeric(df[resolution_col], errors='coerce')
            valid_res = temp_res.notna()
            if valid_res.any():
                df_res = df[valid_res].copy()
                df_res[resolution_col] = temp_res[valid_res]
                avg_res = df_res.groupby(priority_col)[resolution_col].mean().dropna().to_dict()
                insights["priority_vs_resolution_time"] = {str(k): float(round(v, 2)) for k, v in avg_res.items()}
        except Exception:
            pass

    # 5. Ticket Generation Trend & Spike Detection
    if date_col and date_col in df.columns:
        try:
            daily_counts = df.groupby(df[date_col].dt.date).size()
            insights["trends"] = [{"date": str(k), "count": int(v)} for k, v in daily_counts.items()]
            
            # Spike Detection (Rolling Mean + 1.5 * StdDev)
            if len(daily_counts) >= 3:
                rolling_mean = daily_counts.rolling(window=3, min_periods=1).mean()
                rolling_std = daily_counts.rolling(window=3, min_periods=1).std().fillna(0)
                threshold = rolling_mean + (1.5 * rolling_std)
                
                avg_daily = daily_counts.mean()
                for date_obj, count in daily_counts.items():
                    if count > threshold[date_obj] and count > avg_daily:
                        pct_above = float(round(((count - avg_daily) / avg_daily) * 100, 1)) if avg_daily > 0 else 100.0
                        insights["spikes"].append({
                            "date": str(date_obj),
                            "count": int(count),
                            "percentage_above_avg": pct_above
                        })
        except Exception:
            pass

    # 6. Problem Candidates (Similarity Clustering & SLA Breach Aggregations)
    if desc_col and desc_col in df.columns:
        try:
            from collections import Counter
            # Simple similarity/exact grouping of descriptions to find repeated issues
            descriptions = df[desc_col].astype(str).str.strip().str.lower().tolist()
            counts = Counter(descriptions)
            repeats = [desc for desc, count in counts.items() if count > 1]
            
            for idx, r_desc in enumerate(repeats[:5]):
                matching_tickets = df[df[desc_col].astype(str).str.strip().str.lower() == r_desc]
                p_val = "Medium"
                if priority_col and priority_col in df.columns and len(matching_tickets) > 0:
                    p_val = str(matching_tickets[priority_col].iloc[0])
                
                sla_breached = False
                if sla_breached_col and sla_breached_col in df.columns:
                    sla_breached = any(matching_tickets[sla_breached_col].astype(str).str.lower().isin(['true', 'yes', 'y', '1']))

                insights["problem_candidates"].append({
                    "id": f"PROB-{100 + idx}",
                    "type": "Recurring Incident Pattern",
                    "description": r_desc.capitalize(),
                    "frequency": len(matching_tickets),
                    "impacted_priority": p_val,
                    "sla_status": "Breached" if sla_breached else "Within SLA"
                })
        except Exception:
            pass

    # SLA breaches aggregation
    if sla_breached_col and sla_breached_col in df.columns and len(insights["problem_candidates"]) < 8:
        try:
            breached_df = df[df[sla_breached_col].astype(str).str.lower().isin(['true', 'yes', 'y', '1'])]
            if len(breached_df) > 0 and cat_col and cat_col in df.columns:
                top_breach_cat = breached_df[cat_col].value_counts().idxmax()
                insights["problem_candidates"].append({
                    "id": f"PROB-201",
                    "type": "Chronic SLA Breaches",
                    "description": f"Repeated SLA breaches observed under category: {top_breach_cat}",
                    "frequency": int(len(breached_df)),
                    "impacted_priority": "High",
                    "sla_status": "Breached"
                })
        except Exception:
            pass

    # Repeated reopenings aggregation
    if reopen_col and reopen_col in df.columns and len(insights["problem_candidates"]) < 8:
        try:
            reopened_df = df[pd.to_numeric(df[reopen_col], errors='coerce') > 1]
            if len(reopened_df) > 0:
                insights["problem_candidates"].append({
                    "id": f"PROB-301",
                    "type": "Frequent Reopenings",
                    "description": "High ticket reopen rate, indicating potential resolution quality issues.",
                    "frequency": int(len(reopened_df)),
                    "impacted_priority": "Medium",
                    "sla_status": "Within SLA"
                })
        except Exception:
            pass

    return insights
