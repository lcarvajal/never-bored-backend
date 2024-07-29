from pydantic import BaseModel

# Resource


class ResourceBase(BaseModel):
    title: str
    description: str
    type: str
    url: str
    submodule_id: int


class ResourceCreate(ResourceBase):
    pass


class Resource(ResourceBase):
    id: int

    class ConfigDict:
        from_attributes = True

# Submodule


class SubmoduleBase(BaseModel):
    title: str
    description: str
    module_id: int
    position_in_module: int
    query: str


class SubmoduleCreate(SubmoduleBase):
    pass


class Submodule(SubmoduleBase):
    id: int
    resources: list[Resource]

    class ConfigDict:
        from_attributes = True

# Module


class ModuleBase(BaseModel):
    title: str
    description: str
    position_in_roadmap: int
    roadmap_id: int


class ModuleCreate(ModuleBase):
    pass


class Module(ModuleBase):
    id: int
    submodules: list[Submodule]

    class ConfigDict:
        from_attributes = True

# Roadmap Follow


class RoadmapFollow(BaseModel):
    roadmap_id: int
    user_id: int


class RoadmapFollowCreate(RoadmapFollow):
    pass


class RoadmapFollow(RoadmapFollow):
    id: int

    class ConfigDict:
        from_attributes = True

# Roadmap


class RoadmapBase(BaseModel):
    title: str
    learning_goal: str
    owner_id: int


class RoadmapCreate(RoadmapBase):
    pass


class Roadmap(RoadmapBase):
    id: int
    modules: list[Module]
    follows: list[RoadmapFollow]

    class ConfigDict:
        from_attributes = True
