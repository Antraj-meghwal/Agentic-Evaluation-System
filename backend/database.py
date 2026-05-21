# Load environment variables
from dotenv import load_dotenv

# Access environment variables
import os

# SQLAlchemy tools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


# Load .env file
load_dotenv()


# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy backend/.env.example to backend/.env "
        "and configure PostgreSQL (see docs/SETUP.md)."
    )


# Create PostgreSQL engine
engine = create_engine(DATABASE_URL)


# Database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for models
Base = declarative_base()