from datetime import datetime
from typing import Optional
import logging
from fastapi import Header

logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("emoticare.log")
        ]
    )

async def validate_api_key() -> bool:
    """Validate that API key is configured"""
    from core.config import settings
    return bool(settings.google_api_key)

async def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Get API key from header or use default"""
    from core.config import settings
    return x_api_key or settings.google_api_key