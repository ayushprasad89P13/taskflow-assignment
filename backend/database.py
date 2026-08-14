import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# We might connect via docker-compose (db:5432) or locally (localhost:5432)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskflow_user:taskflow_password@localhost:5432/taskflow_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
