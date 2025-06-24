from sqlmodel import Session
from api.models.generation_models import Generation


def create_generation(generation: Generation, db: Session):
    """
    Create a new generation record in the database.
    """
    try:
        db.add(generation)
        db.commit()
        db.refresh(generation)
    except Exception as e:
        db.rollback()
        raise e
    return generation
