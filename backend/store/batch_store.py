import uuid
from datetime import datetime

class BatchStore:
    def __init__(self):
        self.files = {}

    def add_file(self, filename, content):
        file_id = str(uuid.uuid4())
        self.files[file_id] = {
            "id": file_id,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "status": "Uploaded",
            "powerbi_link": None,
            "headers": [],
            "column_mapping": {},
            "original_content": content,
            "processed_content": None
        }
        return self.files[file_id]

    def update_headers(self, file_id, headers):
        if file_id in self.files:
            self.files[file_id]["headers"] = headers
            return True
        return False

    def update_mapping(self, file_id, mapping):
        if file_id in self.files:
            self.files[file_id]["column_mapping"] = mapping
            return True
        return False

    def get_all_files(self):
        # Return metadata only, exclude content
        return [
            {k: v for k, v in f.items() if k not in ["original_content", "processed_content"]}
            for f in self.files.values()
        ]

    def get_file(self, file_id):
        return self.files.get(file_id)

    def update_status(self, file_id, status, processed_content=None):
        if file_id in self.files:
            self.files[file_id]["status"] = status
            if processed_content:
                self.files[file_id]["processed_content"] = processed_content
            return True
        return False

    def update_powerbi_link(self, file_id, link):
        if file_id in self.files:
            self.files[file_id]["powerbi_link"] = link
            return True
        return False

    def delete_file(self, file_id):
        if file_id in self.files:
            del self.files[file_id]
            return True
        return False

batch_store = BatchStore()
