from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = config("DATABASE_URL", cast=str)

# Enhanced engine configuration for production
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    client_encoding="utf8",
    poolclass=QueuePool,
    pool_pre_ping=True,  # Verify connections before use (prevents stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
