from fastapi import APIRouter, Depends
from typing import Annotated, List
from app.authentication import get_firebase_user_from_token
from app.llm import get_roadmap, get_categories
from app.ragsearch import get_search_resources
import json, os
from pydantic import BaseModel
from app.storage import upload_blob, download_blob
from posthog import Posthog

router = APIRouter()
posthog = Posthog(project_api_key=os.getenv('POSTHOG_API_KEY'), host='https://eu.i.posthog.com')

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    posthog.capture('test_id', 'test_event')
    return {"msg": "Hello World!"}

class Profile(BaseModel):
    uid: str
    name: str
    email: str
    goal: str
    static_roadmaps: List[str]

@router.post("/profiles")
def post_profiles(user: Annotated[dict, Depends(get_firebase_user_from_token)], profile: Profile):
    """Uploads profile to azure blob storage"""
    file_name = f'profile-{user["uid"]}.json'
    file_content = json.dumps(profile.model_dump())

    upload_blob(file_name, file_content)

    event_properties = {'$set': {'name': profile.name, 'email': profile.email, 'goal': profile.goal}}
    posthog.capture(user["uid"], 'signup', event_properties)
    return {}

@router.get("/profiles")
async def get_profiles(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Downloads profile from azure blob storage"""
    file_name = f'profile-{user["uid"]}.json'
    profile_json = await download_blob(file_name, "user-profile")
    if profile_json:
        return json.loads(profile_json)
    else:
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
    posthog.capture(user["uid"], '$pageview', {'$current_url': os.getenv('FRONTEND_URL') + f'/roadmaps'})
    uid = user["uid"]
    roadmap_json = await download_blob(f'roadmap-{uid}.json', "user-profile")

    if roadmap_json:
        return json.loads(roadmap_json)
    
@router.get("/roadmaps/{roadmap_name}")
async def get_modules(user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_name: str):
    """Gets the roadmap with modules"""
    posthog.capture(user["uid"], '$pageview', {'$current_url': os.getenv('FRONTEND_URL') + f'/roadmaps/{roadmap_name}'})
    roadmap_json = await download_blob(f'{roadmap_name}/outline.json', "roadmaps")
    
    if roadmap_json:
        return json.loads(roadmap_json)

@router.get("/roadmaps/{roadmap_name}/{module_id}")
async def get_submodule(user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_name: str, module_id: int):
    posthog.capture(user["uid"], '$pageview', {'$current_url': os.getenv('FRONTEND_URL') + f'/roadmaps/{roadmap_name}/{module_id}'})
    module_json = await download_blob(f'{roadmap_name}/{module_id}.json', "roadmaps")
    
    if module_json:
        return json.loads(module_json)


class RoadmapItem(BaseModel):
    learning_goal: str
    name: str
    description: str

@router.post("/categories")
async def post_categories(user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmapItem: RoadmapItem):
    """Generates a list of categories for the current roadmap item"""
    categories_response = get_categories(roadmapItem.learning_goal, roadmapItem.name, roadmapItem.description)
    return categories_response

class Topic(BaseModel):
    description: str

@router.post("/tasks")
async def post_tasks(user: Annotated[dict, Depends(get_firebase_user_from_token)], topic: Topic):
    """Creates a list of resources based on the topic"""
    posthog.capture(user["uid"], 'view-submodule')
    search_resources = get_search_resources(topic.description)
    return search_resources
