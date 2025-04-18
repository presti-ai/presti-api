from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field

router = APIRouter()


class GenerateBackgroundRequest(BaseModel):
    product_image_url: HttpUrl = Field(
        ...,
        description="URL of the product image. The image must have a transparent background and the largest dimension must not exceed 1024 pixels. The transparent areas will be replaced with the generated background.",
        example="https://example.com/product.png",
    )
    prompt: str = Field(
        ...,
        description="Text description of the desired background scene. Be specific about the environment, style, lighting, and mood you want to create around your product.",
        example="luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset",
    )


class GenerateBackgroundResponse(BaseModel):
    image: str = Field(
        ...,
        description="The generated image in base64 format",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/generate_background",
    response_model=GenerateBackgroundResponse,
    responses={
        200: {
            "model": GenerateBackgroundResponse,
            "description": "Successfully generated background for the product",
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

url = "https://sdk.presti.ai/generate_background"
headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "product_image_url": "https://example.com/product.png",
    "prompt": "luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
# The result contains the generated image in base64 format
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://sdk.presti.ai/generate_background', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        product_image_url: 'https://example.com/product.png',
        prompt: 'luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset'
    })
});

const result = await response.json();
// The result contains the generated image in base64 format
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://sdk.presti.ai/generate_background' \\
    -H 'Authorization: Bearer your_api_key_here' \\
    -H 'Content-Type: application/json' \\
    -d '{
        "product_image_url": "https://example.com/product.png",
        "prompt": "luxury living room with modern furniture, warm lighting, and a view of the city skyline at sunset"
    }'
""",
            },
        ]
    },
)
async def generate_background(request: GenerateBackgroundRequest):
    """
    Generate a background scene for a product image.

    The input image must meet the following requirements:
    - Product must be on a transparent background
    - The transparent areas will be filled with the generated scene
    - Largest dimension must not exceed 1024 pixels

    The function will generate a background based on the prompt and compose
    the product image over it.
    """
    try:
        # TODO: Implement actual background generation logic
        # 1. Validate image dimensions
        # 2. Check for transparency
        # 3. Generate background
        # 4. Composite product over background
        # 5. Convert to base64
        return GenerateBackgroundResponse(
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
