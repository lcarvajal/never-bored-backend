from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os, logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig()
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

if os.getenv('ENV') == 'dev':
    SQLALCHEMY_DATABASE_URL = os.getenv('PROD_DATABASE_URL')
else:
    SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()