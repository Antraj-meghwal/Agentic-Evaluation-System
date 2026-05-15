# FastAPI tools
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

# SQLAlchemy session
from sqlalchemy.orm import Session

# DB dependency
from dependencies import get_db

# User model
from models.user_model import User

# Schemas
from schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse
)

# Auth utilities
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)


# Create router
router = APIRouter()


# -----------------------------------
# Register user
# -----------------------------------
@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    # Prevent duplicate accounts
    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Hash password
    hashed_pw = hash_password(
        user.password
    )

    # Create user object
    new_user = User(

        email=user.email,

        hashed_password=hashed_pw,

        role=user.role
    )

    # Save to database
    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# -----------------------------------
# Login user
# -----------------------------------
@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    # Invalid email
    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Verify password
    valid_password = verify_password(

        user.password,

        db_user.hashed_password
    )

    # Invalid password
    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Generate JWT token
    access_token = create_access_token({

    "sub": db_user.email,

    "role": db_user.role,

    "user_id": db_user.id
    })

    # Return token
    return {

        "access_token": access_token,

        "token_type": "bearer"
    }