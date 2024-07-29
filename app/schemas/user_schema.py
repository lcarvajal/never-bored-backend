from pydantic import BaseModel
from app.schemas.roadmap_schema import Roadmap, RoadmapFollow


class UserBase(BaseModel):
    name: str
    email: str
    uid: str
    authentication_service: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    roadmaps: list[Roadmap] = []
    roadmap_follows: list[RoadmapFollow] = []

    class ConfigDict:
        from_attributes = True
