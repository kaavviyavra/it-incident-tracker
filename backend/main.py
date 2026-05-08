import os
import io
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename
from store.memory import incidents
from services.incident_logic import (
    get_dashboard_incidents,
    get_formatted_team,
    process_classification,
    process_assignment,
    process_resolution
)
from services.batch_classifier import process_batch_file
from store.batch_store import batch_store
from services.insights_engine import generate_full_insights
from services.ai_engine import generate_ai_summary
from services.ai_engine import generate_recommendations
from services.ai_engine import ask_data

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

@app.route("/batch/files", methods=["GET"])
def get_batch_files():
    """Returns metadata for all uploaded batch files."""
    return jsonify(batch_store.get_all_files())

@app.route("/batch/upload", methods=["POST"])
def upload_batch():
    """Handles Excel/CSV file upload and saves it to the store."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            file_content = file.read()
            
            # Extract headers
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content), nrows=0)
            else:
                df = pd.read_excel(io.BytesIO(file_content), nrows=0)
            headers = df.columns.tolist()
            
            new_file = batch_store.add_file(file.filename, file_content)
            batch_store.update_headers(new_file["id"], headers)
            
            return jsonify({
                "id": new_file["id"],
                "filename": new_file["filename"],
                "uploaded_at": new_file["uploaded_at"],
                "status": new_file["status"],
                "headers": headers
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Allowed file types are .csv or .xlsx"}), 400

@app.route("/batch/files/<file_id>/classify", methods=["POST"])
def classify_batch_file_route(file_id):
    """Triggers classification for a specific batch file."""
    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File not found"}), 404
        
    try:
        mapping = request.json.get("mapping", {})
        batch_store.update_mapping(file_id, mapping)
        
        processed_file_io = process_batch_file(file_data["original_content"], file_data["filename"], mapping)

        # Convert processed file → DataFrame
        df = pd.read_excel(io.BytesIO(processed_file_io.getvalue()))

        # Store dataset for insights
        from store.memory import batch_datasets
        batch_datasets[file_id] = df

        batch_store.update_status(file_id, "Classified", processed_file_io.getvalue())
        return jsonify({"message": "File classified successfully", "status": "Classified"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/batch/files/<file_id>/powerbi", methods=["POST"])
def update_powerbi_link_route(file_id):
    """Updates the Power BI link for a specific batch file."""
    data = request.json
    link = data.get("link")
    if batch_store.update_powerbi_link(file_id, link):
        return jsonify({"message": "Power BI link updated successfully"})
    return jsonify({"error": "File not found"}), 404

@app.route("/batch/files/<file_id>", methods=["DELETE"])
def delete_batch_file(file_id):
    """Deletes a specific batch file from the store."""
    if batch_store.delete_file(file_id):
        return jsonify({"message": "File deleted successfully"})
    return jsonify({"error": "File not found"}), 404

@app.route("/batch/files/<file_id>/download", methods=["GET"])
def download_batch_file(file_id):
    """Downloads the processed batch file."""
    file_data = batch_store.get_file(file_id)
    if not file_data or not file_data["processed_content"]:
        return jsonify({"error": "Processed file not found"}), 404
        
    output_filename = f"processed_{secure_filename(file_data['filename'])}"
    if not output_filename.endswith('.xlsx'):
        output_filename = output_filename.rsplit('.', 1)[0] + '.xlsx'
        
    return send_file(
        io.BytesIO(file_data["processed_content"]),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=output_filename
    )



@app.route("/insights", methods=["GET"])
def get_insights():
    from store.memory import batch_datasets

    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not file_id:
        if batch_datasets:
            file_id = list(batch_datasets.keys())[-1]
        else:
            files = batch_store.get_all_files()
            if files:
                file_id = files[0]["id"]

    if not file_id:
        return jsonify({"error": "No file ID provided"}), 400

    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File not found"}), 404

    if file_id not in batch_datasets:
        try:
            content = file_data.get("processed_content") or file_data.get("original_content")
            if content:
                if file_data["filename"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                batch_datasets[file_id] = df
        except Exception as e:
            return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

    if file_id not in batch_datasets:
        return jsonify({"error": "No dataset available for this file"}), 400

    df = batch_datasets[file_id]
    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    return jsonify(insights)



@app.route("/summary", methods=["GET"])
def get_summary():
    from store.memory import batch_datasets

    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not file_id:
        if batch_datasets:
            file_id = list(batch_datasets.keys())[-1]
        else:
            files = batch_store.get_all_files()
            if files:
                file_id = files[0]["id"]

    if not file_id:
        return jsonify({"error": "No file ID provided"}), 400

    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File not found"}), 404

    if file_id not in batch_datasets:
        try:
            content = file_data.get("processed_content") or file_data.get("original_content")
            if content:
                if file_data["filename"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                batch_datasets[file_id] = df
        except Exception as e:
            return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

    if file_id not in batch_datasets:
        return jsonify({"error": "No dataset available for this file"}), 400

    df = batch_datasets[file_id]
    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    summary = generate_ai_summary(insights)
    return jsonify(summary)



@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    from store.memory import batch_datasets

    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not file_id:
        if batch_datasets:
            file_id = list(batch_datasets.keys())[-1]
        else:
            files = batch_store.get_all_files()
            if files:
                file_id = files[0]["id"]

    if not file_id:
        return jsonify({"error": "No file ID provided"}), 400

    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File not found"}), 404

    if file_id not in batch_datasets:
        try:
            content = file_data.get("processed_content") or file_data.get("original_content")
            if content:
                if file_data["filename"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                batch_datasets[file_id] = df
        except Exception as e:
            return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

    if file_id not in batch_datasets:
        return jsonify({"error": "No dataset available for this file"}), 400

    df = batch_datasets[file_id]
    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    recs = generate_recommendations(insights)
    return jsonify(recs)



@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    question = data.get("question")
    file_id = data.get("file_id")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    from store.memory import batch_datasets

    if not file_id:
        if batch_datasets:
            file_id = list(batch_datasets.keys())[-1]
        else:
            files = batch_store.get_all_files()
            if files:
                file_id = files[0]["id"]

    if not file_id:
        return jsonify({"error": "No file ID provided"}), 400

    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File not found"}), 404

    if file_id not in batch_datasets:
        try:
            content = file_data.get("processed_content") or file_data.get("original_content")
            if content:
                if file_data["filename"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                batch_datasets[file_id] = df
        except Exception as e:
            return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

    if file_id not in batch_datasets:
        return jsonify({"error": "No dataset available for this file"}), 400

    df = batch_datasets[file_id]
    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping)
    answer = ask_data(question, insights)
    return jsonify(answer)



@app.route("/batch/files/<file_id>/sop", methods=["GET"])
def generate_sop_endpoint(file_id):
    import json
    from store.memory import batch_datasets
    
    file_data = batch_store.get_file(file_id)
    if not file_data:
        return jsonify({"error": "File metadata not found"}), 404
        
    df = batch_datasets.get(file_id)
    if df is None:
        try:
            content = file_data.get("processed_content") or file_data.get("original_content")
            if content:
                if file_data["filename"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                batch_datasets[file_id] = df
        except Exception as e:
            return jsonify({"error": f"Failed to load dataset: {str(e)}"}), 500

    if df is None or len(df) == 0:
        return jsonify({"error": "Dataset is empty or not available"}), 400

    mapping = file_data.get("column_mapping", {})
    
    # Resolve Category column safely
    cat_col = next((c for c in ["Category", "AI_Category", "category"] if c in df.columns), None)
    if not cat_col:
        mapped_cat = mapping.get("Category")
        if mapped_cat in df.columns:
            cat_col = mapped_cat
        else:
            cat_col = next((c for c in df.columns if "cat" in str(c).lower() or "type" in str(c).lower()), None) or (df.columns[0] if len(df.columns) > 0 else None)

    # Resolve Description column safely
    desc_col = next((c for c in ["Description", "description"] if c in df.columns), None)
    if not desc_col:
        mapped_desc = mapping.get("Description")
        if mapped_desc in df.columns:
            desc_col = mapped_desc
        else:
            desc_col = next((c for c in df.columns if "desc" in str(c).lower() or "short" in str(c).lower() or "subject" in str(c).lower()), None) or (df.columns[0] if len(df.columns) > 0 else None)

    res_col = next((c for c in ["Resolution_Summary", "close_notes", "Resolution Notes", "Resolution_Notes", "resolution_notes"] if c in df.columns), None)

    if not cat_col:
        return jsonify({"error": "Category column not found in dataset"}), 400

    # Gather resolution summaries grouped by top 3 categories
    sop_data = {}
    top_categories = df[cat_col].dropna().value_counts().head(3).index.tolist()
    
    for cat in top_categories:
        samples = df[df[cat_col] == cat].dropna(subset=[desc_col] if desc_col else [])
        desc_sample = "No sample description"
        if desc_col and len(samples) > 0:
            desc_sample = str(samples[desc_col].iloc[0])
            
        res_list = []
        if res_col:
            res_list = df[df[cat_col] == cat].dropna(subset=[res_col])[res_col].head(5).astype(str).tolist()
            
        sop_data[cat] = {
            "issue_description": desc_sample,
            "resolutions": res_list or ["Marked as resolved in ITSM system."]
        }

    # Prompt Gemini to generate a Standard Operating Procedure (SOP)
    prompt = f"""
    You are an expert ITSM Solutions Architect.
    Generate a professional Standard Operating Procedure (SOP) Document based on historical resolution data.

    DATA RESOLUTIONS BY CATEGORY:
    {json.dumps(sop_data, indent=2)}

    INSTRUCTIONS:
    - Create a comprehensive, markdown-formatted SOP.
    - For each category, include:
      1. Overview & Issue Definitions
      2. Step-by-Step Troubleshooting Checklist
      3. Proven Solutions (synthesized from the resolutions list)
      4. Prevention & Long-term Actions
    - Keep it practical, structured, and clear.
    """
    
    try:
        response = run_llm_with_prompt_cache(prompt, response_format="json")
    except Exception:
        response = {}

    sop_markdown = f"# STANDARD OPERATING PROCEDURE (SOP)\n\nGenerated from File: {file_data['filename']}\n\n"
    for cat, content in sop_data.items():
        sop_markdown += f"## SOP-{str(cat).upper().replace(' ', '_')} | Troubleshooting {cat}\n\n"
        sop_markdown += f"### 1. Typical Symptom Description\n> {content['issue_description']}\n\n"
        sop_markdown += f"### 2. Verified Troubleshooting & Remediation Checklist\n"
        for idx, res in enumerate(content['resolutions']):
            sop_markdown += f"- {idx+1}. **Resolution Step**: {res}\n"
        sop_markdown += "- [ ] Confirm issue is resolved with the end-user.\n"
        sop_markdown += "- [ ] Verify core dependency health monitor is green.\n"
        sop_markdown += "- [ ] Update tickets with complete resolution notes.\n\n"
        sop_markdown += f"### 3. Prevention & Long-term Corrective Actions\n"
        sop_markdown += f"- Implement system monitoring alerts for {cat}.\n"
        sop_markdown += f"- Schedule monthly health checks on related services.\n"
        sop_markdown += f"- Update user self-service documentation.\n\n"
        sop_markdown += "---\n\n"

    # Export as downloadable file
    sop_io = io.BytesIO(sop_markdown.encode("utf-8"))
    return send_file(
        sop_io,
        mimetype="text/markdown",
        as_attachment=True,
        download_name=f"SOP_{secure_filename(file_data['filename']).rsplit('.', 1)[0]}.md"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
