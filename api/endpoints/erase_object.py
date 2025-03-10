from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field

router = APIRouter()


class EraseObjectRequest(BaseModel):
    image_url: HttpUrl = Field(
        ...,
        description="URL of the main image from which to erase an object.",
        example="https://example.com/room.jpg",
    )
    mask_url: HttpUrl = Field(
        ...,
        description="URL of the mask image. Must be the same size as the main image. The white areas in the mask indicate the object to erase.",
        example="https://example.com/mask.png",
    )


class EraseObjectResponse(BaseModel):
    image: str = Field(
        ...,
        description="The processed image with the object erased, in base64 format. The erased area will be filled using AI-powered inpainting.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/erase_object",
    response_model=EraseObjectResponse,
    responses={
        200: {
            "model": EraseObjectResponse,
            "description": "Successfully erased the object from the image",
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

url = "https://api.presti.ai/erase_object"
headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image_url": "https://example.com/room.jpg",
    "mask_url": "https://example.com/mask.png"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
# The result contains the image with the object erased in base64 format
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://api.presti.ai/erase_object', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image_url: 'https://example.com/room.jpg',
        mask_url: 'https://example.com/mask.png'
    })
});

const result = await response.json();
// The result contains the image with the object erased in base64 format
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://api.presti.ai/erase_object' \\
    -H 'Authorization: Bearer your_api_key_here' \\
    -H 'Content-Type: 'application/json' \\
    -d '{
        "image_url": "https://example.com/room.jpg",
        "mask_url": "https://example.com/mask.png"
    }'
""",
            },
        ]
    },
)
async def erase_object(request: EraseObjectRequest):
    """
    Erase an object from an image using a mask.

    Requirements:
    - The mask image must be the same size as the main image
    - The mask should be a black and white image where white indicates the area to erase
    - The erased area will be filled using AI-powered inpainting

    The function will:
    1. Load both images
    2. Validate mask dimensions
    3. Erase the object
    4. Fill the area intelligently
    """
    try:
        # TODO: Implement actual object erasing logic
        return EraseObjectResponse(
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
