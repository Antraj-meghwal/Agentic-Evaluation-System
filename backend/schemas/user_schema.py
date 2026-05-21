from typing import Literal

from pydantic import BaseModel, EmailStr, Field


RegisterRole = Literal["instructor", "professor", "ta"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: RegisterRole


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
