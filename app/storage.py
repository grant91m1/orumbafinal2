"""
Storage abstraction for handling file uploads.
Supports local filesystem in development and cloud storage in production.
"""
import os
import hashlib
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from app.db import db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class StorageBackend:
    """Base class for storage backends."""

    def _is_allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _exceeds_size_limit(self, file) -> bool:
        stream = file.stream
        position = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(position)
        return size > MAX_FILE_SIZE

    def save_file(self, file, filename: str, subfolder: str = '') -> Tuple[bool, str, Optional[str]]:
        """
        Save a file to storage.
        Returns: (success, url, error_message)
        """
        raise NotImplementedError

    def delete_file(self, filepath: str) -> bool:
        """Delete a file from storage."""
        raise NotImplementedError

    def get_file_url(self, filepath: str) -> str:
        """Get public URL for a file."""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage for development."""

    def __init__(self):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def save_file(self, file, filename: str, subfolder: str = '') -> Tuple[bool, str, Optional[str]]:
        try:
            # Validate file
            if not self._is_allowed_file(filename):
                return False, '', 'File type not allowed'
            if self._exceeds_size_limit(file):
                return False, '', 'File exceeds the 5 MB limit'

            # Secure filename and add hash for uniqueness
            filename = secure_filename(filename)
            file_hash = hashlib.md5((filename + str(os.urandom(16))).encode()).hexdigest()[:8]
            safe_filename = f"{file_hash}_{filename}"

            # Create subfolder if specified
            if subfolder:
                folder_path = os.path.join(UPLOAD_FOLDER, subfolder)
                os.makedirs(folder_path, exist_ok=True)
                filepath = os.path.join(folder_path, safe_filename)
            else:
                filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

            # Save file
            file.save(filepath)

            # Generate URL
            relative_path = os.path.relpath(filepath, BASE_DIR).replace('\\', '/')
            url = f"/{relative_path}"

            return True, url, None
        except Exception as e:
            return False, '', str(e)

    def delete_file(self, filepath: str) -> bool:
        try:
            full_path = os.path.join(BASE_DIR, filepath.lstrip('/'))
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception:
            return False

    def get_file_url(self, filepath: str) -> str:
        return f"/{filepath.lstrip('/')}"


class CloudStorage(StorageBackend):
    """Supabase Storage backend for production uploads."""

    def __init__(self, client, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def save_file(self, file, filename: str, subfolder: str = '') -> Tuple[bool, str, Optional[str]]:
        try:
            # Validate file
            if not self._is_allowed_file(filename):
                return False, '', 'File type not allowed'
            if self._exceeds_size_limit(file):
                return False, '', 'File exceeds the 5 MB limit'

            safe_name = secure_filename(filename)
            safe_subfolder = secure_filename(subfolder)
            if not safe_name:
                return False, '', 'Invalid filename'

            file_hash = hashlib.sha256(os.urandom(32)).hexdigest()[:12]
            storage_path = '/'.join(part for part in (safe_subfolder, f'{file_hash}_{safe_name}') if part)
            bucket = self.client.storage.from_(self.bucket_name)
            bucket.upload(
                storage_path,
                file.read(),
                file_options={
                    'content-type': file.mimetype or 'application/octet-stream',
                    'upsert': 'false',
                },
            )
            return True, bucket.get_public_url(storage_path), None
        except Exception:
            return False, '', 'Cloud storage upload failed'

    def delete_file(self, filepath: str) -> bool:
        try:
            self.client.storage.from_(self.bucket_name).remove([filepath.lstrip('/')])
            return True
        except Exception:
            return False

    def get_file_url(self, filepath: str) -> str:
        return self.client.storage.from_(self.bucket_name).get_public_url(filepath.lstrip('/'))


def get_storage_backend() -> StorageBackend:
    """
    Get the appropriate storage backend based on environment.
    """
    is_production = os.environ.get('FLASK_ENV') == 'production'
    use_cloud = os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true'

    if is_production and use_cloud:
        if not db.client:
            raise RuntimeError('Supabase must be configured to use cloud storage')
        bucket_name = os.environ.get('SUPABASE_STORAGE_BUCKET', 'uploads')
        return CloudStorage(db.client, bucket_name)
    return LocalStorage()


# Global storage instance
storage = get_storage_backend()
