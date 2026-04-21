import os
from dotenv import load_dotenv
from flask import Flask, jsonify

from store.memory import incidents
from services.incident_logic import (
    get_dashboard_incidents,
    get_formatted_team,
    process_classification,
    process_assignment,
    process_resolution
)

load_dotenv()
app = Flask(__name__)

# --- API Endpoints ---

@app.route("/incidents", methods=["GET"])
def get_incidents_route():
    """Fetches raw incidents and prepares them for the dashboard via service layer."""
    try:
        data = get_dashboard_incidents(incidents)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/incidents/<incident_id>/classify", methods=["POST"])
def classify_incident(incident_id):
    """Triggers the AI Hybrid Classification Engine for a specific incident."""
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
        updated_incident = process_classification(incident)
        return jsonify(updated_incident)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/incidents/<incident_id>/assign", methods=["POST"])
def assign_incident(incident_id):
    """Triggers AI-driven assignment and synchronization for a specific incident."""
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
        updated_incident = process_assignment(incident)
        return jsonify(updated_incident)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/incidents/<incident_id>/resolve", methods=["POST"])
def resolve_incident(incident_id):
    """Marks an incident as resolved in both local store and ServiceNow."""
    incident = incidents.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    try:
        updated_incident = process_resolution(incident)
        return jsonify(updated_incident)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/team", methods=["GET"])
def get_team():
    """Fetches and formats the IT team member list."""
    try:
        team = get_formatted_team()
        return jsonify(team)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
