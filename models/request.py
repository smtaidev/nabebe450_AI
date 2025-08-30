from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class EmotionType(str, Enum):
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    GRIEF = "grief"
    ANGER = "anger"
    LONELINESS = "loneliness"
    GENERAL = "general"

class EmotiCareRequest(BaseModel):
    patient_message: str = Field(..., description="Patient's message describing their emotional state")
    emotion_type: Optional[EmotionType] = Field(None, description="Type of emotion the patient is experiencing")
    urgency_level: Optional[int] = Field(1, ge=1, le=5, description="Urgency level from 1 (low) to 5 (high)")
    patient_id: Optional[str] = Field(None, description="Optional patient identifier")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    context: Optional[str] = Field(None, description="Additional context about the patient's situation")

class PrescriptionAnalysisRequest(BaseModel):
    patient_id: Optional[str] = Field(None, description="Optional patient identifier")
    additional_notes: Optional[str] = Field(None, description="Additional notes about the prescription")

class SurgiSmartRequest(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    surgery_type: str = Field(..., description="Type of surgery")
    sex: str = Field(..., description="Patient's sex/gender")
    blood_group: str = Field(..., description="Patient's blood group")
    height_in_cm: int = Field(..., description="Patient's height in centimeters")
    weight: int = Field(..., description="Patient's weight in kg")
    date_of_birth: str = Field(..., description="Patient's date of birth (YYYY-MM-DD)")

class WoundMonitoringRequest(BaseModel):
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    wound_location: Optional[str] = Field(None, description="Location of the wound (e.g., 'abdomen', 'knee', 'arm')")
    days_post_surgery: Optional[int] = Field(None, description="Number of days since surgery")
    additional_notes: Optional[str] = Field(None, description="Additional notes about the wound or symptoms")

class HeyGenRequest(BaseModel):
    text: str = Field(..., description="Text to be spoken in the video")
    avatar_id: str = Field("Daisy-inskirt-20220818", description="HeyGen avatar ID")
    avatar_style: str = Field("normal", description="Avatar style")
    voice_id: str = Field("2d5b0e6cf36f460aa7fc47e3eee4ba54", description="Voice ID for text-to-speech")
    background_color: str = Field("#FFFFFF", description="Background color")
    width: int = Field(1280, description="Video width")
    height: int = Field(720, description="Video height")

class MedicationRequest(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    medication_name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Dosage amount (e.g., '500mg')")
    frequency: str = Field(..., description="Frequency (e.g., 'twice daily')")
    duration: Optional[str] = Field(None, description="Duration of treatment")
    instructions: Optional[str] = Field(None, description="Special instructions")
    start_date: Optional[str] = Field(None, description="Start date of medication")
    end_date: Optional[str] = Field(None, description="End date of medication")

class MedicationUpdateRequest(BaseModel):
    medication_name: Optional[str] = Field(None, description="Name of the medication")
    dosage: Optional[str] = Field(None, description="Dosage amount")
    frequency: Optional[str] = Field(None, description="Frequency")
    duration: Optional[str] = Field(None, description="Duration of treatment")
    instructions: Optional[str] = Field(None, description="Special instructions")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")
    is_active: Optional[bool] = Field(None, description="Whether medication is active")