from pydantic import BaseModel, Field


class RemoveBackgroundRequest(BaseModel):
    image: str = Field(
        ...,
        description="Base64 encoded string of the image from which to remove the background. The image will be processed to separate the main subject from its background.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class RemoveBackgroundResponse(BaseModel):
    image: str = Field(
        ...,
        description="The processed image with background removed, in base64 format. The image will have a transparent background.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str
