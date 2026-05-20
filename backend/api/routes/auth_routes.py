from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from db.session import get_db

from schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema
)

from services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter()


@router.post("/register")
def register(
    user_data: UserRegisterSchema,
    db: Session = Depends(get_db)
):

    user = register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )

    return {
        "message":
        "User registered",

        "user_id":
        str(user.id)
    }


@router.post("/login")
def login(
    user_data: UserLoginSchema,
    db: Session = Depends(get_db)
):

    token = authenticate_user(
        db=db,
        email=user_data.email,
        password=user_data.password
    )

    if not token:

        return {
            "error":
            "Invalid credentials"
        }

    return {
        "access_token": token,
        "token_type": "bearer"
    }