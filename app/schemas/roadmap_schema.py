from pydantic import BaseModel

# Roadmap

class RoadmapBase(BaseModel):
  title: str
  learning_goal: str

class RoadmapCreate(RoadmapBase):
  pass

class Roadmap(RoadmapBase):
  id: int
  owner_id: int

  class ConfigDict:
    from_attributes = True

# Module

class ModuleBase(BaseModel):
  name: str
  description: str

class ModuleCreate(ModuleBase):
  pass

class Module(ModuleBase):
  id: int
  roadmap_id: int
  position_in_roadmap: int

  class ConfigDict:
    from_attributes = True

# Submodule
class SubmoduleBase(BaseModel):
  name: str
  description: str
  query: str

class SubmoduleCreate(SubmoduleBase):
  pass

class Submodule(SubmoduleBase):
  id: int
  module_id: int
  position_in_module: int

  class ConfigDict:
    from_attributes = True

# Resource

class ResourceBase(BaseModel):
  title: str
  description: str
  type: str
  url: str

class ResourceCreate(ResourceBase):
  pass

class Resource(ResourceBase):
  id: int
  submodule_id: int

  class ConfigDict:
    from_attributes = True