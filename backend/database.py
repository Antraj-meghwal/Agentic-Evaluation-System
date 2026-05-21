from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.db_url import get_database_url

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
