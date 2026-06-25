import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base , sessionmaker


# This is used to load system environment variable from the env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Critical: Connection not found")

# create the core connection pool manager
# pool pre ping will check our connection is live or not
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory bound to our engine context

SessionLocal = sessionmaker(autocommit= False , autoflush=False , bind=engine)

#Base class for our SQLAlchemy ORM models

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

