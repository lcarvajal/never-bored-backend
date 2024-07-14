from fastapi import APIRouter, Depends
from typing import Annotated
from app.config import get_firebase_user_from_token, upload_blob
import json
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}

class Profile(BaseModel):
    name: str
    email: str
    goal: str
    reason: str
    deadline: str
    lastLearnedDescription: str

@router.post("/profiles")
def post_profile(profile: Profile):
    """Uploads profile to azure blob storage"""
    file_name = f'profile-{profile.email}.json'
    profile = {
        "name": profile.name,
        "email": profile.email,
        "goal": profile.goal,
        "reason": profile.reason,
        "deadline": profile.deadline,
        "lastLearnedDescription": profile.lastLearnedDescription
    }
    file_content = json.dumps(profile)

    upload_blob(file_name, file_content)

# @router.get("/roadmap")
# def post_profile(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
#     """Generates a learning path based on the user profile"""
#     file_name = "username.json"
#     file_content = '{"email": "p5q5y@example.com", "id": "username"}'
#     upload_blob(file_name, file_content)

@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}