from sqlalchemy.orm import Session

from core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from models.user import User


def register_user(
    db: Session,
    email: str,
    password: str,
    role: str
):

    hashed_pw = hash_password(
        password
    )

    user = User(
        email=email,
        hashed_password=hashed_pw,
        role=role
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if not user:

        return None

    if not verify_password(
        password,
        user.hashed_password
    ):

        return None

    token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role.value
        }
    )

    return token