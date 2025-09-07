from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging
import requests
import json
import time
import uuid

from models.request import HeyGenRequest
from models.response import HeyGenResponse
from core.dependencies import get_api_key
from core.config import settings
from services.s3_service import s3_service

router = APIRouter(prefix="/heygen")
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=HeyGenResponse)
async def generate_video(
    request: HeyGenRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate AI video using HeyGen API"""
    try:
        # Log configuration for debugging
        logger.info(f"HeyGen API Key: {'***' if settings.heygen_api_key else 'NOT SET'}")
        logger.info(f"HeyGen Base URL: {settings.heygen_base_url}")
        logger.info(f"Avatar ID: {request.avatar_id}")
        logger.info(f"Voice ID: {request.voice_id}")
        
        # Prepare headers
        headers = {
            "X-Api-Key": settings.heygen_api_key,
            "Content-Type": "application/json"
        }

        # Prepare payload
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": request.avatar_id,
                        "avatar_style": request.avatar_style
                    },
                    "voice": {
                        "type": "text", 
                        "input_text": request.text,
                        "voice_id": request.voice_id
                    },
                    "background": {
                        "type": "color",
                        "value": request.background_color
                    }
                }
            ],
            "dimension": {
                "width": request.width,
                "height": request.height
            }
        }

        # Generate video
        generate_url = f"{settings.heygen_base_url}/video/generate"
        logger.info(f"Making request to: {generate_url}")
        
        response = requests.post(generate_url, headers=headers, data=json.dumps(payload))
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        try:
            result = response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {response.text}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from HeyGen: {response.text}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HeyGen API error: {result}")

        video_id = result.get("data", {}).get("video_id")
        if not video_id:
            raise HTTPException(status_code=500, detail="Failed to get video_id from HeyGen")

        logger.info(f"Video generation started with ID: {video_id}")

        # Optional: Wait for video completion and get URLs
        # You can uncomment this if you want to wait for completion in the generate endpoint
        # video_url, s3_url = await wait_for_video_completion(video_id)
        
        return HeyGenResponse(
            video_id=video_id,
            status="processing",
            message="Video generation started successfully. Use /status/{video_id} to check completion and get video URLs.",
            video_url=None,
            s3_url=None,
            estimated_time=60  # seconds
        )

    except requests.RequestException as e:
        logger.error(f"HeyGen API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

async def wait_for_video_completion(video_id: str, max_wait_seconds: int = 300):
    """
    Wait for video completion and return URLs
    
    Args:
        video_id: The video ID to wait for
        max_wait_seconds: Maximum time to wait in seconds (default 5 minutes)
    
    Returns:
        Tuple of (video_url, s3_url)
    """
    import asyncio
    
    wait_time = 0
    check_interval = 10  # Check every 10 seconds
    
    while wait_time < max_wait_seconds:
        try:
            # Check video status
            headers = {"X-Api-Key": settings.heygen_api_key}
            status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
            
            response = requests.get(status_url, headers=headers)
            status_data = response.json()
            
            if response.status_code == 200:
                data = status_data.get("data", {})
                status = data.get("status")
                
                if status == "completed":
                    video_url = data.get("video_url")
                    s3_url = None
                    
                    # Upload to S3
                    if video_url:
                        try:
                            logger.info(f"Uploading completed video {video_id} to S3...")
                            s3_url = s3_service.upload_video_from_url(video_url, video_id)
                        except Exception as e:
                            logger.error(f"Error uploading video to S3: {str(e)}")
                    
                    return video_url, s3_url
                
                elif status == "failed" or status == "error":
                    logger.error(f"Video generation failed for {video_id}")
                    return None, None
            
            # Wait before next check
            await asyncio.sleep(check_interval)
            wait_time += check_interval
            
        except Exception as e:
            logger.error(f"Error checking video status: {str(e)}")
            await asyncio.sleep(check_interval)
            wait_time += check_interval
    
    logger.warning(f"Video {video_id} did not complete within {max_wait_seconds} seconds")
    return None, None

@router.post("/generate-and-wait", response_model=HeyGenResponse)
async def generate_video_and_wait(
    request: HeyGenRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate AI video and wait for completion to return URLs immediately"""
    try:
        # Log configuration for debugging
        logger.info(f"HeyGen API Key: {'***' if settings.heygen_api_key else 'NOT SET'}")
        logger.info(f"HeyGen Base URL: {settings.heygen_base_url}")
        logger.info(f"Avatar ID: {request.avatar_id}")
        logger.info(f"Voice ID: {request.voice_id}")
        
        # Prepare headers
        headers = {
            "X-Api-Key": settings.heygen_api_key,
            "Content-Type": "application/json"
        }

        # Prepare payload
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": request.avatar_id,
                        "avatar_style": request.avatar_style
                    },
                    "voice": {
                        "type": "text",
                        "input_text": request.text,
                        "voice_id": request.voice_id
                    },
                    "background": {
                        "type": "color",
                        "value": request.background_color
                    }
                }
            ],
            "dimension": {
                "width": request.width,
                "height": request.height
            }
        }

        # Generate video
        generate_url = f"{settings.heygen_base_url}/video/generate"
        logger.info(f"Making request to: {generate_url}")
        
        response = requests.post(generate_url, headers=headers, data=json.dumps(payload))
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        try:
            result = response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {response.text}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from HeyGen: {response.text}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HeyGen API error: {result}")

        video_id = result.get("data", {}).get("video_id")
        if not video_id:
            raise HTTPException(status_code=500, detail="Failed to get video_id from HeyGen")

        logger.info(f"Video generation started with ID: {video_id}, waiting for completion...")

        # Wait for video completion
        video_url, s3_url = await wait_for_video_completion(video_id)
        
        if video_url:
            return HeyGenResponse(
                video_id=video_id,
                status="completed",
                message="Video generation completed successfully",
                video_url=video_url,
                s3_url=s3_url,
                estimated_time=0
            )
        else:
            return HeyGenResponse(
                video_id=video_id,
                status="failed",
                message="Video generation failed or timed out",
                video_url=None,
                s3_url=None,
                estimated_time=0
            )

    except requests.RequestException as e:
        logger.error(f"HeyGen API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

@router.get("/status/{video_id}", response_model=HeyGenResponse)
async def get_video_status(
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """Check video generation status"""
    try:
        headers = {"X-Api-Key": settings.heygen_api_key}
        # Use v1 API for status checking (v2 doesn't seem to have status endpoint)
        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        
        logger.info(f"Checking video status at: {status_url}")
        response = requests.get(status_url, headers=headers)
        logger.info(f"Status response code: {response.status_code}")
        logger.info(f"Status response text: {response.text}")
        
        try:
            status_data = response.json()
        except ValueError as e:
            logger.error(f"Failed to parse status JSON response: {response.text}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from HeyGen status API: {response.text}")

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HeyGen status API error: {status_data}")

        data = status_data.get("data", {})
        status = data.get("status")
        
        if status == "completed":
            video_url = data.get("video_url")
            s3_url = None
            
            # Upload video to S3 if video_url is available
            if video_url:
                try:
                    logger.info(f"Uploading video {video_id} to S3...")
                    s3_url = s3_service.upload_video_from_url(video_url, video_id)
                    if s3_url:
                        logger.info(f"Video successfully uploaded to S3: {s3_url}")
                    else:
                        logger.warning(f"Failed to upload video {video_id} to S3")
                except Exception as e:
                    logger.error(f"Error uploading video to S3: {str(e)}")
            
            return HeyGenResponse(
                video_id=video_id,
                status="completed",
                message="Video generation completed and uploaded to S3",
                video_url=video_url,
                s3_url=s3_url,
                estimated_time=0
            )
        elif status == "failed" or status == "error":
            return HeyGenResponse(
                video_id=video_id,
                status="failed", 
                message="Video generation failed",
                video_url=None,
                s3_url=None,
                estimated_time=0
            )
        else:
            return HeyGenResponse(
                video_id=video_id,
                status="processing",
                message="Video is still being generated",
                video_url=None,
                s3_url=None,
                estimated_time=30
            )

    except requests.RequestException as e:
        logger.error(f"HeyGen status API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check video status: {str(e)}")
    except Exception as e:
        logger.error(f"Video status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check video status: {str(e)}")

@router.get("/health")
async def heygen_health_check():
    """HeyGen service health check"""
    s3_status = s3_service.check_connection()
    return {
        "status": "healthy", 
        "service": "heygen",
        "s3_connection": s3_status
    }

@router.get("/videos")
async def list_s3_videos(api_key: str = Depends(get_api_key)):
    """List all videos stored in S3"""
    try:
        videos = s3_service.list_videos()
        return {
            "videos": videos,
            "count": len(videos)
        }
    except Exception as e:
        logger.error(f"Error listing S3 videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list videos: {str(e)}")

@router.delete("/videos/{video_key:path}")
async def delete_s3_video(video_key: str, api_key: str = Depends(get_api_key)):
    """Delete a video from S3"""
    try:
        success = s3_service.delete_video(video_key)
        if success:
            return {"message": f"Video {video_key} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Video not found or could not be deleted")
    except Exception as e:
        logger.error(f"Error deleting S3 video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete video: {str(e)}")

@router.post("/upload-to-s3")
async def upload_video_to_s3(
    video_url: str,
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """Manually upload a video from URL to S3"""
    try:
        s3_url = s3_service.upload_video_from_url(video_url, video_id)
        if s3_url:
            return {
                "message": "Video uploaded successfully",
                "s3_url": s3_url,
                "video_id": video_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload video to S3")
    except Exception as e:
        logger.error(f"Error uploading video to S3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")
