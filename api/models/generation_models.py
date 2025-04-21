import datetime
import uuid

from sqlmodel import Field, SQLModel, String

from api.utils.constants import AVAILABLE_MODELS


class Generation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="user.id", index=True, nullable=False)
    output_url: str
    final_prompt: str
    original_prompt: str
    generation_width: int
    generation_height: int
    seed: int
    model: AVAILABLE_MODELS = Field(sa_type=String, nullable=False)
    execution_time_ms: int
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
