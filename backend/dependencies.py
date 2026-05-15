# Database session
from database import SessionLocal

# FastAPI dependency tools
from fastapi import Depends

# OAuth2 token extraction
from fastapi.security import OAuth2PasswordBearer

# JWT verification
from services.auth_service import (
    verify_access_token
)

from fastapi import HTTPException

# -----------------------------------
# Database dependency
# -----------------------------------
def get_db():

    # Create DB session
    db = SessionLocal()

    try:
        yield db

    finally:
        # Always close session
        db.close()


# -----------------------------------
# OAuth2 token extractor
# -----------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# -----------------------------------
# Get current authenticated user
# -----------------------------------
def get_current_user(

    token: str = Depends(oauth2_scheme)
):

    # Verify JWT token
    token_data = verify_access_token(token)

    return token_data


# -----------------------------------
# Role-based access control
# -----------------------------------
def require_role(allowed_roles: list):

    # Dependency function
    def role_checker(

        current_user = Depends(get_current_user)
    ):

        # Extract user role
        user_role = current_user.get("role")

        # Role not allowed
        if user_role not in allowed_roles:

            raise HTTPException(

                status_code=403,

                detail="Access denied"
            )

        # Return authenticated user
        return current_user

    return role_checker