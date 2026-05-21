from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db_url import get_database_url

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
