import os
import time
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from requests.auth import HTTPBasicAuth

from store import incidents
from llm_client import classify_incident_basic, assign_incident_with_context

load_dotenv()
app = Flask(__name__)

# --- ServiceNow Fetchers ---
def get_snow_auth():
    snow_url = os.getenv("SNOW_INSTANCE_URL")
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

def update_snow_work_notes(sys_id, work_notes):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/incident/{sys_id}"
    try:
        requests.patch(api_url, auth=auth, json={"work_notes": work_notes}, headers={"Accept": "application/json"}, verify=False)
    except:
        pass

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
        
        incident = {
            "id": inc_id,
            "sys_id": inc.get("sys_id"),
            "description": full_description,
            "category": "Unassigned",
            "subcategory": "Unassigned",
            "priority": "Medium",
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
        result = classify_incident_basic(incident["description"])
        incident["category"] = result.get("category", "Unknown")
        incident["subcategory"] = result.get("subcategory", "Unknown")
        incident["priority"] = result.get("priority", "Medium")
        incident["status"] = "Classified"
        incident["history"].append(f"Classified: {incident['category']} / {incident['subcategory']}")
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
        
        incident["assignment_group"] = result.get("assignment_group", "Unknown")
        incident["assigned_to"] = result.get("assigned_to", "Unknown")
        incident["status"] = "Assigned"
        log_msg = f"Assigned to {incident['assignment_group']} -> {incident['assigned_to']}"
        incident["history"].append(log_msg)
        
        # 3. Patch SNOW work notes
        work_notes = (
            f"--- AI Assignment & Classification ---\n"
            f"Category: {incident['category']}\n"
            f"Subcategory: {incident['subcategory']}\n"
            f"Assignment Group: {incident['assignment_group']}\n"
            f"Assigned To: {incident['assigned_to']}\n"
        )
        update_snow_work_notes(incident.get("sys_id"), work_notes)

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
    update_snow_work_notes(incident.get("sys_id"), "Incident manually marked as Resolved via Incident Tracker.")
    
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