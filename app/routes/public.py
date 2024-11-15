from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Welcome to the never bored learning api!"}
