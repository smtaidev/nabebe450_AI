from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import Optional
import logging

from models.response import PrescriptionAnalysisResponse
from services.gemma_service import gemma_service
from core.dependencies import get_api_key

router = APIRouter(prefix="/prescription")
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=PrescriptionAnalysisResponse)
async def analyze_prescription(
    prescription_image: UploadFile = File(..., description="Prescription image (JPG, PNG, etc.)"),
    patient_id: Optional[str] = Form(None, description="Optional patient identifier"),
    additional_notes: Optional[str] = Form(None, description="Additional notes about the prescription"),
    api_key: str = Depends(get_api_key)
):
    """Analyze prescription image and extract medication information using AI."""
    try:
        # Validate file type
        if not prescription_image.content_type or not prescription_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPG, PNG, GIF, etc.)"
            )
        
        # Check file size (limit to 10MB)
        if prescription_image.size and prescription_image.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 10MB"
            )
        
        # Read image data
        image_data = await prescription_image.read()
        
        # Analyze the prescription using Gemma service
        analysis_result = await gemma_service.analyze_prescription(
            image_data=image_data,
            patient_id=patient_id
        )
        
        # Create response object
        response_data = {
            "medications": [
                {
                    "name": med.get("name", ""),
                    "dosage": med.get("dosage"),
                    "frequency": med.get("frequency"),
                    "duration": med.get("duration"),
                    "instructions": med.get("instructions")
                }
                for med in analysis_result.get("medications", [])
            ],
            "doctor_name": analysis_result.get("doctor_name"),
            "patient_name": analysis_result.get("patient_name"),
            "prescription_date": analysis_result.get("prescription_date"),
            "additional_notes": additional_notes or analysis_result.get("additional_notes"),
            "confidence_score": analysis_result.get("confidence_score"),
            "raw_text": analysis_result.get("raw_text")
        }
        
        logger.info(f"Successfully analyzed prescription for patient: {patient_id}")
        
        return PrescriptionAnalysisResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing prescription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze prescription: {str(e)}"
        )

@router.get("/health")
async def prescription_health_check():
    """Health check endpoint for prescription analysis service"""
    return {"status": "healthy", "service": "prescription_analysis"}
