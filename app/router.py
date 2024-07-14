from fastapi import APIRouter, Depends
from typing import Annotated
from app.config import get_firebase_user_from_token, upload_blob

router = APIRouter()

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}

@router.post("/profile")
def post_profile(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Uploads profile to azure blob storage"""
    file_name = "username.json"
    file_content = '{"email": "p5q5y@example.com", "username": "username"}'
    upload_blob(file_name, file_content)


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}