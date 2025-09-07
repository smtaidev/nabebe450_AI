import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
from core.config import settings
import os
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        """Initialize S3 client for DigitalOcean Spaces"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=settings.s3_region,
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key
            )
            self.bucket_name = settings.s3_bucket_name
            logger.info(f"S3 service initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise

    def upload_video_from_url(self, video_url: str, video_id: str) -> Optional[str]:
        """
        Download video from HeyGen URL and upload to S3
        
        Args:
            video_url: The URL of the video to download
            video_id: Unique identifier for the video
            
        Returns:
            S3 URL of the uploaded video or None if failed
        """
        try:
            # Generate S3 key with timestamp and video_id
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"heygen_videos/{timestamp}_{video_id}.mp4"
            
            logger.info(f"Downloading video from: {video_url}")
            
            # Download video from HeyGen URL
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            # Upload to S3
            logger.info(f"Uploading video to S3: {s3_key}")
            self.s3_client.upload_fileobj(
                response.raw,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'video/mp4',
                    'ACL': 'public-read'  # Make video publicly accessible
                }
            )
            
            # Generate public URL
            s3_url = f"{settings.s3_endpoint.rstrip('/')}/{self.bucket_name}/{s3_key}"
            logger.info(f"Video uploaded successfully to: {s3_url}")
            
            return s3_url
            
        except requests.RequestException as e:
            logger.error(f"Failed to download video from {video_url}: {str(e)}")
            return None
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading video: {str(e)}")
            return None

    def upload_file(self, file_content: bytes, file_key: str, content_type: str = "video/mp4") -> Optional[str]:
        """
        Upload file content directly to S3
        
        Args:
            file_content: Binary content of the file
            file_key: S3 key for the file
            content_type: MIME type of the file
            
        Returns:
            S3 URL of the uploaded file or None if failed
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            s3_url = f"{settings.s3_endpoint.rstrip('/')}/{self.bucket_name}/{file_key}"
            logger.info(f"File uploaded successfully to: {s3_url}")
            
            return s3_url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            return None

    def delete_video(self, video_key: str) -> bool:
        """
        Delete video from S3
        
        Args:
            video_key: S3 key of the video to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=video_key)
            logger.info(f"Video deleted successfully: {video_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete video {video_key}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting video: {str(e)}")
            return False

    def list_videos(self, prefix: str = "heygen_videos/") -> list:
        """
        List all videos in S3 bucket with given prefix
        
        Args:
            prefix: S3 key prefix to filter videos
            
        Returns:
            List of video objects
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            videos = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    video_url = f"{settings.s3_endpoint.rstrip('/')}/{self.bucket_name}/{obj['Key']}"
                    videos.append({
                        'key': obj['Key'],
                        'url': video_url,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return videos
            
        except ClientError as e:
            logger.error(f"Failed to list videos: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing videos: {str(e)}")
            return []

    def check_connection(self) -> bool:
        """
        Test S3 connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3 connection test successful")
            return True
        except ClientError as e:
            logger.error(f"S3 connection test failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing S3 connection: {str(e)}")
            return False

# Create global S3 service instance
s3_service = S3Service()
