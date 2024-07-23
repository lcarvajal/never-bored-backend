from pydantic import BaseModel

class RoadmapBase(BaseModel):
  name: str
  learning_goal: str

class RoadmapCreate(RoadmapBase):
  pass

class Roadmap(RoadmapBase):
  id: int
  owner_id: int

  class Config:
    from_attributes = True