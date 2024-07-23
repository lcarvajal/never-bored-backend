from sqlalchemy import and_
from sqlalchemy.orm import Session
from app import models
from app.schemas import user_schema, roadmap_schema
import uuid

# Users

def get_user(db: Session, user_id: int):
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()

def get_user_by_uid(db: Session, authentication_service: str, uid: uuid.UUID):
    return db.query(models.user.User).filter(and_(models.user.User.uid == uid, models.user.User.authentication_service == authentication_service)).first()

def create_user(db: Session, user: user_schema.UserCreate):
    db_user = models.user.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Roadmaps

def get_first_roadmap(db: Session, roadmap_id: int):
    return db.query(models.roadmap).filter(models.roadmap.id == roadmap_id).first()

def create_user_roadmap(db: Session, roadmap: roadmap_schema.RoadmapCreate, user_id: int):
    db_roadmap = models.roadmap(**roadmap.model_dump(), owner_id=user_id)
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    return db_roadmap