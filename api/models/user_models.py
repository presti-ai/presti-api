import uuid

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    api_key: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)

    __tablename__ = "users"
