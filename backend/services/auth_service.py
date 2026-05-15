# -----------------------------------
# Password hashing
# -----------------------------------
from passlib.context import CryptContext


# -----------------------------------
# JWT tools
# -----------------------------------
from jose import jwt
from jose import JWTError


# -----------------------------------
# Date/time utilities
# -----------------------------------
from datetime import datetime
from datetime import timedelta


# -----------------------------------
# FastAPI exceptions
# -----------------------------------
from fastapi import HTTPException


# -----------------------------------
# Configure bcrypt hashing
# -----------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# -----------------------------------
# JWT configuration
# -----------------------------------

# Secret key
# Later move this to .env
SECRET_KEY = "gradeops_secret_key"

# JWT algorithm
ALGORITHM = "HS256"

# Token expiry duration
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# -----------------------------------
# Hash password
# -----------------------------------
def hash_password(password: str):

    return pwd_context.hash(password)


# -----------------------------------
# Verify password
# -----------------------------------
def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# -----------------------------------
# Create JWT token
# -----------------------------------
def create_access_token(data: dict):

    # Copy payload
    to_encode = data.copy()

    # Expiry time
    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # Add expiry to payload
    to_encode.update({

        "exp": expire
    })

    # Generate JWT token
    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt


# -----------------------------------
# Verify JWT token
# -----------------------------------
def verify_access_token(token: str):

    try:

        # Decode JWT token
        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        # Extract email
        email = payload.get("sub")

        # Extract role
        role = payload.get("role")

        # Extract user ID
        user_id = payload.get("user_id")

        # Missing required data
        if email is None:

            raise HTTPException(

                status_code=401,

                detail="Invalid token"
            )

        # Return authenticated user data
        return {

            "id": user_id,

            "email": email,

            "role": role
        }

    # Invalid JWT token
    except JWTError:

        raise HTTPException(

            status_code=401,

            detail="Invalid token"
        )