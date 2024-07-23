from pydantic import BaseModel
from app.schemas.roadmap_schema import Roadmap
import uuid

class UserBase(BaseModel):
  name: str
  email: str
  uid: uuid.UUID
  authentication_service: str

class UserCreate(UserBase):
  pass

class User(UserBase):
  id: int
  roadmaps: list[Roadmap] = []

  class Config:
    from_attributes = True