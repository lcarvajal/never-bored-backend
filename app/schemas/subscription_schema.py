import datetime
from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    user_id: int
    status: str
    current_period_end: datetime.datetime
    payment_gateway_provider: str
    payment_gateway_customer_id: str
    payment_gateway_subscription_id: str


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    id: int

    class ConfigDict:
        from_attributes = True
