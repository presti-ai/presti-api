from sqlmodel import Session
from api.models.generation_models import Generation
from database.connection import get_db
from api.models.generation_models import Generation


# Assuming you have a Pydantic/SQLModel schema for creation, e.g., GenerationCreate


def create_generation(generation: Generation, db: Session = next(get_db())):
    """
    Create a new generation record in the database.
    """
    db.add(generation)
    db.commit()
    db.refresh(generation)
    return generation
