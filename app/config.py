import logging
import os
import pathlib
from functools import lru_cache
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import credentials, initialize_app, auth
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

def get_firebase_user_from_token(
    token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> Optional[dict]:
    """Uses bearer token to identify firebase user id

    Args:
        token : the bearer token. Can be None as we set auto_error to False

    Returns:
        dict: the firebase user on success
    Raises:
        HTTPException 401 if user does not exist or token is invalid
    """
    try:
        if not token:
            raise ValueError("No token provided")
        logger.info(f"Token received: {token.credentials}")
        user = auth.verify_id_token(token.credentials)
        logger.info(f"User verified: {user}")
        return user
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

