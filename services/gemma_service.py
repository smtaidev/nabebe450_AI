import google.generativeai as genai
from typing import Optional, List, Dict, Any
import json
import logging
import io
from PIL import Image
from core.config import settings

logger = logging.getLogger(__name__)

class GemmaService:
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
        
    async def generate_emoticare_response(
        self, 
        patient_message: str, 
        emotion_type: Optional[str] = None,
        urgency_level: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an empathetic and supportive response for emotional care
        """
        try:
            # Create a specialized prompt for emotional support
            system_prompt = """You are a compassionate AI emotional support assistant for EmotiCare. 
            Your role is to provide empathetic, non-judgmental, and helpful responses to patients seeking emotional support.
            
            Guidelines:
            1. Always respond with empathy and understanding
            2. Never provide medical diagnosis or treatment advice
            3. Encourage professional help when appropriate
            4. Provide practical coping strategies when suitable
            5. Validate the patient's feelings
            6. Keep responses supportive but professional
            7. If the situation seems urgent (mentions of self-harm, suicide, etc.), prioritize safety resources
            
            Response format should include:
            - Empathetic acknowledgment
            - Supportive guidance
            - Practical suggestions if appropriate
            - Encouragement to seek professional help when needed
            """
            
            user_prompt = f"""
            Patient Message: {patient_message}
            
            Additional Context:
            - Emotion Type: {emotion_type if emotion_type else 'Not specified'}
            - Urgency Level: {urgency_level if urgency_level else 'Not specified'}
            - Context: {context if context else 'None provided'}
            
            Please provide a compassionate and helpful response.
            """
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(full_prompt)
            
            # Detect emotion and assess urgency
            emotion_detected = await self._detect_emotion(patient_message)
            urgency_assessment = await self._assess_urgency(patient_message)
            
            return {
                "response_message": response.text,
                "emotion_detected": emotion_detected,
                "support_type": "emotional_support",
                "urgency_assessment": urgency_assessment,
                "recommended_actions": await self._get_recommended_actions(emotion_type, urgency_assessment),
                "resources": await self._get_resources(emotion_type, urgency_assessment),
                "confidence_score": 0.85  # This could be improved with actual confidence calculation
            }
            
        except Exception as e:
            logger.error(f"Error generating emoticare response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def _detect_emotion(self, message: str) -> Optional[str]:
        """Detect primary emotion from the message"""
        try:
            emotion_prompt = f"""
            Analyze the following message and identify the primary emotion. 
            Respond with only one word from: anxiety, depression, stress, grief, anger, loneliness, joy, neutral
            
            Message: {message}
            """
            
            response = self.model.generate_content(emotion_prompt)
            return response.text.strip().lower()
        except:
            return None
    
    async def _assess_urgency(self, message: str) -> Optional[int]:
        """Assess urgency level of the message (1-5)"""
        try:
            urgency_prompt = f"""
            Assess the urgency level of this emotional support request on a scale of 1-5:
            1 = Low urgency (general support needed)
            2 = Mild urgency (some distress)
            3 = Moderate urgency (significant distress)
            4 = High urgency (severe distress)
            5 = Critical urgency (immediate safety concerns, mentions of self-harm)
            
            Respond with only the number.
            
            Message: {message}
            """
            
            response = self.model.generate_content(urgency_prompt)
            try:
                return int(response.text.strip())
            except:
                return 3  # Default to moderate if parsing fails
        except:
            return 3
    
    async def _get_recommended_actions(self, emotion_type: Optional[str], urgency: Optional[int]) -> List[str]:
        """Get recommended actions based on emotion type and urgency"""
        actions = []
        
        if urgency and urgency >= 4:
            actions.extend([
                "Consider contacting a mental health professional immediately",
                "Reach out to a trusted friend or family member",
                "Contact a crisis helpline if you're in immediate distress"
            ])
        
        if emotion_type:
            emotion_actions = {
                "anxiety": ["Practice deep breathing exercises", "Try progressive muscle relaxation", "Limit caffeine intake"],
                "depression": ["Maintain a daily routine", "Engage in physical activity", "Connect with supportive people"],
                "stress": ["Take regular breaks", "Practice mindfulness", "Prioritize tasks and delegate when possible"],
                "grief": ["Allow yourself to feel and process emotions", "Seek support from others who understand", "Consider grief counseling"],
                "anger": ["Take time to cool down before reacting", "Practice anger management techniques", "Identify triggers"],
                "loneliness": ["Reach out to friends or family", "Join community activities", "Consider volunteering"]
            }
            actions.extend(emotion_actions.get(emotion_type, []))
        
        return actions[:5]  # Limit to 5 actions
    
    async def _get_resources(self, emotion_type: Optional[str], urgency: Optional[int]) -> List[Dict[str, str]]:
        """Get helpful resources based on emotion type and urgency"""
        resources = []
        
        if urgency and urgency >= 4:
            resources.extend([
                {"type": "crisis_line", "name": "National Suicide Prevention Lifeline", "contact": "988"},
                {"type": "emergency", "name": "Emergency Services", "contact": "911"},
                {"type": "text_support", "name": "Crisis Text Line", "contact": "Text HOME to 741741"}
            ])
        
        # General mental health resources
        resources.extend([
            {"type": "website", "name": "Mental Health America", "url": "https://www.mhanational.org"},
            {"type": "website", "name": "National Alliance on Mental Illness", "url": "https://www.nami.org"},
            {"type": "app", "name": "Mindfulness Apps", "description": "Headspace, Calm, Insight Timer"}
        ])
        
        return resources[:5]  # Limit to 5 resources
    
    async def generate_chat_response(self, message: str, conversation_history: List[dict] = None) -> str:
        """Generate a general chat response"""
        try:
            if conversation_history:
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
                prompt = f"Previous conversation:\n{context}\n\nUser: {message}\n\nAssistant:"
            else:
                prompt = message
                
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_completion(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate text completion"""
        try:
            # Note: Gemini API doesn't directly support temperature and max_tokens like OpenAI
            # These parameters are included for API compatibility
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")

    async def analyze_prescription(self, image_data: bytes, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze prescription image and extract medication information"""
        try:
            # Create a vision model for image analysis
            vision_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Create a detailed prompt for prescription analysis
            analysis_prompt = """
            You are a medical prescription analysis AI. Analyze this prescription image and extract the following information in JSON format:

            {
                "medications": [
                    {
                        "name": "medication name",
                        "dosage": "dosage amount with units",
                        "frequency": "how often to take",
                        "duration": "how long to take",
                        "instructions": "special instructions"
                    }
                ],
                "doctor_name": "doctor's name if visible",
                "patient_name": "patient's name if visible", 
                "prescription_date": "date if visible",
                "additional_notes": "any additional notes or instructions",
                "raw_text": "all text found in the image"
            }

            Important:
            - Be accurate and only extract information that is clearly visible
            - If information is unclear or not visible, use null
            - Pay special attention to medication names, dosages, and frequencies
            - Include any special instructions or warnings
            - Extract all readable text in the raw_text field

            Analyze this prescription image:
            """
            
            # Generate content with the image
            response = vision_model.generate_content([analysis_prompt, image])
            
            # Parse the JSON response
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                analysis_result = json.loads(response_text)
                
                # Add metadata
                analysis_result['confidence_score'] = 0.8  # This could be improved with actual confidence calculation
                analysis_result['patient_id'] = patient_id
                
                return analysis_result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "medications": [],
                    "doctor_name": None,
                    "patient_name": None,
                    "prescription_date": None,
                    "additional_notes": None,
                    "raw_text": response.text,
                    "confidence_score": 0.5,
                    "patient_id": patient_id,
                    "error": "Failed to parse structured data, raw text provided"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing prescription: {str(e)}")
            raise Exception(f"Failed to analyze prescription: {str(e)}")

    async def generate_surgery_simulation(self, patient_data: Dict[str, Any], surgery_type: str) -> Dict[str, Any]:
        """Generate comprehensive surgery simulation with 3-minute script based on patient data"""
        try:
            # Calculate patient age if date of birth is provided
            age = None
            if patient_data.get("date_of_birth"):
                try:
                    from datetime import datetime
                    birth_date = datetime.strptime(patient_data["date_of_birth"], "%Y-%m-%d")
                    age = (datetime.now() - birth_date).days // 365
                except:
                    age = None
            
            # Create detailed prompt for surgery simulation
            simulation_prompt = f"""
            You are an expert surgical consultant AI. Generate a comprehensive surgery simulation report for:
            
            **Surgery Type**: {surgery_type}
            **Patient Information**:
            - Patient ID: {patient_data.get("patient_id", "Not specified")}
            - Age: {age if age else "Not specified"}
            - Sex: {patient_data.get("sex", "Not specified")}
            - Height: {patient_data.get("height_in_cm", "Not specified")} cm
            - Weight: {patient_data.get("weight", "Not specified")} kg
            - Blood Group: {patient_data.get("blood_group", "Not specified")}
            
            Please provide a detailed surgical simulation in JSON format including a 3-minute surgery studies simulation script:
            
            {{
                "surgery_script": "A detailed 3-minute narrated script for surgery studies simulation. This should be educational content that could be read aloud and would take approximately 3 minutes to present. Include patient-specific considerations, surgical techniques, anatomical references, and educational points about the procedure.",
                "overview": "Comprehensive overview of the surgery procedure",
                "patient_suitability": "Assessment of patient's suitability for this surgery based on their specific profile",
                "procedure_steps": [
                    {{
                        "step_number": 1,
                        "title": "Step title",
                        "description": "Detailed description of the surgical step",
                        "duration_minutes": 30
                    }},
                    {{
                        "step_number": 2,
                        "title": "Next step title", 
                        "description": "Detailed description of the next surgical step",
                        "duration_minutes": 45
                    }}
                ],
                "estimated_duration": 180,
                "risk_factors": ["patient-specific risk factors based on age, sex, weight, blood group, etc."],
                "post_operative_care": ["post-operative care instructions tailored to patient profile"],
                "success_rate": 95.5
            }}
            
            **Important Requirements for the surgery_script:**
            1. Must be exactly 3 minutes when read aloud (approximately 450-500 words)
            2. Must be written as a SINGLE CONTINUOUS PARAGRAPH with no line breaks or paragraph breaks
            3. Should be educational and informative for surgery studies
            4. Include patient-specific considerations (age: {age}, sex: {patient_data.get("sex")}, BMI calculations, blood group considerations)
            5. Explain the surgical procedure step by step within the flowing narrative
            6. Mention anatomical structures involved
            7. Discuss potential complications and how to avoid them
            8. Reference modern surgical techniques and equipment
            9. Make it engaging for medical students/residents
            10. Format as one flowing educational narrative without any paragraph breaks
            
            Focus on:
            1. Patient-specific considerations based on their exact profile
            2. Educational value for surgery studies
            3. Step-by-step surgical procedure explanation
            4. Risk assessment tailored to this specific patient
            5. Post-operative care specific to patient needs
            6. Success rates and evidence-based information
            
            Be thorough, accurate, and consider the patient's specific characteristics (age {age}, sex {patient_data.get("sex")}, height {patient_data.get("height_in_cm")}cm, weight {patient_data.get("weight")}kg, blood group {patient_data.get("blood_group")}).
            """
            
            response = self.model.generate_content(simulation_prompt)
            
            # Parse the JSON response
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                simulation_result = json.loads(response_text)
                
                # Add confidence score
                simulation_result['confidence_score'] = 0.9
                
                return simulation_result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic structure from the raw response
                logger.warning("Failed to parse JSON response for surgery simulation")
                return {
                    "overview": f"AI-generated simulation for {surgery_type}. " + response.text[:500],
                    "patient_suitability": "Please consult with a qualified surgeon for detailed assessment.",
                    "procedure_steps": [
                        {
                            "step_number": 1,
                            "title": "Initial Assessment",
                            "description": "Comprehensive patient evaluation and preparation",
                            "duration_minutes": 30,
                            "risks": ["General surgical risks"],
                            "critical_points": ["Patient monitoring", "Safety protocols"]
                        }
                    ],
                    "estimated_duration": 180,
                    "risk_factors": ["General surgical risks - consult surgeon"],
                    "post_operative_care": ["Follow post-operative protocols", "Regular monitoring"],
                    "success_rate": 85.0,
                    "contraindications": ["Standard contraindications apply"],
                    "alternative_treatments": ["Consult with surgeon for alternatives"],
                    "preparation_instructions": ["Follow pre-surgical guidelines"],
                    "confidence_score": 0.6,
                    "note": "Detailed analysis requires clinical evaluation"
                }
                
        except Exception as e:
            logger.error(f"Error generating surgery simulation: {str(e)}")
            raise Exception(f"Failed to generate surgery simulation: {str(e)}")

# Global service instance
gemma_service = GemmaService()