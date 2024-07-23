from app.database import Base
from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="roadmaps")