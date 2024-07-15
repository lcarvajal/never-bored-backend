import os, logging
from functools import lru_cache
from fastapi.security import HTTPBearer
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Use a simple bearer scheme as auth is handled by firebase and not fastapi
bearer_scheme = HTTPBearer(auto_error=False)

class Settings(BaseSettings):
    """Main settings"""
    app_name: str = "demofirebase"
    env: str = os.getenv("ENV", "development")
    frontend_url: str = os.getenv("FRONTEND_URL", "NA")

@lru_cache
def get_settings() -> Settings:
    """Retrieves the fastapi settings"""
    return Settings()
