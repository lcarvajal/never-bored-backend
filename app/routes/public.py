from fastapi import APIRouter, Depends
from typing import Annotated
from app.utils.authentication import get_firebase_user_from_token

router = APIRouter()


@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Welcome to the never bored learning api!"}
