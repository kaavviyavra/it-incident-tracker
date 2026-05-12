from flask import Blueprint, jsonify, request
from services.insights_engine import generate_full_insights
from services.dataset_loader import get_dataset_for_file

insights_bp = Blueprint("insights", __name__)

@insights_bp.route("/insights", methods=["GET"])
def get_insights():
    file_id = request.args.get("file_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    df, file_data, err = get_dataset_for_file(file_id)
    if err:
        return jsonify(err[0]), err[1]

    mapping = file_data.get("column_mapping", {})
    insights = generate_full_insights(df, mapping=mapping, start_date=start_date, end_date=end_date)
    return jsonify(insights)
