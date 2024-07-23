from app.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text
from sqlalchemy.orm import relationship


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    goal = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    roadmaps = relationship("User", back_populates="roadmaps")