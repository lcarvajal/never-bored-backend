from app.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,nullable=False)
    uid = Column(UUID(as_uuid=True),nullable=False)
    authentication_service = Column(String,nullable=False)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    roadmaps = relationship("Roadmap", back_populates="owner")