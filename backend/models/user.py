"""Re-export legacy User model (api routes use models.user)."""

from models.user_model import User

__all__ = ["User"]
