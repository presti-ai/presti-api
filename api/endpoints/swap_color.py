from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
import re

router = APIRouter()


def validate_hex_color(v: str) -> str:
    """Validate hex color code."""
    if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
        raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
    return v


class SwapColorRequest(BaseModel):
    image_url: HttpUrl = Field(
        ...,
        description="URL of the main image to be modified.",
        example="https://example.com/product.jpg",
    )
    mask_url: HttpUrl = Field(
        ...,
        description="URL of the mask image. Must be the same size as the main image. The white areas in the mask indicate where to apply the color change.",
        example="https://example.com/mask.png",
    )
    color: str = Field(
        ...,
        description="The target color in hexadecimal format (e.g., #FF0000 for red).",
        example="#FF0000",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )


class SwapColorResponse(BaseModel):
    image: str = Field(
        ...,
        description="The processed image with the color changed in the masked area, in base64 format.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/swap_color",
    response_model=SwapColorResponse,
    responses={
        200: {
            "model": SwapColorResponse,
            "description": "Successfully changed the color in the masked area",
            "content": {
                "application/json": {
                    "example": {
                        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                    }
                }
            },
        },
        401: {"model": ErrorResponse, "description": "API Key missing"},
        403: {"model": ErrorResponse, "description": "Invalid API Key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "Python",
                "source": """
import requests

url = "https://sdk.presti.ai/swap_color"
headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image_url": "https://example.com/product.jpg",
    "mask_url": "https://example.com/mask.png",
    "color": "#FF0000"  # Red color in hex format
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
# The result contains the color-modified image in base64 format
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://sdk.presti.ai/swap_color', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image_url: 'https://example.com/product.jpg',
        mask_url: 'https://example.com/mask.png',
        color: '#FF0000'  // Red color in hex format
    })
});

const result = await response.json();
// The result contains the color-modified image in base64 format
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://sdk.presti.ai/swap_color' \\
    -H 'Authorization: Bearer your_api_key_here' \\
    -H 'Content-Type: 'application/json' \\
    -d '{
        "image_url": "https://example.com/product.jpg",
        "mask_url": "https://example.com/mask.png",
        "color": "#FF0000"
    }'
""",
            },
        ]
    },
)
async def swap_color(request: SwapColorRequest):
    """
    Change the color of a masked area in an image.

    Requirements:
    - The mask image must be the same size as the main image
    - The mask should be a black and white image where white indicates the area to recolor
    - The color must be provided in hexadecimal format (e.g., #FF0000 for red)

    The function will:
    1. Load both images
    2. Validate mask dimensions
    3. Apply the color change to the masked area
    4. Preserve lighting and texture while changing the base color
    """
    try:
        # TODO: Implement actual color swapping logic
        return SwapColorResponse(
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
