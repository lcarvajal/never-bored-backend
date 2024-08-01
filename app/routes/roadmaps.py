from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Annotated
from app.utils.authentication import get_firebase_user_from_token
from app.utils import crud, event_tracking, llm, ragsearch
from pydantic import BaseModel
from app.database import get_db
from app import schemas
from sqlalchemy.orm import Session
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roadmaps",
    tags=["roadmaps"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Roadmaps


class LearningGoal(BaseModel):
    description: str


@router.post("/")
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
        title=llm_roadmap["title"],
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
    created_roadmap_follow = crud.create_roadmap_follow(
        db=db, roadmap_follow=roadmap_follow)

    if created_roadmap_follow is None:
        raise HTTPException(
            status_code=500, detail="Error creating roadmap follow")

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
            raise HTTPException(
                status_code=500, detail="Error creating module")

        created_roadmap.modules.append(created_module)

    return created_roadmap


@router.get("/")
def get_roadmap_follows(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
    """Get roadmap follows"""
    user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    roadmaps = crud.get_followed_roadmaps(db, user.id)

    if roadmaps is None:
        raise HTTPException(status_code=404, detail="Roadmaps not found")

    return roadmaps


@router.get("/{roadmap_id}")
def get_roadmap_by_id(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id(db, roadmap_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    return roadmap


@router.get("/{roadmap_id}/modules")
def get_roadmap_by_id_with_modules(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, db: Session = Depends(get_db)):
    """Get roadmap with mdoules"""
    event_tracking.capture_pageview(
        firebase_user["uid"], f'roadmaps/{roadmap_id}/modules')

    roadmap = crud.get_roadmap_by_id_with_modules(db, roadmap_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    return roadmap


@router.get("/{roadmap_id}/modules/{module_id}")
def get_module_by_id(module_id: int, db: Session = Depends(get_db)):
    module = crud.get_module_by_id_with_submodules_and_resources(db, module_id)

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    return module

# Roadmap follows


@router.post("/{roadmap_id}/follow")
def follow_roadmap(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    roadmap_follow = schemas.roadmap_schema.RoadmapFollowCreate(
        user_id=user.id,
        roadmap_id=roadmap_id
    )
    created_roadmap_follow = crud.create_roadmap_follow(
        db=db, roadmap_follow=roadmap_follow)

    if created_roadmap_follow is None:
        raise HTTPException(
            status_code=500, detail="Error creating roadmap follow")

    return created_roadmap_follow

# Modules


def create_resources_using_ragsearch_for_submodule(roadmap_title, module_description, submodule_id, db):
    submodule = crud.get_submodule_by_id_with_resources(db, submodule_id)

    if submodule is None:
        raise HTTPException(status_code=404, detail="Submodule not found")

    if len(submodule.resources) > 0:
        logger.info("Submodule already populated")
        return

    query = llm.get_query_to_find_learning_resources(
        roadmap_title, module_description, submodule_description=submodule.description)
    search_response = ragsearch.get_search_resources(query)
    rag_resources = search_response["results"]
    resources = []

    for rag_resource in rag_resources:
        logger.info("Creating resource")
        logger.info(rag_resource)
        resource = schemas.roadmap_schema.ResourceCreate(
            title=rag_resource["title"],
            description=rag_resource["content"],
            url=rag_resource["url"],
            submodule_id=submodule.id,
            type="article"
        )
        resource = crud.create_resource(db, resource)

        if resource is None:
            raise HTTPException(
                status_code=500, detail="Error creating resource")

        resources.append(resource)

    return []


def create_resources_using_ragsearch_for_module(roadmap_title, module_id, db):
    module = crud.get_module_by_id_with_submodules_and_resources(db, module_id)

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    for submodule in module.submodules:
        create_resources_using_ragsearch_for_submodule(
            roadmap_title, module.description, submodule.id, db)


@router.post("/{roadmap_id}/modules/{module_id}/populate")
async def populate_module_with_submodules_and_resources(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, module_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id(db, roadmap_id)
    module = crud.get_module_by_id_with_submodules_and_resources(db, module_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    if len(module.submodules) > 0:
        raise HTTPException(status_code=400, detail="Module already populated")

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
            raise HTTPException(
                status_code=500, detail="Error creating submodule")

        submodules.append(submodule)

    background_tasks.add_task(
        create_resources_using_ragsearch_for_module, roadmap.title, module.id, db)
    return submodules


# Submodules


@router.post("/{roadmap_id}/modules/{module_id}/submodules/{submodule_id}/populate")
def populate_submodule_with_resources(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], roadmap_id: int, module_id: int, submodule_id: int, db: Session = Depends(get_db)):
    roadmap = crud.get_roadmap_by_id(db, roadmap_id)
    module = crud.get_module_by_id(db, module_id)
    submodule = crud.get_submodule_by_id_with_resources(db, submodule_id)

    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    if submodule is None:
        raise HTTPException(status_code=404, detail="Submodule not found")

    if len(submodule.resources) > 0:
        raise HTTPException(
            status_code=400, detail="Submodule already populated")

    resources = create_resources_using_ragsearch_for_submodule(
        roadmap.title, module.description, submodule.id, db)

    return resources
