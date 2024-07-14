from fastapi import APIRouter, Depends
from typing import Annotated
from app.config import get_firebase_user_from_token, upload_blob
import json

router = APIRouter()

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}

@router.post("/profile")
def post_profile(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Uploads profile to azure blob storage"""
    uid = user["uid"]
    email = user["email"]

    file_name = "username.json"
    profile = {
        "email": email,
        "uid": uid
    }
    file_content = json.dumps(profile)

    upload_blob(file_name, file_content)


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}