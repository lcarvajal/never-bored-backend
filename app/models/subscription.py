from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=True)
    current_period_end = Column(TIMESTAMP(timezone=True), nullable=True)

    payment_gateway_provider = Column(String, nullable=True)
    payment_gateway_customer_id = Column(String, nullable=True)
    payment_gateway_subscription_id = Column(String, nullable=True)

    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"
