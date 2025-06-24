from sqlmodel import Session
from api.models.bg_removal_models import BackgroundRemoval


def create_bg_removal(removal: BackgroundRemoval, db: Session):
    """
    Create a new background removal record in the database.
    """
    try:
        db.add(removal)
        db.commit()
        db.refresh(removal)
    except Exception as e:
        db.rollback()
        raise e
    return removal
