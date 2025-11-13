from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# REPLACE THESE VALUES WITH YOUR ACTUAL DB INFO
DB_USER = "satyayendru"      # e.g., postgres
DB_PASSWORD = ""  # e.g., password123 (leave empty if none)
DB_HOST = "localhost"
DB_PORT = "5432"               # default postgres port
DB_NAME = "project_database"

# Connection String
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()