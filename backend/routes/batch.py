import io
import pandas as pd
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
from store.batch_store import batch_store
from services.batch_processing import process_batch_file

batch_bp = Blueprint("batch", __name__)

@batch_bp.route("/batch/files", methods=["GET"])
def get_batch_files():
    """Returns metadata for all uploaded batch files."""
    return jsonify(batch_store.get_all_files())

@batch_bp.route("/batch/upload", methods=["POST"])
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

@batch_bp.route("/batch/files/<file_id>/process", methods=["POST"])
def process_batch_file_route(file_id):
    """Triggers processing/analysis for a specific batch file."""
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
        from store.runtime_cache import batch_datasets
        batch_datasets[file_id] = df

        batch_store.update_status(file_id, "Classified", processed_file_io.getvalue())
        return jsonify({"message": "File processed successfully", "status": "Classified"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@batch_bp.route("/batch/files/<file_id>", methods=["DELETE"])
def delete_batch_file(file_id):
    """Deletes a specific batch file from the store."""
    if batch_store.delete_file(file_id):
        return jsonify({"message": "File deleted successfully"})
    return jsonify({"error": "File not found"}), 404

@batch_bp.route("/batch/files/<file_id>/download", methods=["GET"])
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
