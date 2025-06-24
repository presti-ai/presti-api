from sqlmodel import Session
from api.models.generation_models import Generation
from database.connection import get_db


def create_generation(generation: Generation, db: Session = next(get_db())):
    """
    Create a new generation record in the database.
    """
    db.add(generation)
    try:
        db.commit()
        db.refresh(generation)
    except Exception as e:
        db.rollback()
        raise e
    return generation
