from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import uuid
import logging
from datetime import datetime

from models.request import EmotiCareRequest
from models.response import EmotiCareResponse
from services.gemma_service import gemma_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emoticare", tags=["EmotiCare Support"])

@router.post("/support", response_model=EmotiCareResponse)
async def get_emoticare_support(request: EmotiCareRequest):
    """
    Provide emotional support to patients using AI-powered responses.
    
    This endpoint analyzes the patient's emotional state and provides:
    - Empathetic and supportive responses
    - Emotion detection and urgency assessment
    - Recommended coping strategies
    - Mental health resources when appropriate
    """
    try:
        logger.info(f"EmotiCare support request received for emotion: {request.emotion_type}")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate AI response using Gemma service
        ai_response = await gemma_service.generate_emoticare_response(
            patient_message=request.patient_message,
            emotion_type=request.emotion_type.value if request.emotion_type else None,
            urgency_level=request.urgency_level,
            context=request.context
        )
        
        # Create response
        response = EmotiCareResponse(
            response_message=ai_response["response_message"],
            emotion_detected=ai_response.get("emotion_detected"),
            support_type=ai_response["support_type"],
            urgency_assessment=ai_response.get("urgency_assessment"),
            recommended_actions=ai_response.get("recommended_actions", []),
            resources=ai_response.get("resources", []),
            session_id=session_id,
            confidence_score=ai_response.get("confidence_score")
        )
        
        logger.info(f"EmotiCare response generated successfully for session: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in emoticare support endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to provide emotional support: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the EmotiCare service"""
    return {
        "status": "healthy",
        "service": "EmotiCare Support API",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }
