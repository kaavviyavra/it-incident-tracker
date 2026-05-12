import io
import json
from flask import Blueprint, jsonify, send_file
from werkzeug.utils import secure_filename
from services.dataset_loader import get_dataset_for_file
from services.ai import run_llm_with_prompt_cache

sop_bp = Blueprint("sop", __name__)

@sop_bp.route("/batch/files/<file_id>/sop", methods=["GET"])
def generate_sop_endpoint(file_id):
    df, file_data, err = get_dataset_for_file(file_id)
    if err:
        return jsonify(err[0]), err[1]

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
    - Return RAW markdown without code fence blocks, starting directly with the content.
    """
    
    try:
        # Change format request to something like 'text' conceptually, or let prompt_cache handle it.
        # Looking at run_llm_with_prompt_cache logic earlier, default "json" cleans backticks.
        # If I ask for json format in engine, it will enforce it. Let's use simple "toon" or modify to support basic text.
        # Wait, let's look at what run_llm_with_prompt_cache supported... It only has 'json' and 'toon' parsing in _run_llm.
        # Let's query it asking for format="json" and requesting field "markdown".
        prompt_json = prompt.replace("Return RAW markdown", "Return output as JSON object with a 'markdown' key containing the fully escaped markdown string.")
        response = run_llm_with_prompt_cache(prompt_json, response_format="json")
        ai_markdown = response.get("markdown")
    except Exception as e:
        print(f"SOP AI generation fallback triggered: {e}")
        ai_markdown = None

    if ai_markdown:
         sop_markdown = ai_markdown
    else:
        # Fallback template
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
