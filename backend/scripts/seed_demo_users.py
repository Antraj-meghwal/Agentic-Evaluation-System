"""Create demo instructor + TA accounts. Run: python scripts/seed_demo_users.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import SessionLocal
from models.upload_model import UploadedFile  # noqa: F401 — registers User.uploads relationship
from models.user_model import User
from core.security import hash_password

DEMO_USERS = [
    ("instructor@gradeops.edu", "demo1234", "instructor"),
    ("ta@gradeops.edu", "demo1234", "ta"),
]


def main():
    db = SessionLocal()
    try:
        for email, password, role in DEMO_USERS:
            if db.query(User).filter(User.email == email).first():
                print(f"Skip (exists): {email}")
                continue
            db.add(
                User(
                    email=email,
                    hashed_password=hash_password(password),
                    role=role,
                )
            )
            print(f"Created: {email} ({role})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
