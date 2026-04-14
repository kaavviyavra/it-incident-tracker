import os
import re
from dotenv import load_dotenv
from flask import Flask, jsonify

from store import incidents
from llm_client import classify_incident_basic, assign_incident_with_context
from services.servicenow.client import (
    fetch_incidents,
    fetch_groups,
    fetch_users,
    update_incident
)
from services.servicenow.choices import get_choices_for_llm
from services.servicenow.utils import calculate_priority, map_snow_to_standard

load_dotenv()
app = Flask(__name__)

# --- API Endpoints ---
@app.route("/incidents", methods=["GET"])
def get_incidents_route():
    """Fetch raw incidents and display them. Do not auto-classify."""
    try:
        snow_incidents = fetch_incidents()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    processed_incidents = []
    
    for inc in snow_incidents:
        inc_id = inc.get("number")
        if not inc_id: continue
        
        # Keep existing cached version if we have it
        if inc_id in incidents:
            processed_incidents.append(incidents[inc_id])
            continue
            
        short_desc = inc.get("short_description", "") or ""
        long_desc = inc.get("description", "") or ""
        # prevent 'None' appearing
        full_description = f"{short_desc}\n\n{long_desc}".strip()
        
        impact = map_snow_to_standard(inc.get("impact"))
        urgency = map_snow_to_standard(inc.get("urgency"))
        priority = calculate_priority(impact, urgency)

        incident = {
            "id": inc_id,
            "sys_id": inc.get("sys_id"),
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
        incidents[inc_id] = incident
        processed_incidents.append(incident)
        
    return jsonify(processed_incidents)


@app.route("/incidents/<incident_id>/classify", methods=["POST"])
def classify_incident(incident_id):
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
        # 1. Fetch live choices
        categories, subcategories_map, category_map = get_choices_for_llm()

        # 2. Run Classification with dynamic choices
        result = classify_incident_basic(incident["description"], categories, subcategories_map, category_map)
        incident["category"] = result.get("category", "Unknown")
        incident["subcategory"] = result.get("subcategory", "Unknown")
        # Priority is calculated deterministically
        incident["priority"] = calculate_priority(incident.get("impact"), incident.get("urgency"))
        incident["status"] = "Classified"
        incident["history"].append(f"Classified: {incident['category']} / {incident['subcategory']}")

        # 3. Patch SNOW fields and work notes
        work_notes = (
            f"--- AI Initial Classification ---\n"
            f"Category: {incident['category']}\n"
            f"Subcategory: {incident['subcategory']}\n"
            f"Priority (Calculated): {incident['priority']}\n"
        )
        
        impact_val = incident.get("impact", "3").split(' ')[0]
        urgency_val = incident.get("urgency", "3").split(' ')[0]

        # Clean values to avoid whitespace issues
        cat_val = str(incident["category"]).strip()
        subcat_val = str(incident["subcategory"]).strip()

        update_data = {
            "work_notes": work_notes,
            "category": cat_val,
            "subcategory": subcat_val,
            "u_subcategory": subcat_val, # Fallback for some custom instances
            "impact": impact_val,
            "urgency": urgency_val
        }
        update_incident(incident.get("sys_id"), update_data)

        return jsonify(incident)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/incidents/<incident_id>/assign", methods=["POST"])
def assign_incident(incident_id):
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
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

        incident["assignment_group"] = assigned_group_name
        incident["assigned_to"] = assigned_to_clean
        incident["status"] = "Assigned"
        log_msg = f"Assigned to {incident['assignment_group']} -> {incident['assigned_to']}"
        incident["history"].append(log_msg)
        
        # Format the update data safely. Map to sys_id if possible.
        update_data = {}
        
        # Find group sys_id
        group_sys_id = None
        for g in groups_raw:
            if g.get("name") == assigned_group_name:
                group_sys_id = g.get("sys_id")
                break
        
        if group_sys_id:
            update_data["assignment_group"] = group_sys_id
        else:
            update_data["assignment_group"] = assigned_group_name  # fallback to display value string

        # Find user sys_id
        user_sys_id = None
        for u in users_raw:
            if u.get("name") == assigned_to_clean:
                user_sys_id = u.get("sys_id")
                break
        
        if user_sys_id:
            update_data["assigned_to"] = user_sys_id
        else:
            update_data["assigned_to"] = assigned_to_clean  # fallback to display value string
            
        # Add work notes
        work_notes = (
            f"--- AI Assignment ---\n"
            f"Assignment Group: {incident['assignment_group']}\n"
            f"Assigned To: {incident['assigned_to']}\n"
        )
        update_data["work_notes"] = work_notes
        
        # Patch SNOW fields
        update_incident(incident.get("sys_id"), update_data)

        return jsonify(incident)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/incidents/<incident_id>/resolve", methods=["POST"])
def resolve_incident(incident_id):
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    incident["status"] = "Resolved"
    incident["history"].append("Marked as Resolved via UI.")
    
    update_data = {
        "work_notes": "Incident manually marked as Resolved via Incident Tracker.",
        "state": "6", # 6 is typical for Resolved
        "close_code": "Solved (Permanently)",
        "close_notes": "Resolved via Incident Tracker Dashboard.",
    }
    
    update_incident(incident.get("sys_id"), update_data)
    
    return jsonify(incident)


@app.route("/team", methods=["GET"])
def get_team():
    try:
        users = fetch_users(limit=50)
        team = []
        for u in users:
            role = u.get("title")
            if not role: role = "IT Professional"
            email = u.get("email", "")
            team.append({
                "id": u.get("sys_id"),
                "name": u.get("name"),
                "role": role,
                "email": email
            })
        return jsonify(team)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)