import os
import uuid
from werkzeug.utils import secure_filename

class StorageService:
    """Abstract interface for file storage operations."""
    def save_file(self, file_stream, filename: str) -> str:
        raise NotImplementedError
        
    def get_file_path(self, relative_path: str) -> str:
        raise NotImplementedError
        
    def delete_file(self, relative_path: str) -> bool:
        raise NotImplementedError

class LocalStorageService(StorageService):
    """Local filesystem implementation of StorageService."""
    def __init__(self, upload_folder: str = None):
        if upload_folder is None:
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    def save_file(self, file_stream, filename: str) -> str:
        sanitized_name = secure_filename(filename) or 'invoice.pdf'
        ext = sanitized_name.rsplit('.', 1)[-1].lower() if '.' in sanitized_name else 'pdf'
        unique_filename = f"{uuid.uuid4().hex}_{sanitized_name}"
        full_path = os.path.join(self.upload_folder, unique_filename)
        
        if hasattr(file_stream, 'save'):
            file_stream.save(full_path)
        else:
            with open(full_path, 'wb') as f:
                f.write(file_stream.read() if hasattr(file_stream, 'read') else file_stream)
                
        return unique_filename

    def get_file_path(self, relative_path: str) -> str:
        full_path = os.path.join(self.upload_folder, relative_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {relative_path}")
        return full_path

    def delete_file(self, relative_path: str) -> bool:
        try:
            full_path = self.get_file_path(relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except FileNotFoundError:
            pass
        return False
