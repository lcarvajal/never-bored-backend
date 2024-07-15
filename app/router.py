from fastapi import APIRouter, Depends
from typing import Annotated
from app.config import get_firebase_user_from_token, upload_blob, download_blob
import json, logging
from pydantic import BaseModel

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}

class Profile(BaseModel):
    uid: str
    name: str
    email: str
    goal: str

@router.post("/profiles")
def post_profiles(user: Annotated[dict, Depends(get_firebase_user_from_token)], profile: Profile):
    """Uploads profile to azure blob storage"""
    logger.info('Setting up profile upload')
    file_name = f'profile-{profile.uid}.json'
    file_content = json.dumps(profile)

    upload_blob(file_name, file_content)
    return {}

@router.get("/roadmaps")
async def get_roadmaps(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the roadmap based on the learner profile"""
    uid = user["uid"]
    roadmap_json = await download_blob(f'roadmap-{uid}.json', "user-profile")
    # TODO: The roadmap variable contains a json file. Convert it to a python dictionary.

    if roadmap_json:
        return json.loads(roadmap_json)
    else:
        return []

@router.post("/roadmaps")
async def post_roadmaps(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Creates a roadmap based on the learner profile"""
    uid = user["uid"]
    profile_json = await download_blob(f'profile-{uid}.json', "user-profile")

    if profile_json:
        profile = json.loads(profile_json)
        return profile
        # TODO: Generate roadmap with Langchain
        # Store roadmap with langchain

@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}