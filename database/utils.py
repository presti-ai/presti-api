from sqlalchemy.orm import Session

from database.connection import get_db
from api.models.user_models import User


def check_api_key(api_key: str, db: Session) -> bool:
    """Check if API key is valid and user is active"""
    user = db.query(User).filter(User.api_key == api_key).first()
    if user and user.is_active:
        return True
    return False


def get_user_from_api_key(api_key: str, db: Session) -> User | None:
    """Get user by API key"""
    return db.query(User).filter(User.api_key == api_key).first()
