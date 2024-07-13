from typing import Annotated
from app.config import get_firebase_user_from_token
from fastapi import FastAPI,APIRouter, Depends
import firebase_admin
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

app = FastAPI()

router = APIRouter()


@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """gets the firebase connected user"""
    return {"id": user["uid"]}

app.include_router(router)
settings = get_settings()
origins = [settings.frontend_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

firebase_admin.initialize_app()