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
def create_checkout_session(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)], db: Session = Depends(get_db)):
    user = crud.get_user_by_uid(db, "firebase", firebase_user["uid"])

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found")

    if user.payment_gateway_customer_id is None:
        stripe_customer = stripe.Customer.create(
            name=user.name,
            email=user.email,
        )

        if stripe_customer is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to create Stripe customer")

        logger.info("Created Stripe customer")

        user.payment_gateway_customer_id = stripe_customer.id
        user.payment_gateway_provider = 'stripe'

        updated_user = crud.update_user(db, user)

        logger.info("Updated user with Stripe customer ID")
        logger.info(updated_user)

        if updated_user is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to update user")

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1Pi12ERwlNxepH9XDobR4Gjd',
                    'quantity': 1,
                },
            ],
            customer=user.payment_gateway_customer_id,
            customer_update={
                'address': 'auto'
            },
            mode='subscription',
            success_url=os.getenv('FRONTEND_URL') + \
            '/checkout?success=true',
            cancel_url=os.getenv('FRONTEND_URL') + \
            '/checkout?canceled=true',
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

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_ENDPOINT_SECRET'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info("Received webhook")
    logger.info('ID')
    logger.info(event['data']['object']['id'])
    logger.info('...')

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
    user = crud.get_user_by_payment_gateway_customer_id(
        db, subscription['customer'], 'stripe')
    if user:
        new_subscription = schemas.subscription_schema.SubscriptionCreate(
            user_id=user.id,
            payment_gateway_customer_id=subscription['customer'],
            payment_gateway_subscription_id=subscription['id'],
            payment_gateway_provider='stripe',
            status=subscription['status'],
            current_period_end=datetime.datetime.fromtimestamp(
                subscription['current_period_end']),
        )
        crud.create_subscription(db, new_subscription)

        user.payment_gateway_customer_id = subscription['customer']
        user.payment_gateway_provider = 'stripe'
        crud.update_user(db, user)
    else:
        logger.info('User not found. Unable to create subscription.')


def handle_subscription_updated(subscription, db: Session):
    db_subscription = crud.get_subscription_by_stripe_id(
        db, subscription['id'])
    if db_subscription:
        db_subscription.status = subscription['status']
        db_subscription.current_period_end = datetime.datetime.fromtimestamp(
            subscription['current_period_end'])

        crud.update_subscription(
            db, db_subscription)


def handle_subscription_deleted(subscription, db: Session):
    db_subscription = crud.get_subscription_by_stripe_id(
        db, subscription['id'])
    if db_subscription:
        crud.delete_subscription(db, db_subscription.id)


def handle_payment_succeeded(invoice, db: Session):
    # Optionally handle successful payment events
    pass
