from pydantic import BaseModel, Field
from typing import Union, Dict, Literal


class PreprocessRequest(BaseModel):
    image: str = Field(
        ...,
        description="Base64 encoded string of the image to preprocess. The image will have its background removed, margins added, and be aligned on a target canvas.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )
    margin: Union[float, Dict[str, float]] = Field(
        default=0.1,
        description="Margin to add around the image. Can be a float (percentage of image size, e.g., 0.1 = 10% on all sides) or a dict with specific values for each side: {'left': 50, 'right': 30, 'top': 20, 'bottom': 40}",
        example=0.1,
    )
    horizontal_alignment: Literal["left", "center", "right"] = Field(
        default="center",
        description="Horizontal alignment of the image within the target canvas. 'left' positions the image at the left edge, 'center' centers it horizontally, 'right' positions it at the right edge.",
        example="center",
    )
    vertical_alignment: Literal["top", "center", "bottom"] = Field(
        default="center",
        description="Vertical alignment of the image within the target canvas. 'top' positions the image at the top edge, 'center' centers it vertically, 'bottom' positions it at the bottom edge.",
        example="center",
    )
    target_width: int = Field(
        ...,
        description="Target width of the output image in pixels. Dimensions must be one of the accepted formats: 1024x1024 (1:1), 1280x720 (16:9) or 720x1280 (9:16), 768x920 (4:5) or 920x768 (5:4), 1152x768 (3:2) or 768x1152 (2:3). Multiples of these dimensions (x2, x4, x8) are also accepted.",
        example=1024,
    )
    target_height: int = Field(
        ...,
        description="Target height of the output image in pixels. Dimensions must be one of the accepted formats: 1024x1024 (1:1), 1280x720 (16:9) or 720x1280 (9:16), 768x920 (4:5) or 920x768 (5:4), 1152x768 (3:2) or 768x1152 (2:3). Multiples of these dimensions (x2, x4, x8) are also accepted.",
        example=1024,
    )

    class Config:
        schema_extra = {
            "example": {
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "margin": 0.1,
                "horizontal_alignment": "center",
                "vertical_alignment": "center",
                "target_width": 1024,
                "target_height": 1024,
            }
        }


class PreprocessResponse(BaseModel):
    image: str = Field(
        ...,
        description="The preprocessed image with background removed, margins added, and aligned on the target canvas, returned as base64 string.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )
