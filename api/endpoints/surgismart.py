from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import uuid
import logging
from datetime import datetime, date

from models.request import SurgiSmartRequest
from models.response import SurgiSmartResponse, SurgeryStep
from services.gemma_service import gemma_service
from core.dependencies import get_api_key

router = APIRouter(prefix="/surgismart", tags=["SurgiSmart"])
logger = logging.getLogger(__name__)

@router.post("/simulate", response_model=SurgiSmartResponse)
async def simulate_surgery(
    request: SurgiSmartRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Generate surgery simulation with 3-minute script based on patient data.
    
    Accepts patient information including:
    - patient_id: Patient identifier
    - surgery_type: Type of surgery to simulate
    - sex: Patient's sex/gender
    - blood_group: Patient's blood group
    - height_in_cm: Patient's height in centimeters
    - weight: Patient's weight in kg
    - date_of_birth: Patient's date of birth (YYYY-MM-DD format)
    
    Returns a comprehensive surgery simulation including a 3-minute educational script.
    """
    try:
        # Generate simulation using Gemma service
        simulation_result = await gemma_service.generate_surgery_simulation(
            patient_data=request.dict(),
            surgery_type=request.surgery_type
        )
        
        # Create complete response with required fields
        response_data = {
            "patient_id": request.patient_id,
            "surgery_type": request.surgery_type,
            "simulation_id": str(uuid.uuid4()),
            **simulation_result  # Merge the AI-generated content
        }
        
        logger.info(f"Successfully generated surgery simulation for patient: {request.patient_id}")
        
        return SurgiSmartResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error generating surgery simulation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate surgery simulation: {str(e)}"
        )


