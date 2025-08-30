# EmotiCare API

A comprehensive FastAPI-based healthcare support system with AI-powered emotional care, prescription analysis, surgery simulation, and video generation capabilities.

## Features

- **EmotiCare Support**: AI-powered emotional support for patients
- **Prescription Analysis**: AI-powered prescription image analysis and medication extraction
- **SurgiSmart**: Surgery simulation with 3-minute educational scripts
- **HeyGen Integration**: AI video generation for healthcare content
- **Wound Monitoring**: AI-powered wound healing analysis from uploaded photos

## API Endpoints

### EmotiCare Support
- `POST /api/v1/emoticare/support` - Get emotional support

### Prescription Analysis
- `POST /api/v1/prescription/analyze` - Analyze prescription images

### SurgiSmart Simulation
- `POST /api/v1/surgismart/simulate` - Generate surgery simulation with 3-minute script

### HeyGen Video Generation
- `POST /api/v1/heygen/generate` - Generate AI videos
- `GET /api/v1/heygen/status/{video_id}` - Check video generation status

### Wound Monitoring
- `POST /api/v1/wound-monitoring/analyze` - Analyze wound healing from uploaded photos

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key
- HeyGen API key (optional)

### Environment Setup

1. Configure environment variables in `.env` file:
```bash
# API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
HEYGEN_API_KEY=your_heygen_api_key_here

# Model Configuration
MODEL_NAME=gemma-3-27b-it

# Application Configuration
APP_NAME=EmotiCare Support API
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8090

# HeyGen Configuration
HEYGEN_BASE_URL=https://api.heygen.com/v2
DEFAULT_AVATAR_ID=Daisy-inskirt-20220818
DEFAULT_VOICE_ID=2d5b0e6cf36f460aa7fc47e3eee4ba54

# Environment
ENVIRONMENT=production
```

### Docker Deployment

#### Using Docker Compose (Recommended)

1. Build and start the application:
```bash
docker-compose up --build
```

2. The API will be available at:
- API: http://localhost:8090
- Interactive Docs: http://localhost:8090/docs
- ReDoc: http://localhost:8090/redoc

#### Using Docker directly

1. Build the Docker image:
```bash
docker build -t emoticare-api .
```

2. Run the container:
```bash
docker run -d \
  --name emoticare-api \
  -p 8090:8090 \
  --env-file .env \
  emoticare-api
```

## API Usage Examples

### SurgiSmart Simulation (3-minute script)
```bash
curl -X POST "http://localhost:8090/api/v1/surgismart/simulate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "patient_id": "P12345",
    "surgery_type": "Laparoscopic Cholecystectomy",
    "sex": "female",
    "blood_group": "O+",
    "height_in_cm": 165,
    "weight": 70,
    "date_of_birth": "1985-03-15"
  }'
```

## Configuration

All configuration is managed through environment variables defined in the `.env` file. The API keys are now securely stored in environment variables instead of being hardcoded.
- **Text Completion**: Text generation and completion capabilities

## Project Structure

```
nabebe450/
├── app/
│   ├── __init__.py
│   └── main.py                 # FastAPI application entry point
├── api/
│   ├── __init__.py
│   └── endpoints/
│       ├── __init__.py
│       ├── emoticare.py        # EmotiCare support endpoints
│       ├── chat.py             # General chat endpoints
│       └── completion.py       # Text completion endpoints
├── core/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   └── dependencies.py        # Dependency injection
├── models/
│   ├── __init__.py
│   ├── request.py             # Request models
│   └── response.py            # Response models
├── services/
│   ├── __init__.py
│   └── gemma_service.py       # Gemma AI service
├── requirements.txt
├── .env                       # Environment variables
└── README.md
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   
   Make sure your `.env` file contains:
   ```env
   model_name=gemma-3-27b-it
   google_api_key=YOUR_GOOGLE_API_KEY
   ```

3. **Run the Application**
   ```bash
   cd app
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
   ```

## API Endpoints

### 1. EmotiCare Support
**POST** `/api/v1/emoticare/support`

Provides emotional support and guidance to patients experiencing various emotional states.

```json
{
  "patient_message": "I'm feeling very anxious about my upcoming surgery",
  "emotion_type": "anxiety",
  "urgency_level": 3,
  "patient_id": "patient_123",
  "context": "Patient has upcoming surgery next week"
}
```

### 2. Prescription Analysis 📋
**POST** `/api/v1/prescription/analyze`

Upload a prescription image and get AI-powered medication extraction and analysis.

**Form Data:**
- `prescription_image`: Image file (JPG, PNG, etc.)
- `patient_id`: Optional patient identifier
- `additional_notes`: Optional notes about the prescription

**Response:**
```json
{
  "medications": [
    {
      "name": "Amoxicillin",
      "dosage": "500mg",
      "frequency": "Three times daily",
      "duration": "7 days",
      "instructions": "Take with food"
    }
  ],
  "doctor_name": "Dr. Smith",
  "patient_name": "John Doe",
  "prescription_date": "2025-08-27",
  "confidence_score": 0.85,
  "raw_text": "Full extracted text from image"
}
```

### 3. General Chat
**POST** `/api/v1/chat/`

General conversation endpoint for basic AI interactions.

### 4. Text Completion
**POST** `/api/v1/completion/`

Generate text completions based on prompts.

#### POST `/api/v1/emoticare/crisis-assessment`
Specialized crisis assessment for high-urgency situations.

#### GET `/api/v1/emoticare/resources?emotion_type=anxiety`
Get mental health resources by emotion type.

### General Chat

#### POST `/api/v1/chat/`
General conversational AI interactions.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_history": []
}
```

### Text Completion

#### POST `/api/v1/completion/`
Generate text completions.

**Request Body:**
```json
{
  "prompt": "Write a motivational message about...",
  "max_tokens": 512,
  "temperature": 0.7
}
```

## Emotion Types Supported

- `anxiety`
- `depression`
- `stress`
- `grief`
- `anger`
- `loneliness`
- `general`

## Urgency Levels

1. **Low** - General support needed
2. **Mild** - Some distress
3. **Moderate** - Significant distress
4. **High** - Severe distress
5. **Critical** - Immediate safety concerns

## Crisis Resources

The API provides immediate access to crisis resources including:

- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911
- Online crisis chat support

## Development

### Testing the API

1. Start the server:
   ```bash
   python app/main.py
   ```

2. Visit the interactive API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. Test the EmotiCare endpoint:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/emoticare/support" \
        -H "Content-Type: application/json" \
        -d '{
          "patient_message": "I am feeling overwhelmed with work stress",
          "emotion_type": "stress",
          "urgency_level": 3
        }'
   ```

4. Test the Prescription Analysis endpoint:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/prescription/analyze" \
        -H "X-API-Key: your-api-key" \
        -F "prescription_image=@prescription.jpg" \
        -F "patient_id=patient_123"
   ```

### Health Checks

- Main health check: `GET /health`
- Service-specific health checks:
  - EmotiCare: `GET /api/v1/emoticare/health`
  - Prescription Analysis: `GET /api/v1/prescription/health`
  - Chat: `GET /api/v1/chat/health`
  - Completion: `GET /api/v1/completion/health`

## Important Notes

⚠️ **Disclaimer**: This API provides AI-generated emotional support and should not replace professional mental health care. For emergencies, always contact local emergency services or crisis hotlines.

## License

MIT License

## Support

For support, please contact the EmotiCare Support Team at support@emoticare.com
