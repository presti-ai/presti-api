from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field

router = APIRouter()


class RemoveBackgroundRequest(BaseModel):
    image_url: HttpUrl = Field(
        ...,
        description="URL of the image from which to remove the background. The image will be processed to separate the main subject from its background.",
        example="https://example.com/product.jpg",
    )


class RemoveBackgroundResponse(BaseModel):
    image: str = Field(
        ...,
        description="The processed image with background removed, in base64 format. The image will have a transparent background.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/remove_background",
    response_model=RemoveBackgroundResponse,
    responses={
        200: {
            "model": RemoveBackgroundResponse,
            "description": "Successfully removed background from the image",
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

url = "https://sdk.presti.ai/remove_background"
headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image_url": "https://example.com/product.jpg"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
# The result contains the image with background removed in base64 format
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://sdk.presti.ai/remove_background', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image_url: 'https://example.com/product.jpg'
    })
});

const result = await response.json();
// The result contains the image with background removed in base64 format
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://sdk.presti.ai/remove_background' \\
    -H 'Authorization: Bearer your_api_key_here' \\
    -H 'Content-Type: 'application/json' \\
    -d '{
        "image_url": "https://example.com/product.jpg"
    }'
""",
            },
        ]
    },
)
async def remove_background(request: RemoveBackgroundRequest):
    """
    Remove the background from an image, isolating the main subject.

    The function will:
    1. Process the input image
    2. Identify and isolate the main subject
    3. Remove the background
    4. Return the result with a transparent background
    """
    try:
        # TODO: Implement actual background removal logic
        return RemoveBackgroundResponse(
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
