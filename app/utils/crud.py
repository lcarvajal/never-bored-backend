from sqlalchemy import and_
from sqlalchemy.orm import Session
from app import models
from app.schemas import user_schema, roadmap_schema

# Users

def get_user(db: Session, user_id: int):
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()

def get_user_by_uid(db: Session, authentication_service: str, uid: str):
    return db.query(models.user.User).filter(and_(models.user.User.uid == uid, models.user.User.authentication_service == authentication_service)).first()

def create_user(db: Session, user: user_schema.UserCreate):
    db_user = models.user.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Roadmaps

def get_roadmap_by_id(db: Session, roadmap_id: int):
    return db.query(models.roadmap.Roadmap).filter(models.roadmap.Roadmap.id == roadmap_id).first()


def get_roadmap_by_id_with_modules(db: Session, roadmap_id: int):
    roadmap = db.query(models.roadmap.Roadmap).filter(models.roadmap.Roadmap.id == roadmap_id).first()
    modules = db.query(models.roadmap.Module).filter(models.roadmap.Module.roadmap_id == roadmap_id).all()

    roadmap.modules = modules

    return roadmap


def create_roadmap(db: Session, roadmap: roadmap_schema.RoadmapCreate):
    db_roadmap = models.roadmap.Roadmap(**roadmap.model_dump())
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    return db_roadmap

def create_roadmap_follow(db: Session, roadmap_follow: roadmap_schema.RoadmapFollowCreate):
    db_roadmap_follow = models.roadmap.RoadmapFollow(**roadmap_follow.model_dump())
    db.add(db_roadmap_follow)
    db.commit()
    db.refresh(db_roadmap_follow)
    return db_roadmap_follow

# Modules

def create_module(db: Session, module: roadmap_schema.ModuleCreate):
    db_module = models.roadmap.Module(**module.model_dump())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

def get_module_by_id_with_submodules_and_resources(db: Session, module_id: int):
    module = db.query(models.roadmap.Module).filter(models.roadmap.Module.id == module_id).first()
    submodules = db.query(models.roadmap.Submodule).filter(models.roadmap.Submodule.module_id == module_id).all()

    for submodule in submodules:
        submodule.resources = db.query(models.roadmap.Resource).filter(models.roadmap.Resource.submodule_id == submodule.id).all()

    module.submodules = submodules

    return module

# Submodules

def create_submodule(db: Session, submodule: roadmap_schema.SubmoduleCreate):
    db_submodule = models.roadmap.Submodule(**submodule.model_dump())
    db.add(db_submodule)
    db.commit()
    db.refresh(db_submodule)
    return db_submodule

def get_submodule_by_id_with_resources(db: Session, submodule_id: int):
    submodule = db.query(models.roadmap.Submodule).filter(models.roadmap.Submodule.id == submodule_id).first()
    submodule.resources = db.query(models.roadmap.Resource).filter(models.roadmap.Resource.submodule_id == submodule_id).all()
    return submodule

# Resources

def create_resource(db: Session, resource: roadmap_schema.ResourceCreate):
    db_resource = models.roadmap.Resource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource