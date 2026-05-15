# Pydantic tools
from pydantic import BaseModel
from pydantic import EmailStr


# -----------------------------------
# User registration request
# -----------------------------------
class UserCreate(BaseModel):

    email: EmailStr

    password: str

    role: str


# -----------------------------------
# User response
# -----------------------------------
class UserResponse(BaseModel):

    id: int

    email: EmailStr

    role: str

    class Config:

        from_attributes = True


# -----------------------------------
# Login request schema
# -----------------------------------
class UserLogin(BaseModel):

    email: EmailStr

    password: str


# -----------------------------------
# Token response schema
# -----------------------------------
class TokenResponse(BaseModel):

    access_token: str

    token_type: str