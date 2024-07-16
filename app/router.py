from fastapi import APIRouter, Depends
from typing import Annotated
from app.authentication import get_firebase_user_from_token
from app.llm import get_roadmap, get_categories
from app.ragsearch import get_search_resources
import json
from pydantic import BaseModel
from app.storage import upload_blob, download_blob

router = APIRouter()

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
    file_name = f'profile-{user["uid"]}.json'
    file_content = json.dumps(profile.model_dump())

    upload_blob(file_name, file_content)
    return {}

@router.post("/roadmaps")
async def post_roadmaps(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Creates a roadmap based on the learner profile"""
    uid = user["uid"]
    profile_json = await download_blob(f'profile-{uid}.json', "user-profile")
    profile = json.loads(profile_json)
    
    learning_goal = profile["goal"]
    file_name = f'roadmap-{uid}.json'
    roadmap = get_roadmap(learning_goal)

    upload_blob(file_name, json.dumps(roadmap))
    
    return roadmap

@router.get("/roadmaps")
async def get_roadmaps(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the roadmap based on the learner profile"""
    uid = user["uid"]
    roadmap_json = await download_blob(f'roadmap-{uid}.json', "user-profile")

    if roadmap_json:
        return json.loads(roadmap_json)

class RoadmapItem(BaseModel):
    learning_goal: str
    name: str
    description: str

@router.post("/categories")
async def post_categories(roadmapItem: RoadmapItem):
    """Generates a list of categories for the current roadmap item"""
    categories_response = get_categories(roadmapItem.learning_goal, roadmapItem.name, roadmapItem.description)
    return categories_response

class Topic(BaseModel):
    description: str

@router.post("/tasks")
async def post_tasks(topic: Topic):
    """Creates a list of resources based on the topic"""
    search_resources = get_search_resources(topic.description)
    return search_resources