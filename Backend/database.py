from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()  # Base model
