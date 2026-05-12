from flask import Blueprint, jsonify, request
from services.insights_engine import generate_full_insights
from services.ai import generate_ai_summary, generate_recommendations, ask_data
from services.dataset_loader import get_dataset_for_file
from config import ENABLE_BATCH_LLM

ai_bp = Blueprint("ai", __name__)

def check_llm_active():
    """Checks request context and master config to see if inference is active."""
    # Allow UI toggle to force bypass if desired
    param_val = request.args.get("force_llm")
    if param_val is not None:
        return param_val.lower() == "true"
    
    # Fallback to server-wide setting
    return ENABLE_BATCH_LLM

@ai_bp.route("/summary", methods=["GET"])
def get_summary():
    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    df, file_data, err = get_dataset_for_file(file_id)
    if err:
        return jsonify(err[0]), err[1]

    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    
    # EXECUTION LAYER
    if check_llm_active():
        summary = generate_ai_summary(insights)
    else:
        # Deterministic Fallback System
        top_cats = ", ".join(list(insights.get("categories", {}).keys())[:3])
        summary = {
            "summary": f"Analysis completed on {insights.get('total_tickets')} total incidents. Top contributing categories are {top_cats}. Static monitoring is operational while LLM enhancement is offline."
        }

    return jsonify(summary)

@ai_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    df, file_data, err = get_dataset_for_file(file_id)
    if err:
        return jsonify(err[0]), err[1]

    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    
    # EXECUTION LAYER
    if check_llm_active():
        recs = generate_recommendations(insights)
    else:
        # Deterministic Fallback System
        recs = [
            {
                "problem": "Infrastructure Stability / Recency Volumes",
                "recommendation": "Investigate current top categorizations and perform immediate root cause correlation on recent surge events manually."
            },
            {
                "problem": "General Operational Thresholds",
                "recommendation": "Automated AI generation is disabled. Review the Visual Charts tab to analyze breakdown statistics directly."
            }
        ]

    return jsonify(recs)

@ai_bp.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    question = data.get("question")
    file_id = data.get("file_id")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    df, file_data, err = get_dataset_for_file(file_id)
    if err:
        return jsonify(err[0]), err[1]

    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping)
    
    # EXECUTION LAYER
    if check_llm_active():
        answer = ask_data(question, insights)
    else:
        # Deterministic Fallback System
        answer = {
            "answer": "Automated Q&A requires active machine intelligence connectivity. Currently processing in Statistics Only mode."
        }

    return jsonify(answer)
