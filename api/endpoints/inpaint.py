from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field

router = APIRouter()


class InpaintRequest(BaseModel):
    image_url: HttpUrl = Field(
        ...,
        description="URL of the main image to be modified.",
        example="https://example.com/room.jpg",
    )
    mask_url: HttpUrl = Field(
        ...,
        description="URL of the mask image. Must be the same size as the main image. The white areas in the mask indicate where to apply the inpainting.",
        example="https://example.com/mask.png",
    )
    prompt: str = Field(
        ...,
        description="Text description of what should replace the masked area. Be specific about the appearance, style, and context.",
        example="a modern leather armchair with brown upholstery",
    )


class InpaintResponse(BaseModel):
    image: str = Field(
        ...,
        description="The processed image with the masked area replaced according to the prompt, in base64 format.",
        example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    )


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/inpaint",
    response_model=InpaintResponse,
    responses={
        200: {
            "model": InpaintResponse,
            "description": "Successfully inpainted the masked area",
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

url = "https://api.presti.ai/inpaint"
headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image_url": "https://example.com/room.jpg",
    "mask_url": "https://example.com/mask.png",
    "prompt": "a modern leather armchair with brown upholstery"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
# The result contains the inpainted image in base64 format
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://api.presti.ai/inpaint', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image_url: 'https://example.com/room.jpg',
        mask_url: 'https://example.com/mask.png',
        prompt: 'a modern leather armchair with brown upholstery'
    })
});

const result = await response.json();
// The result contains the inpainted image in base64 format
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://api.presti.ai/inpaint' \\
    -H 'Authorization: Bearer your_api_key_here' \\
    -H 'Content-Type: 'application/json' \\
    -d '{
        "image_url": "https://example.com/room.jpg",
        "mask_url": "https://example.com/mask.png",
        "prompt": "a modern leather armchair with brown upholstery"
    }'
""",
            },
        ]
    },
)
async def inpaint(request: InpaintRequest):
    """
    Replace a masked area in an image with AI-generated content based on a text prompt.

    Requirements:
    - The mask image must be the same size as the main image
    - The mask should be a black and white image where white indicates the area to inpaint
    - The prompt should describe what you want to appear in the masked area

    The function will:
    1. Load both images
    2. Validate mask dimensions
    3. Generate new content based on the prompt
    4. Seamlessly blend the generated content into the original image
    """
    try:
        # TODO: Implement actual inpainting logic
        return InpaintResponse(
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
