import os
import time
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from requests.auth import HTTPBasicAuth

from store import incidents
from llm_client import classify_incident_basic, assign_incident_with_context
from servicenow_choices import get_choices_for_llm

load_dotenv()
app = Flask(__name__)

# --- ServiceNow Fetchers ---
def get_snow_auth():
    snow_url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    if not all([snow_url, snow_user, snow_pwd]):
        raise ValueError("ServiceNow credentials are not configured in the .env file.")
    return snow_url, HTTPBasicAuth(snow_user, snow_pwd)

def fetch_servicenow_incidents(limit=10):
    snow_url = os.getenv("SNOW_INSTANCE_URL")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    url, auth = get_snow_auth()
    api_url = f"{snow_url}/api/now/table/incident?sysparm_query=active=true^opened_by=javascript:gs.getUserID()^ORDERBYDESCsys_created_on"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    response.raise_for_status()
    return response.json().get("result", [])

def fetch_servicenow_groups(limit=15):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/sys_user_group?sysparm_query=active=true&sysparm_limit={limit}"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    response.raise_for_status()
    return response.json().get("result", [])

def fetch_servicenow_users(limit=50):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/sys_user?sysparm_query=active=true^emailISNOTEMPTY&sysparm_limit={limit}"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    response.raise_for_status()
    return response.json().get("result", [])

def update_snow_incident(sys_id, update_data):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/incident/{sys_id}?sysparm_input_display_value=true"
    try:
        print(f"DEBUG: Patching SNOW {sys_id} with data: {update_data}")
        response = requests.patch(api_url, auth=auth, json=update_data, headers={"Accept": "application/json"}, verify=False)
        if response.status_code != 200:
             print(f"SNOW Update Warning (Status {response.status_code}): {response.text}")
        response.raise_for_status()
        print(f"SNOW Update Successful for {sys_id}")
    except Exception as e:
        error_details = response.text if 'response' in locals() else "No response"
        print(f"CRITICAL: Failed to update SNOW incident {sys_id}: {e}\nDetails: {error_details}")

# --- Priority Calculation ---
def calculate_priority(impact, urgency):
    """
    Deterministically calculates priority based on Impact and Urgency.
    Default to '3 - Moderate' if inputs are missing or invalid.
    """
    # Mapping based on user requirement
    matrix = {
        ("1 - High", "1 - High"): "1 - Critical",
        ("1 - High", "2 - Medium"): "2 - High",
        ("1 - High", "3 - Low"): "3 - Moderate",
        ("2 - Medium", "1 - High"): "2 - High",
        ("2 - Medium", "2 - Medium"): "3 - Moderate",
        ("2 - Medium", "3 - Low"): "4 - Low",
        ("3 - Low", "1 - High"): "3 - Moderate",
        ("3 - Low", "2 - Medium"): "4 - Low",
        ("3 - Low", "3 - Low"): "5 - Planning",
    }
    return matrix.get((impact, urgency), "3 - Moderate")

def map_snow_to_standard(val):
    """Maps SNOW numeric values to the standard 'N - Label' format."""
    mapping = {
        "1": "1 - High",
        "2": "2 - Medium",
        "3": "3 - Low"
    }
    return mapping.get(str(val), "3 - Low")

# --- API Endpoints ---
@app.route("/incidents", methods=["GET"])
def get_incidents():
    """Fetch raw incidents and display them. Do not auto-classify."""
    try:
        snow_incidents = fetch_servicenow_incidents()
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
        update_snow_incident(incident.get("sys_id"), update_data)

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
        groups_raw = fetch_servicenow_groups(limit=20)
        users_raw = fetch_servicenow_users(limit=50)
        
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
        
        import re
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
        update_snow_incident(incident.get("sys_id"), update_data)

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
    
    # Optional: fetch the sys_user id for the current user if we want 'resolved_by'.
    # We will pass a generic text in close_notes or rely on API identity for resolved_by.
    # `resolved_at` is usually set automatically by ServiceNow upon state changing to 6.
    
    update_snow_incident(incident.get("sys_id"), update_data)
    
    return jsonify(incident)


@app.route("/team", methods=["GET"])
def get_team():
    try:
        users = fetch_servicenow_users(limit=50)
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