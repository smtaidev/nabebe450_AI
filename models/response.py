from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmotiCareResponse(BaseModel):
    response_message: str = Field(..., description="AI-generated supportive response")
    emotion_detected: Optional[str] = Field(None, description="Detected emotion from the message")
    support_type: str = Field(..., description="Type of support provided (emotional, practical, etc.)")
    urgency_assessment: Optional[int] = Field(None, ge=1, le=5, description="AI's assessment of urgency level")
    recommended_actions: Optional[List[str]] = Field([], description="Recommended actions for the patient")
    resources: Optional[List[Dict[str, str]]] = Field([], description="Helpful resources (links, contacts, etc.)")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in the response")

class Medication(BaseModel):
    name: str = Field(..., description="Medication name")
    dosage: Optional[str] = Field(None, description="Dosage amount (e.g., '500mg')")
    frequency: Optional[str] = Field(None, description="Frequency of taking (e.g., 'twice daily')")
    duration: Optional[str] = Field(None, description="Duration of treatment")
    instructions: Optional[str] = Field(None, description="Special instructions")

class PrescriptionAnalysisResponse(BaseModel):
    medications: List[Medication] = Field(..., description="List of extracted medications")
    doctor_name: Optional[str] = Field(None, description="Doctor's name if detected")
    patient_name: Optional[str] = Field(None, description="Patient's name if detected")
    prescription_date: Optional[str] = Field(None, description="Prescription date if detected")
    additional_notes: Optional[str] = Field(None, description="Additional notes or instructions")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in extraction")
    raw_text: Optional[str] = Field(None, description="Raw extracted text from image")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class SurgeryStep(BaseModel):
    step_number: int = Field(..., description="Step sequence number")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Detailed step description")
    duration_minutes: Optional[int] = Field(None, description="Estimated duration in minutes")

class SurgiSmartResponse(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    surgery_type: str = Field(..., description="Type of surgery")
    simulation_id: str = Field(..., description="Unique simulation identifier")
    surgery_script: str = Field(..., description="3-minute surgery studies simulation script")
    overview: str = Field(..., description="Surgery overview and description")
    patient_suitability: str = Field(..., description="Patient suitability assessment")
    procedure_steps: List[SurgeryStep] = Field(..., description="Detailed surgery steps")
    estimated_duration: int = Field(..., description="Total estimated surgery duration in minutes")
    risk_factors: List[str] = Field(..., description="Risk factors specific to this patient")
    post_operative_care: List[str] = Field(..., description="Post-operative care instructions")
    success_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Success rate percentage")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in analysis")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class HeyGenResponse(BaseModel):
    video_id: str = Field(..., description="Unique video identifier")
    status: str = Field(..., description="Video generation status (processing, completed, failed)")
    message: str = Field(..., description="Status message")
    video_url: Optional[str] = Field(None, description="Download URL when video is ready")
    estimated_time: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")