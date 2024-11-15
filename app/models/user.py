from app.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)

    uid = Column(String, nullable=False)
    authentication_service = Column(String, nullable=False)

    payment_gateway_customer_id = Column(String, nullable=True)
    payment_gateway_provider = Column(String, nullable=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    roadmaps = relationship("Roadmap", back_populates="owner")
    roadmap_follows = relationship("RoadmapFollow", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
