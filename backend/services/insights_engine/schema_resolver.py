import pandas as pd

def resolve_columns(df: pd.DataFrame, mapping: dict = None) -> dict:
    """
    Resolves DataFrame headers, ensuring user manual mappings from UI ALWAYS take precedence,
    followed by strict checks on enterprise naming standards, and finally fuzzy fallbacks.
    """
    mapping = mapping or {}
    resolved = {}

    # 1. Category Mapping
    cat_col = mapping.get("Category")
    if not cat_col or cat_col not in df.columns:
        cat_col = next((c for c in ["Category", "AI_Category", "category", "Ticket Category", "Classification", "Company", "Request For", "Account/Department"] if c in df.columns), None)
        if not cat_col:
            cat_col = next((c for c in df.columns if "cat" in str(c).lower() or "type" in str(c).lower() or "company" in str(c).lower()), None)
    resolved["category"] = cat_col

    # 2. Description Mapping
    desc_col = mapping.get("Description")
    if not desc_col or desc_col not in df.columns:
        desc_col = next((c for c in ["Description", "description", "Short_Description", "Short Description", "summary", "Summary"] if c in df.columns), None)
        if not desc_col:
            desc_col = next((c for c in df.columns if "desc" in str(c).lower() or "short" in str(c).lower() or "subject" in str(c).lower()), None)
    resolved["description"] = desc_col

    # 3. Subcategory Mapping
    sub_col = mapping.get("Subcategory")
    if not sub_col or sub_col not in df.columns:
        sub_col = next((c for c in ["Subcategory", "AI_Subcategory", "subcategory", "Sub-category"] if c in df.columns), None)
        if not sub_col:
             sub_col = next((c for c in df.columns if "sub" in str(c).lower() and "cat" in str(c).lower()), None)
    resolved["subcategory"] = sub_col

    # 4. Assignment Group Mapping
    grp_col = mapping.get("Assignment_Group")
    if not grp_col or grp_col not in df.columns:
        grp_col = next((c for c in ["Assignment_Group", "Assignment Group", "assignment_group", "group", "Group", "Assigned Group"] if c in df.columns), None)
        if not grp_col:
            grp_col = next((c for c in df.columns if "assign" in str(c).lower() and "group" in str(c).lower()), None)
    resolved["assignment_group"] = grp_col

    # 5. Priority Mapping (With additional auto-synonyms like Severity, Urgency)
    prio_col = mapping.get("Priority")
    if not prio_col or prio_col not in df.columns:
        prio_col = next((c for c in ["Priority", "priority", "AI_Priority", "Urgency", "urgency", "Severity", "severity", "State"] if c in df.columns), None)
        if not prio_col:
            prio_col = next((c for c in df.columns if "prio" in str(c).lower() or "urg" in str(c).lower() or "sev" in str(c).lower() or "criticality" in str(c).lower() or "state" in str(c).lower()), None)
    resolved["priority"] = prio_col

    # 6. Resolution Notes Mapping
    res_notes_col = mapping.get("Resolution_Notes")
    if not res_notes_col or res_notes_col not in df.columns:
        res_notes_col = next((c for c in ["Resolution_Notes", "resolution_notes", "Resolution Notes", "close_notes", "Resolution_Summary", "Resolution Summary", "Fix", "Notes"] if c in df.columns), None)
        if not res_notes_col:
            # Fallback to Description if no resolution notes exist
            res_notes_col = next((c for c in df.columns if "resol" in str(c).lower() or "close" in str(c).lower() or "fix" in str(c).lower()), None) or desc_col
    resolved["resolution_notes"] = res_notes_col
    
    # 7. Date resolution (intelligent sorting to ignore technical system timestamps)
    date_col = next((c for c in df.columns if any(sub in str(c).lower() for sub in ["created", "opened(time)", "opened", "incident_date", "incident date", "timestamp", "date"]) and str(c) != "Processed_At"), None)
    if not date_col:
        date_col = next((c for c in ["Opened(Time)", "Created", "Created_At", "Opened", "Opened_At", "date", "createdAt"] if c in df.columns), None) or next((c for c in ["Processed_At"] if c in df.columns), None)
    resolved["date"] = date_col

    # 8. Technical Performance Metrics
    resolved["resolution"] = next((c for c in ["Resolved Date and Time", "Resolution_Time", "duration", "resolve_time", "resolution_time", "Hours", "hours", "resolve_duration"] if c in df.columns), None) or next((c for c in df.columns if "durat" in str(c).lower() or "resol" in str(c).lower() and "time" in str(c).lower()), None)
    resolved["sla_breach"] = next((c for c in ["SLA_Breached", "sla_breached", "breached", "SLA"] if c in df.columns), None) or next((c for c in df.columns if "sla" in str(c).lower() and "breach" in str(c).lower()), None)
    resolved["reopen"] = next((c for c in ["Reopen_Count", "reopen_count", "reopened", "reopens"] if c in df.columns), None) or next((c for c in df.columns if "reopen" in str(c).lower()), None)

    # 9. Status Mapping
    status_col = mapping.get("Status")
    if not status_col or status_col not in df.columns:
        status_col = next((c for c in ["Status", "status", "State", "state", "Incident_State", "Incident State", "Phase", "phase"] if c in df.columns), None)
        if not status_col:
            status_col = next((c for c in df.columns if "stat" in str(c).lower() or "state" in str(c).lower() or "phase" in str(c).lower()), None)
    resolved["status"] = status_col

    return resolved
