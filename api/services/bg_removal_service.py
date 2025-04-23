from sqlmodel import Session
from database.connection import get_db
from api.models.bg_removal_models import BackgroundRemoval


def create_bg_removal(removal: BackgroundRemoval, db: Session = next(get_db())):
    """
    Create a new background removal record in the database.
    """
    db.add(removal)
    db.commit()
    db.refresh(removal)
    return removal
