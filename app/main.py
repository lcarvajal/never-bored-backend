from app.router import router
from fastapi import FastAPI
import firebase_admin
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
import os
import json
import base64
from dotenv import load_dotenv
from app import models
from app.database import SessionLocal,engine

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
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
