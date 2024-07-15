from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.config import get_firebase_user_from_token, upload_blob, download_blob
import json, logging
from pydantic import BaseModel
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

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
    
    model = ChatOpenAI()

    class LearningGoal(BaseModel):
        id: int
        name: str
        description: str

    class StudyPlan(BaseModel):
        modules: List[LearningGoal]
        learning_goal: str
    
    parser = JsonOutputParser(pydantic_object=StudyPlan)

    # A chat template converts raw user input into better input for an llm.
    prompt = PromptTemplate(
        template="Break down the learning goal into smaller learning goals using Blooms taxonomy verbs: \n{format_instructions}\n{learning_goal}\n",
        input_variables=["learning_goal"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    learning_goal = profile["goal"]

    file_name = f'roadmap-{uid}.json'
    roadmap = chain.invoke({"learning_goal": learning_goal})

    upload_blob(file_name, json.dumps(roadmap))
    
    return roadmap

@router.get("/roadmaps")
async def get_roadmaps(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the roadmap based on the learner profile"""
    uid = user["uid"]
    roadmap_json = await download_blob(f'roadmap-{uid}.json', "user-profile")

    if roadmap_json:
        return json.loads(roadmap_json)

@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}