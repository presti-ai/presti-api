from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from database.utils import check_api_key, get_user_from_api_key
from database.connection import get_db

api_key_header = APIKeyHeader(name="X-PRESTI-API-KEY")


def get_user(
    api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)
):
    if check_api_key(api_key_header, db):
        user = get_user_from_api_key(api_key_header, db)
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
    )
