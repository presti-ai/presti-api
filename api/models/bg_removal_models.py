import datetime
import uuid

from sqlmodel import Field, SQLModel


class BackgroundRemoval(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    execution_time_ms: int
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now, nullable=False
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now, nullable=False
    )

    __tablename__ = "bg_removals"
