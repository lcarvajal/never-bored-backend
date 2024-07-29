from fastapi import APIRouter, Depends
from typing import Annotated
from app.utils.authentication import get_firebase_user_from_token

router = APIRouter()


@router.get("/")
def hello():
    """Hello world route to make sure the app is working correctly"""
    return {"msg": "Welcome to the never bored learning api!"}

# Payment Gateway


# @router.post("/checkout")
# def create_checkout_session(firebase_user: Annotated[dict, Depends(get_firebase_user_from_token)]):
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                     'price': '{{PRICE_ID}}',
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url=YOUR_DOMAIN + '?success=true',
#             cancel_url=YOUR_DOMAIN + '?canceled=true',
#             automatic_tax={'enabled': True},
#         )
#     except Exception as e:
#         return str(e)

#     return redirect(checkout_session.url, code=303)
