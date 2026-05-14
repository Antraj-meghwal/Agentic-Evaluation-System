# Import SessionLocal
from database import SessionLocal


# Database dependency
def get_db():

    # Create DB session
    db = SessionLocal()

    try:
        yield db

    finally:
        # Always close DB session
        db.close()