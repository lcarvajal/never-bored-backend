from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.utils.authentication import get_firebase_user_from_token
from app.utils import crud, event_tracking
from app.database import get_db
from app import schemas
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Users


@router.post("/", response_model=schemas.user_schema.User)
def create_user(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)],
                user: schemas.user_schema.UserCreate,
                db: Session = Depends(get_db)):
    """Create a new user"""

    db_user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])

    if db_user:
        raise HTTPException(status_code=400, detail="UUID already registered")

    # Track sign up
    event_properties = {'$set': {'name': user.name, 'email': user.email}}
    event_tracking.capture(user.uid, 'signup', event_properties)

    return crud.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.user_schema.User)
def read_user(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)],
              user_id: int,
              db: Session = Depends(get_db)):
    """Get user by id"""

    db_user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
