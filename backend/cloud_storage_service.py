"""
Cloud Storage Service for Document Management
Handles file upload, storage, and retrieval using Google Cloud Storage
"""

import os
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, BinaryIO
from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
import logging

logger = logging.getLogger(__name__)

class CloudStorageService:
    """Service for managing documents in Google Cloud Storage"""
    
    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        self.bucket = None
        
        try:
            self.bucket = self.client.bucket(bucket_name)
            # Check if bucket exists, create if not
            if not self.bucket.exists():
                logger.info(f"Creating bucket {bucket_name}")
                self.bucket = self.client.create_bucket(bucket_name)
            else:
                logger.info(f"Using existing bucket {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage: {e}")
            raise
    
    def generate_file_path(self, filename: str, user_id: str, file_type: str = "documents") -> str:
        """Generate organized file path for storage"""
        # Create organized folder structure
        timestamp = datetime.now().strftime("%Y/%m/%d")
        file_hash = hashlib.md5(f"{filename}{user_id}{timestamp}".encode()).hexdigest()[:8]
        
        # Clean filename
        clean_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
        
        return f"{file_type}/{user_id}/{timestamp}/{file_hash}_{clean_filename}"
    
    def upload_file(self, file_content: bytes, filename: str, user_id: str, 
                   metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """Upload file to Cloud Storage"""
        try:
            # Generate file path
            file_path = self.generate_file_path(filename, user_id)
            
            # Create blob
            blob = self.bucket.blob(file_path)
            
            # Set content type
            content_type, _ = mimetypes.guess_type(filename)
            if content_type:
                blob.content_type = content_type
            
            # Set metadata
            blob_metadata = {
                "original_filename": filename,
                "uploaded_by": user_id,
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": str(len(file_content)),
                "file_hash": hashlib.sha256(file_content).hexdigest()
            }
            
            if metadata:
                blob_metadata.update(metadata)
            
            blob.metadata = blob_metadata
            
            # Upload file
            blob.upload_from_string(file_content)
            
            # Make blob publicly readable (optional)
            blob.make_public()
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "public_url": blob.public_url,
                "gs_uri": f"gs://{self.bucket_name}/{file_path}",
                "metadata": blob_metadata,
                "size_bytes": len(file_content)
            }
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage upload error: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"File upload error: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file from Cloud Storage"""
        try:
            blob = self.bucket.blob(file_path)
            
            if not blob.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            content = blob.download_as_bytes()
            logger.info(f"File downloaded successfully: {file_path}")
            return content
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage download error: {e}")
            return None
        except Exception as e:
            logger.error(f"File download error: {e}")
            return None
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from Cloud Storage"""
        try:
            blob = self.bucket.blob(file_path)
            
            if not blob.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            blob.reload()
            
            metadata = {
                "file_path": file_path,
                "size_bytes": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "public_url": blob.public_url,
                "gs_uri": f"gs://{self.bucket_name}/{file_path}",
                "metadata": blob.metadata or {}
            }
            
            return metadata
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage metadata error: {e}")
            return None
        except Exception as e:
            logger.error(f"File metadata error: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Cloud Storage"""
        try:
            blob = self.bucket.blob(file_path)
            
            if not blob.exists():
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            blob.delete()
            logger.info(f"File deleted successfully: {file_path}")
            return True
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage delete error: {e}")
            return False
        except Exception as e:
            logger.error(f"File delete error: {e}")
            return False
    
    def list_user_files(self, user_id: str, file_type: str = "documents") -> List[Dict[str, Any]]:
        """List all files for a specific user"""
        try:
            prefix = f"{file_type}/{user_id}/"
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            
            files = []
            for blob in blobs:
                metadata = self.get_file_metadata(blob.name)
                if metadata:
                    files.append(metadata)
            
            logger.info(f"Listed {len(files)} files for user {user_id}")
            return files
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage list error: {e}")
            return []
        except Exception as e:
            logger.error(f"File list error: {e}")
            return []
    
    def generate_signed_url(self, file_path: str, expiration_hours: int = 1) -> Optional[str]:
        """Generate signed URL for private file access"""
        try:
            blob = self.bucket.blob(file_path)
            
            if not blob.exists():
                logger.warning(f"File not found for signed URL: {file_path}")
                return None
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(hours=expiration_hours),
                method="GET"
            )
            
            logger.info(f"Generated signed URL for: {file_path}")
            return url
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage signed URL error: {e}")
            return None
        except Exception as e:
            logger.error(f"Signed URL generation error: {e}")
            return None
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = 0
            
            blobs = self.client.list_blobs(self.bucket_name)
            for blob in blobs:
                if blob.time_created and blob.time_created.replace(tzinfo=None) < cutoff_date:
                    blob.delete()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {blob.name}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            return deleted_count
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage cleanup error: {e}")
            return 0
        except Exception as e:
            logger.error(f"File cleanup error: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            blobs = list(self.client.list_blobs(self.bucket_name))
            
            total_files = len(blobs)
            total_size = sum(blob.size for blob in blobs if blob.size)
            
            # Group by file type
            file_types = {}
            for blob in blobs:
                if blob.content_type:
                    file_type = blob.content_type.split('/')[0]
                    file_types[file_type] = file_types.get(file_type, 0) + 1
            
            stats = {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types,
                "bucket_name": self.bucket_name,
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage stats error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Storage stats error: {e}")
            return {}

# Global instance
def get_storage_service() -> CloudStorageService:
    """Get Cloud Storage service instance"""
    project_id = os.getenv("PROJECT_ID", "startup-ai-evaluator")
    bucket_name = os.getenv("BUCKET_NAME", f"{project_id}-startup-docs")
    
    return CloudStorageService(project_id, bucket_name)
