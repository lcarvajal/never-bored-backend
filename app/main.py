import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import base64
from dotenv import load_dotenv
import firebase_admin
from app.routes import public, roadmaps, subscriptions, users
from app.config import get_settings
from app.database import engine, Base
from app.utils.admin import configure_admin
import stripe

load_dotenv()

stripe.api_key = os.getenv('STRIPE_API_KEY')

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(public.router)
app.include_router(users.router)
app.include_router(roadmaps.router)
app.include_router(subscriptions.router)
settings = get_settings()

origins = [
    "https://localhost:5173",
    "https://never-bored-learning.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize Firebase
firebase_service_account = os.getenv('FIREBASE_SERVICE_ACCOUNT')

if not firebase_service_account:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable not set")

service_account_info = json.loads(base64.b64decode(firebase_service_account))
cred = firebase_admin.credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

if os.getenv('ENV') == 'dev':
    logger.info("Running in development mode")

configure_admin(app, engine)
