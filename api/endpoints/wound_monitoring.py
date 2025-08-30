from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List
import logging
import uuid
import io
from PIL import Image
from datetime import datetime

from models.request import WoundMonitoringRequest
from models.response import WoundMonitoringResponse
from services.gemma_service import gemma_service
from core.dependencies import get_api_key

router = APIRouter(prefix="/wound-monitoring")
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=WoundMonitoringResponse)
async def analyze_wound(
    file: UploadFile = File(...),
    patient_id: Optional[str] = None,
    wound_location: Optional[str] = None,
    days_post_surgery: Optional[int] = None,
    additional_notes: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """
    Analyze wound healing progress from uploaded photo.
    
    Upload a photo of surgical site for AI-powered healing analysis including:
    - Wound healing assessment
    - Infection risk evaluation
    - Healing progress tracking
    - Care recommendations
    
    Note: We don't support images of private parts and face for privacy protection.
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read and validate image
        try:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image validation
            if image.size[0] < 100 or image.size[1] < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Image resolution too low. Please upload a clearer image."
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Please upload a valid image."
            )
        
        # Create request object for processing
        wound_request = {
            "patient_id": patient_id,
            "wound_location": wound_location,
            "days_post_surgery": days_post_surgery,
            "additional_notes": additional_notes,
            "image_size": image.size,
            "image_format": image.format
        }
        
        # Analyze wound using Gemma service
        analysis_result = await gemma_service.analyze_wound_healing(
            image_data=image_data,
            wound_info=wound_request
        )
        
        # Create complete response
        response_data = {
            "analysis_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "wound_location": wound_location or "Not specified",
            "days_post_surgery": days_post_surgery,
            **analysis_result
        }
        
        logger.info(f"Successfully analyzed wound for patient: {patient_id}")
        
        return WoundMonitoringResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing wound: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze wound: {str(e)}"
        )

@router.get("/health")
async def wound_monitoring_health_check():
    """Health check endpoint for wound monitoring service"""
    return {"status": "healthy", "service": "wound-monitoring"}
