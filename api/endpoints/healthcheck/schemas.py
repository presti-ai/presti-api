from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(
        description="The status of the service. Should be 'ok' if the service is running correctly.",
        example="ok",
    )
