import os
import time
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from requests.auth import HTTPBasicAuth

from store import incidents
from llm_client import classify_with_gemini

# Load environment variables
load_dotenv()

app = Flask(__name__)


def fetch_servicenow_incidents(limit=5):
    """Fetch active incidents directly from ServiceNow."""
    snow_url = os.getenv("SNOW_INSTANCE_URL")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")

    if not all([snow_url, snow_user, snow_pwd]):
        raise ValueError("ServiceNow credentials are not configured in the .env file.")

    api_url = (
        f"{snow_url}/api/now/table/incident"
        f"?sysparm_query=active=true"
        f"&sysparm_limit={limit}"
    )

    response = requests.get(
        api_url,
        auth=HTTPBasicAuth(snow_user, snow_pwd),
        headers={"Accept": "application/json"},
        verify=False  # DEV only
    )
    
    # Check if ServiceNow returned an HTML hibernation page instead of JSON
    if "application/json" not in response.headers.get("Content-Type", ""):
        if "Hibernating" in response.text:
            raise ValueError("Your ServiceNow Developer Instance is currently Hibernating! Please log in to developer.servicenow.com to wake it up.")
        raise ValueError("ServiceNow returned an invalid non-JSON response. Check your instance URL.")

    response.raise_for_status()
    return response.json().get("result", [])


@app.route("/incidents", methods=["GET"])
def get_incidents():
    """List incidents currently in the local cache."""
    return jsonify(list(incidents.values()))


@app.route("/incidents/sync", methods=["POST"])
def sync_and_classify():
    """
    Fetch live ServiceNow incidents and classify them using Gemini.
    """
    try:
        snow_incidents = fetch_servicenow_incidents(limit=3)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to ServiceNow", "details": str(e)}), 502

    processed = []

    for inc in snow_incidents:
        inc_id = inc.get("number")
        short_desc = inc.get("short_description")
        long_desc = inc.get("description")
        
        # Ensure we don't concatenate None types
        short_desc = short_desc if short_desc else ""
        long_desc = long_desc if long_desc else ""
        
        full_description = f"{short_desc}\n\n{long_desc}".strip()

        if not inc_id:
            continue

        try:
            time.sleep(4)  # Rate limit protection
            result = classify_with_gemini(full_description)
            category = result["category"]
            assignment_group = result["assignment_group"]
            source = "Gemini"
        except Exception as e:
            category = "Unassigned"
            assignment_group = "Unassigned"
            source = "Failed to classify (LLM Error)"

        incidents[inc_id] = {
            "id": inc_id,
            "description": full_description,
            "category": category,
            "assignment_group": assignment_group,
            "status": "Assigned",
            "history": [
                f"Fetched from ServiceNow",
                f"Classified by {source}: {category} / {assignment_group}"
            ]
        }

        processed.append(incidents[inc_id])

    return jsonify({
        "message": f"Processed {len(processed)} ServiceNow incidents",
        "incidents": processed
    })


@app.route("/incidents/<incident_id>/classify", methods=["POST"])
def classify_incident(incident_id):
    incident = incidents.get(incident_id)

    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
        result = classify_with_gemini(incident["description"])
    except Exception as e:
        return jsonify({
            "error": "LLM classification failed",
            "details": str(e)
        }), 500

    incident["category"] = result["category"]
    incident["assignment_group"] = result["assignment_group"]
    incident["status"] = "Assigned"

    incident["history"].append(
        f"Gemini classified as {incident['category']} "
        f"and assigned to {incident['assignment_group']}"
    )

    return jsonify(incident)


@app.route("/incidents/<incident_id>/heal", methods=["POST"])
def auto_heal(incident_id):
    if incident_id not in incidents:
        return jsonify({"error": "Incident not yet processed"}), 404

    incidents[incident_id]["status"] = "Resolved"
    incidents[incident_id]["history"].append("Auto-healing simulated: Issue resolved")

    return jsonify(incidents[incident_id])


@app.route("/incidents/<incident_id>/history", methods=["GET"])
def incident_history(incident_id):
    if incident_id not in incidents:
        return jsonify({"error": "Incident not found"}), 404

    return jsonify(incidents[incident_id])


if __name__ == "__main__":
    app.run(debug=True)