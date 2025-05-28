from typing import Literal
from pydantic import BaseModel, Field, model_validator


class GenerateBackgroundRequest(BaseModel):
    product_image: str = Field(
        min_length=1,
        description="Base64 encoded image of the product.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )
    prompt: str = Field(
        min_length=1,
        description="Text description of the desired background scene. Be specific about the environment, style, lighting, and mood you want to create around your product.",
        example="luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset",
    )
    enhance_prompt: bool = Field(
        default=True,
        description="Whether to enhance the prompt with additional details for better image generation. Only applicable for 'presti_v2' and 'presti_v3' models.",
        example=True,
    )
    model: Literal["presti_v3", "presti_v2", "presti_v1"] = Field(
        default="presti_v3",
        description="The model to use for image generation. Options include 'presti_v3', 'presti_v2', 'presti_v1'.",
        example="presti_v3",
    )

    @model_validator(mode="after")
    def check_enhance_prompt_with_model(self) -> "GenerateBackgroundRequest":
        if self.model == "presti_v1" and self.enhance_prompt:
            raise ValueError(
                "Prompt enhancement is only available for the 'presti_v2' and 'presti_v3' models."
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
