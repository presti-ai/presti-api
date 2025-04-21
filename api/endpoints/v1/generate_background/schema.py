from typing import Literal
from pydantic import BaseModel, Field, model_validator


class GenerateBackgroundRequest(BaseModel):
    product_image: str = Field(
        ...,
        description="Base64 encoded image of the product. The image must have a transparent background and the largest dimension must not exceed 1024 pixels. The transparent areas will be replaced with the generated background.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )
    prompt: str = Field(
        ...,
        description="Text description of the desired background scene. Be specific about the environment, style, lighting, and mood you want to create around your product.",
        example="luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset",
    )
    enhance_prompt: bool = Field(
        default=True,
        description="Whether to enhance the prompt with additional details for better image generation. Only applicable for 'presti_v2' model.",
        example=True,
    )
    model: Literal["presti_v2", "presti_v1"] = Field(
        default="presti_v2",
        description="The model to use for image generation. Options include 'presti_v2', 'presti_v1'.",
        example="presti_v2",
    )

    @model_validator(mode="after")
    def check_enhance_prompt_with_model(self) -> "GenerateBackgroundRequest":
        if self.model == "presti_v1" and self.enhance_prompt:
            raise ValueError(
                "Prompt enhancement is only available for the 'presti_v2' model."
            )
        return self


class GenerateBackgroundResponse(BaseModel):
    image: str = Field(
        ...,
        description="The generated image in base64 format",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str
