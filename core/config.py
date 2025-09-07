import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Model Configuration
        model_name_env = os.getenv("MODEL_NAME", "")
        self.model_name: str = model_name_env.strip() if model_name_env.strip() else "gemma-3-27b-it"
        
        # API Keys
        google_api_key_env = os.getenv("GOOGLE_API_KEY", "")
        self.google_api_key: str = google_api_key_env.strip() if google_api_key_env else ""
        heygen_api_key_env = os.getenv("HEYGEN_API_KEY", "")
        self.heygen_api_key: str = heygen_api_key_env.strip() if heygen_api_key_env else ""
        
        # Application Configuration
        app_name_env = os.getenv("APP_NAME", "")
        self.app_name: str = app_name_env if app_name_env.strip() else "EmotiCare Support API"
        app_version_env = os.getenv("APP_VERSION", "")
        self.app_version: str = app_version_env.strip() if app_version_env.strip() else "1.0.0"
        host_env = os.getenv("HOST", "")
        self.host: str = host_env.strip() if host_env.strip() else "0.0.0.0"
        port_str = os.getenv("PORT", "8090")
        self.port: int = int(port_str) if port_str and port_str.strip().isdigit() else 8090
        
        # HeyGen Configuration
        heygen_base_url_env = os.getenv("HEYGEN_BASE_URL", "")
        self.heygen_base_url: str = heygen_base_url_env.strip() if heygen_base_url_env.strip() else "https://api.heygen.com/v2"
        default_avatar_id_env = os.getenv("DEFAULT_AVATAR_ID", "")
        self.default_avatar_id: str = default_avatar_id_env.strip() if default_avatar_id_env.strip() else "Daisy-inskirt-20220818"
        default_voice_id_env = os.getenv("DEFAULT_VOICE_ID", "")
        self.default_voice_id: str = default_voice_id_env.strip() if default_voice_id_env.strip() else "2d5b0e6cf36f460aa7fc47e3eee4ba54"
        
        # Environment
        environment_env = os.getenv("ENVIRONMENT", "")
        self.environment: str = environment_env.strip() if environment_env.strip() else "development"
        
        # S3 Configuration (DigitalOcean Spaces)
        s3_access_key_env = os.getenv("S3_ACCESS_KEY", "")
        self.s3_access_key: str = s3_access_key_env.strip() if s3_access_key_env else ""
        s3_secret_key_env = os.getenv("S3_SECRET_KEY", "")
        self.s3_secret_key: str = s3_secret_key_env.strip() if s3_secret_key_env else ""
        s3_region_env = os.getenv("S3_REGION", "")
        self.s3_region: str = s3_region_env.strip() if s3_region_env.strip() else "nyc3"
        s3_bucket_name_env = os.getenv("S3_BUCKET_NAME", "")
        self.s3_bucket_name: str = s3_bucket_name_env.strip() if s3_bucket_name_env.strip() else "smtech-space"
        s3_endpoint_env = os.getenv("S3_ENDPOINT", "")
        self.s3_endpoint: str = s3_endpoint_env.strip() if s3_endpoint_env.strip() else "https://nyc3.digitaloceanspaces.com/"
        
    def validate(self):
        if not self.google_api_key:
            raise ValueError("Google API key is required")
        if not self.heygen_api_key:
            print("Warning: HeyGen API key not provided. HeyGen endpoints will not function.")

settings = Settings()