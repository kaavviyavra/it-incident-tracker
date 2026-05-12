import io
import pandas as pd
from store.runtime_cache import batch_datasets
from store.batch_store import batch_store

def get_dataset_for_file(file_id=None):
    """
    Loads and retrieves a DataFrame for a specific file_id, 
    handling falling back to the most recent file if file_id is None.
    Returns tuple: (DataFrame, file_data, error_tuple)
    """
    if not file_id:
        if batch_datasets:
            file_id = list(batch_datasets.keys())[-1]
        else:
            files = batch_store.get_all_files()
            if files:
                file_id = files[0]["id"]

    if not file_id:
        return None, None, ({"error": "No file ID provided"}, 400)

    file_data = batch_store.get_file(file_id)
    if not file_data:
        return None, None, ({"error": "File not found"}, 404)

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
            return None, None, ({"error": f"Failed to load dataset: {str(e)}"}, 500)

    if file_id not in batch_datasets:
         return None, None, ({"error": "No dataset available for this file"}, 400)

    return batch_datasets[file_id], file_data, None
