from pydantic import BaseModel
from RoadmapSchema import Roadmap
import uuid

class UserBase(BaseModel):
  name: str
  email: str
  uid: uuid
  authentication_service: str

class UserCreate(UserBase):
  pass

class User(UserBase):
  id: int
  roadmaps: list[Roadmap] = []

  class Config:
    orm_mode = True