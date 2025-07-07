import datetime
import uuid
from typing import Dict, Any

from sqlmodel import Field, SQLModel, JSON, Column


class Preprocess(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    execution_time_ms: int

    # Parameters as received from the request
    margin: Dict[str, Any] = Field(
        sa_column=Column(JSON)
    )  # JSON field: {"percentage": 0.1} or {"left": 50, "right": 30, "top": 20, "bottom": 40}
    horizontal_alignment: str  # "left", "center", "right"
    vertical_alignment: str  # "top", "center", "bottom"
    target_width: int
    target_height: int

    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now, nullable=False
    )

    __tablename__ = "preprocesses"
