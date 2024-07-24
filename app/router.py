from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Annotated
from app.utils.authentication import get_firebase_user_from_token
from app.utils import crud
from app.utils import llm
from app.utils import ragsearch
import os
from pydantic import BaseModel
from posthog import Posthog
from app.database import get_db
from app import schemas
from sqlalchemy.orm import Session

router = APIRouter()
posthog = Posthog(project_api_key=os.getenv('POSTHOG_API_KEY'), host='https://eu.i.posthog.com')

if os.getenv('ENV') == 'dev':
    # posthog.debug = True
    posthog.disabled = True

@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Hello World!"}

# Users

@router.post("/users/", response_model=schemas.user_schema.User)
def create_user(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], user: schemas.user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])
    if db_user:
        raise HTTPException(status_code=400, detail="UUID already registered")
    else:
        event_properties = {'$set': {'name': user.name, 'email': user.email}}
        posthog.capture(user.uid, 'signup', event_properties)

    return crud.create_user(db=db, user=user)

@router.get("/users/{user_id}", response_model=schemas.user_schema.User)
def read_user(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

class LearningGoal(BaseModel):
    description: str

# Roadmaps

@router.post("/roadmaps")
async def post_roadmaps(
    firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)],
    learning_goal: LearningGoal,
    db: Session = Depends(get_db),
) -> schemas.roadmap_schema.Roadmap:
    """Creates a roadmap for the user and stores it in the database"""
    user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    llm_roadmap = llm.get_roadmap(learning_goal.description)

    roadmap = schemas.roadmap_schema.RoadmapCreate(
        title="",
        learning_goal=learning_goal.description,
        owner_id=user.id,
    )
    created_roadmap = crud.create_roadmap(db=db, roadmap=roadmap)

    if created_roadmap is None:
        raise HTTPException(status_code=500, detail="Error creating roadmap")
    
    roadmap_follow = schemas.roadmap_schema.RoadmapFollowCreate(
        user_id=user.id,
        roadmap_id=created_roadmap.id
    )
    created_roadmap_follow = crud.create_roadmap_follow(db=db, roadmap_follow=roadmap_follow)

    if created_roadmap_follow is None:
        raise HTTPException(status_code=500, detail="Error creating roadmap follow")

    created_roadmap.modules = []

    for index, llm_module in enumerate(llm_roadmap["modules"]):
        module = schemas.roadmap_schema.ModuleCreate(
            position_in_roadmap=index,
            title=llm_module["title"],
            description=llm_module["description"],
            roadmap_id=created_roadmap.id
        )
        created_module = crud.create_module(db=db, module=module)

        if created_module is None:
            raise HTTPException(status_code=500, detail="Error creating module")

        created_roadmap.modules.append(created_module)

    return created_roadmap

@router.get("/roadmaps")
def get_roadmap_follows(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
    user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    roadmaps: list[schemas.roadmap_schema.Roadmap] = []
    for follow in user.roadmap_follows:
        roadmap = crud.get_roadmap_by_id(db, follow.roadmap_id)

        if roadmap is None:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        roadmaps.append(roadmap)

    return roadmaps

@router.get("/roadmaps/{roadmap_id}")
def get_roadmap_by_id(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id(db, roadmap_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    return roadmap

@router.get("/roadmaps/{roadmap_id}/modules")
def get_roadmap_by_id_with_modules(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id_with_modules(db, roadmap_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    return roadmap

@router.get("/roadmaps/{roadmap_id}/modules/{module_id}")
def get_module_by_id(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], module_id: int, db: Session = Depends(get_db)):
    module = crud.get_module_by_id_with_submodules(db, module_id)

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    return module

# Modules

def get_resources_for_submodules(module_id: int, db):
  module = crud.get_module_by_id_with_submodules(db, module_id)

  if module is None:
    raise HTTPException(status_code=404, detail="Module not found")

  for submodule in module.submodules:
    search_response = ragsearch.get_search_resources(submodule.description)
    rag_resources = search_response["results"]
    print(rag_resources)
    for rag_resource in rag_resources:
      print("resource retrieved")
      print(rag_resource)
      resource = schemas.roadmap_schema.ResourceCreate(
        title=rag_resource["title"],
        description=rag_resource["content"],
        url=rag_resource["url"],
        submodule_id=submodule.id,
        type="article"
      )
      crud.create_resource(db, resource)

      if resource is None:
        raise HTTPException(status_code=500, detail="Error creating resource")

@router.post("/roadmaps/{roadmap_id}/modules/{module_id}/populate")
async def update_module(module_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id(db, module_id)
    module = crud.get_module_by_id_with_submodules(db, module_id)
    
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    llm_submodules = llm.get_submodules(module)

    submodules = []

    for index, llm_submodule in enumerate(llm_submodules):
        submodule = schemas.roadmap_schema.SubmoduleCreate(
            position_in_module=index,
            title=llm_submodule["title"],
            description=llm_submodule["description"],
            module_id=module.id,
            query=llm_submodule["search_query_to_find_learning_resources"]
        )

        created_submodule = crud.create_submodule(db=db, submodule=submodule)

        if created_submodule is None:
            raise HTTPException(status_code=500, detail="Error creating submodule")
        
        submodules.append(submodule)

    background_tasks.add_task(get_resources_for_submodules, module.id, db)
    return submodules