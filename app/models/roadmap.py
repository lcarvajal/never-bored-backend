from app.database import Base
from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    learning_goal = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="roadmaps")
    modules = relationship("Module", back_populates="roadmap")
    follows = relationship("RoadmapFollow", back_populates="roadmap")

    def __repr__(self):
        return f'<Roadmap {self.title}>'


class RoadmapFollow(Base):
    __tablename__ = "roadmap_follows"

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)

    user = relationship("User", back_populates="roadmap_follows")
    roadmap = relationship("Roadmap", back_populates="follows")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    position_in_roadmap = Column(Integer, nullable=False)

    roadmap = relationship("Roadmap", back_populates="modules")
    submodules = relationship("Submodule", back_populates="module")

    def __repr__(self):
        return f'<Module {self.title}>'


class Submodule(Base):
    __tablename__ = "submodules"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    query = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    module_id = Column(Integer, ForeignKey("modules.id"))
    position_in_module = Column(Integer, nullable=False)

    module = relationship("Module", back_populates="submodules")
    resources = relationship("Resource", back_populates="submodule")

    def __repr__(self):
        return f'<Submodule {self.title}>'


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    submodule_id = Column(Integer, ForeignKey("submodules.id"))

    submodule = relationship("Submodule", back_populates="resources")

    def __repr__(self):
        return f'<Resource {self.title}>'
