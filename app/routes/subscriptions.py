import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from typing import Annotated
import stripe
from app.utils.authentication import get_firebase_user_from_token
from app.utils import crud
from app.database import get_db
from app import schemas
from sqlalchemy.orm import Session
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Subscriptions


@router.post("/checkout-session")
def create_checkout_session(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1Pi12ERwlNxepH9XDobR4Gjd',
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=os.getenv('FRONTEND_URL') + \
            '/order-preview?success=true',
            cancel_url=os.getenv('FRONTEND_URL') + \
            '/order-preview?canceled=true',
            automatic_tax={'enabled': True},
        )
    except Exception as e:
        return str(e)

    return {
        "redirect_url": checkout_session.url
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    logger.info("Received webhook")
    logger.info(payload)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_ENDPOINT_SECRET'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'], db)
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'], db)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'], db)
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'], db)
    return {"success": True}


def handle_subscription_created(subscription, db: Session):
    user = crud.get_user_by_email(db, subscription['customer'])
    if user:
        new_subscription = schemas.SubscriptionCreate(
            user_id=user.id,
            payment_gateway_customer_id=subscription['customer'],
            payment_gateway_subscription_id=subscription['id'],
            payment_gateway_provider='stripe',
            status=subscription['status'],
            current_period_end=datetime.fromtimestamp(
                subscription['current_period_end']),
        )
        crud.create_subscription(db, new_subscription)

        crud.update_user(db, user, schemas.User(
            payment_gateway_customer_id=subscription['customer'],
            payment_gateway_provider='stripe'))


def handle_subscription_updated(subscription, db: Session):
    db_subscription = crud.get_subscription_by_stripe_id(
        db, subscription['id'])
    if db_subscription:
        update_data = {
            "status": subscription['status'],
            "current_period_end": datetime.fromtimestamp(subscription['current_period_end'])
        }
        crud.update_subscription(
            db, db_subscription.id, schemas.SubscriptionUpdate(**update_data))


def handle_subscription_deleted(subscription, db: Session):
    db_subscription = crud.get_subscription_by_stripe_id(
        db, subscription['id'])
    if db_subscription:
        crud.delete_subscription(db, db_subscription.id)


def handle_payment_succeeded(invoice, db: Session):
    # Optionally handle successful payment events
    pass
