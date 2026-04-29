import re
from services.ai_engine import classify_incident_basic, assign_incident_with_context
from services.servicenow.client import (
    fetch_incidents,
    update_incident,
    get_user_vip,
    fetch_groups,
    fetch_users
)
from services.servicenow.choices import get_choices_for_llm
from services.servicenow.mappers import calculate_priority, map_snow_to_standard

def get_dashboard_incidents(incidents_cache: dict) -> list:
    """Fetches raw incidents from ServiceNow and prepares them for the dashboard."""
    snow_incidents = fetch_incidents()
    processed_incidents = []

    for inc in snow_incidents:
        inc_id = inc.get("number")
        if not inc_id: continue
        
        if inc_id in incidents_cache:
            processed_incidents.append(incidents_cache[inc_id])
            continue
            
        short_desc = inc.get("short_description", "") or ""
        long_desc = inc.get("description", "") or ""
        full_description = f"{short_desc}\n\n{long_desc}".strip()
        
        impact = map_snow_to_standard(inc.get("impact"))
        urgency = map_snow_to_standard(inc.get("urgency"))
        priority = calculate_priority(impact, urgency)

        caller_data = inc.get("caller_id")
        caller_sys_id = caller_data.get("value") if isinstance(caller_data, dict) else caller_data

        incident = {
            "id": inc_id,
            "sys_id": inc.get("sys_id"),
            "caller_id": caller_sys_id,
            "description": full_description,
            "category": "Unassigned",
            "subcategory": "Unassigned",
            "impact": impact,
            "urgency": urgency,
            "priority": priority,
            "assignment_group": "Unassigned",
            "assigned_to": "Unassigned",
            "status": "Open",
            "history": ["Fetched from ServiceNow"]
        }
        incidents_cache[inc_id] = incident
        processed_incidents.append(incident)
    
    return processed_incidents

def get_formatted_team() -> list:
    """Fetches users from ServiceNow and formats them for the team view."""
    users = fetch_users(limit=50)
    team = []
    for u in users:
        role = u.get("title") or "IT Professional"
        team.append({
            "id": u.get("sys_id"),
            "name": u.get("name"),
            "role": role,
            "email": u.get("email", "")
        })
    return team


# --- Rule-based Constants ---
RED_FLAG_KEYWORDS = ["outage", "production down", "emergency", "breach", "critical bug", "p1", "system down", "security incident", "suspicious", "compromise", "unauthorized"]
SECURITY_KEYWORDS = ["breach", "compromise", "suspicious", "unauthorized", "credential", "security incident"]

def check_red_flags(description: str) -> bool:
    """Returns True if highly critical keywords are detected in the description."""
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in RED_FLAG_KEYWORDS)

def process_classification(incident):
    """Handles the hybrid classification logic for an incident."""
    description = incident.get("description", "")
    
    # Pre-LLM Step: Deterministic Red-Flag Keyword Scan
    has_red_flags = check_red_flags(description)
    is_security_threat = any(k in description.lower() for k in SECURITY_KEYWORDS)
    
    # 1. Fetch live choices
    categories, subcategories_map, category_map = get_choices_for_llm()

    # 2. Run LLM Classification (Primary)
    result = classify_incident_basic(description, categories, subcategories_map, category_map)
    
    # AI Result extraction
    category = result.get("category", "Unknown")
    subcategory = result.get("subcategory", "Unknown")
    
    # Base Impact/Urgency from AI
    impact_num = str(result.get("impact", "3")).split(' ')[0]
    urgency_num = str(result.get("urgency", "3")).split(' ')[0]
    
    overrides = []

    # --- Hybrid Override Engine ---
    
    # Rule 0: Security Force (Deterministic)
    if is_security_threat:
        category = "Security"
        impact_num = "1"
        urgency_num = "1"
        overrides.append("Security threat detected (Forced Category & High Impact)")

    # Rule 1: Red-Flag Keywords
    if has_red_flags:
        impact_num = "1"
        urgency_num = "1"
        overrides.append("Deterministic Red-Flag keyword detected")

    # Rule 2: VIP Status Check
    caller_id = incident.get("caller_id")
    if caller_id and get_user_vip(caller_id):
        urgency_num = "1"
        overrides.append("VIP Caller detected (Urgency elevated)")

    # Rule 3: Security Category Check
    if category.lower() == "security":
        impact_num = "1"
        overrides.append("Security incident detected (Impact elevated)")

    # Update incident state
    incident["category"] = category
    incident["subcategory"] = subcategory
    incident["impact"] = map_snow_to_standard(impact_num)
    incident["urgency"] = map_snow_to_standard(urgency_num)
    incident["priority"] = calculate_priority(incident["impact"], incident["urgency"])
    incident["status"] = "Classified"
    
    # History log
    history_entry = f"Hybrid Classification: {category}/{subcategory} (P:{incident['priority']})"
    if overrides:
         history_entry += " [!] Rules applied: " + ", ".join(overrides)
    incident.setdefault("history", []).append(history_entry)

    # 3. Patch SNOW fields and work notes
    override_msg = "\n".join([f"- {o}" for o in overrides]) if overrides else "No rule-based overrides applied."
    work_notes = (
        f"--- AI Hybrid Classification ---\n"
        f"Category: {category}\n"
        f"Subcategory: {subcategory}\n"
        f"Impact: {incident['impact']}\n"
        f"Urgency: {incident['urgency']}\n"
        f"Priority (Calculated): {incident['priority']}\n\n"
        f"Policy Checklist:\n{override_msg}\n"
    )
    
    update_data = {
        "work_notes": work_notes,
        "category": str(category).strip(),
        "subcategory": str(subcategory).strip(),
        "u_subcategory": str(subcategory).strip(),
        "impact": impact_num,
        "urgency": urgency_num
    }
    update_incident(incident.get("sys_id"), update_data)
    return incident

def process_assignment(incident):
    """Handles logic for assigning an incident to a group and user."""
    # 1. Fetch live contexts
    groups_raw = fetch_groups(limit=20)
    users_raw = fetch_users(limit=50)
    
    group_names = [g.get("name") for g in groups_raw if g.get("name")]
    user_info = [f'{u.get("name", "")} ({u.get("title", "IT")})' for u in users_raw]
    
    # 2. Run Gemini
    result = assign_incident_with_context(
        incident["description"], 
        incident["category"], 
        group_names, 
        user_info
    )
    
    assigned_group_name = result.get("assignment_group", "Unknown")
    assigned_to_raw = result.get("assigned_to", "Unknown")
    assigned_to_clean = re.sub(r'\s*\(.*?\)', '', assigned_to_raw).strip()

    # Update local state
    incident["assignment_group"] = assigned_group_name
    incident["assigned_to"] = assigned_to_clean
    incident["status"] = "Assigned"
    incident.setdefault("history", []).append(f"Assigned to {assigned_group_name} -> {assigned_to_clean}")
    
    # Map to sys_ids for SNOW update
    update_data = {}
    
    group_sys_id = next((g.get("sys_id") for g in groups_raw if g.get("name") == assigned_group_name), assigned_group_name)
    user_sys_id = next((u.get("sys_id") for u in users_raw if u.get("name") == assigned_to_clean), assigned_to_clean)
    
    update_data["assignment_group"] = group_sys_id
    update_data["assigned_to"] = user_sys_id
    update_data["work_notes"] = f"--- AI Assignment ---\nGroup: {assigned_group_name}\nAssigned To: {assigned_to_clean}\n"
    
    incident_sys_id = incident.get("sys_id")
    print(f"DEBUG: assignment_group value type: {type(group_sys_id)} | value: {group_sys_id}")
    print(f"DEBUG: assigned_to value type: {type(user_sys_id)} | value: {user_sys_id}")
    print(f"DEBUG: Patching SNOW {incident_sys_id} with data:", update_data)
    
    update_incident(incident_sys_id, update_data)
    return incident

def process_resolution(incident):
    """Handles the resolution logic for an incident."""
    incident["status"] = "Resolved"
    incident.setdefault("history", []).append("Marked as Resolved via UI.")
    
    update_data = {
        "work_notes": "Incident manually marked as Resolved via Incident Tracker.",
        "state": "6", # Resolved
        "close_code": "Solved (Permanently)",
        "close_notes": "Resolved via Incident Tracker Dashboard.",
    }
    update_incident(incident.get("sys_id"), update_data)
    return incident
