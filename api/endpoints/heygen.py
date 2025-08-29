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

router = APIRouter(prefix="/heygen")
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=HeyGenResponse)
async def generate_video(
    request: HeyGenRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate AI video using HeyGen API"""
    try:
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
        response = requests.post(generate_url, headers=headers, data=json.dumps(payload))
        result = response.json()
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HeyGen API error: {result}")

        video_id = result.get("data", {}).get("video_id")
        if not video_id:
            raise HTTPException(status_code=500, detail="Failed to get video_id from HeyGen")

        logger.info(f"Video generation started with ID: {video_id}")

        return HeyGenResponse(
            video_id=video_id,
            status="processing",
            message="Video generation started successfully",
            video_url=None,
            estimated_time=60  # seconds
        )

    except requests.RequestException as e:
        logger.error(f"HeyGen API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

@router.get("/status/{video_id}", response_model=HeyGenResponse)
async def get_video_status(
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """Check video generation status"""
    try:
        headers = {"X-Api-Key": settings.heygen_api_key}
        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        
        response = requests.get(status_url, headers=headers)
        status_data = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HeyGen status API error: {status_data}")

        data = status_data.get("data", {})
        status = data.get("status")
        
        if status == "completed":
            video_url = data.get("video_url")
            return HeyGenResponse(
                video_id=video_id,
                status="completed",
                message="Video generation completed",
                video_url=video_url,
                estimated_time=0
            )
        elif status == "failed":
            return HeyGenResponse(
                video_id=video_id,
                status="failed", 
                message="Video generation failed",
                video_url=None,
                estimated_time=0
            )
        else:
            return HeyGenResponse(
                video_id=video_id,
                status="processing",
                message="Video is still being generated",
                video_url=None,
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
    return {"status": "healthy", "service": "heygen"}
