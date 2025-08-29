import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Model Configuration
        self.model_name: str = os.getenv("MODEL_NAME", "gemma-3-27b-it")
        
        # API Keys
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.heygen_api_key: str = os.getenv("HEYGEN_API_KEY", "")
        
        # Application Configuration
        self.app_name: str = os.getenv("APP_NAME", "EmotiCare Support API")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8090"))
        
        # HeyGen Configuration
        self.heygen_base_url: str = os.getenv("HEYGEN_BASE_URL", "https://api.heygen.com/v2")
        self.default_avatar_id: str = os.getenv("DEFAULT_AVATAR_ID", "Daisy-inskirt-20220818")
        self.default_voice_id: str = os.getenv("DEFAULT_VOICE_ID", "2d5b0e6cf36f460aa7fc47e3eee4ba54")
        
        # Environment
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        
    def validate(self):
        if not self.google_api_key:
            raise ValueError("Google API key is required")
        if not self.heygen_api_key:
            print("Warning: HeyGen API key not provided. HeyGen endpoints will not function.")

settings = Settings()