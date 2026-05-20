"""Shared FastAPI dependencies for auth and database sessions."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from core.constants import ROLE_INSTRUCTOR, ROLE_PROFESSOR
from core.security import ALGORITHM, SECRET_KEY
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _expand_roles(roles: list[str]) -> set[str]:
    """Accept professor/instructor interchangeably (frontend vs backend naming)."""
    expanded: set[str] = set()
    for role in roles:
        key = role.lower()
        expanded.add(key)
        if key in (ROLE_PROFESSOR, ROLE_INSTRUCTOR):
            expanded.update({ROLE_PROFESSOR, ROLE_INSTRUCTOR})
    return expanded


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user_id = payload.get("id") or payload.get("user_id")
    return {
        "id": user_id,
        "user_id": user_id,
        "email": payload.get("sub"),
        "role": payload.get("role", ""),
        "sub": payload.get("sub"),
    }


def require_role(allowed_roles: list[str]):
    allowed = _expand_roles(allowed_roles)

    def role_checker(current_user: dict = Depends(get_current_user)):
        role = (current_user.get("role") or "").lower()
        if role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{role}' is not allowed for this action",
            )
        if current_user.get("id") is None:
            raise HTTPException(
                status_code=401,
                detail="Token missing user id; please log in again",
            )
        return current_user

    return role_checker
