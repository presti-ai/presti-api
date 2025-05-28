import base64
import io
import time
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, Depends, HTTPException

from api.deps.auth import get_user
from api.models.bg_removal_models import BackgroundRemoval
from api.models.user_models import User
from api.services.bg_removal_service import create_bg_removal
import api.utils.image as image_utils
from .helpers import remove_background_helper
from .schema import RemoveBackgroundRequest, RemoveBackgroundResponse, ErrorResponse

router = APIRouter()


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

url = "https://sdk.presti.ai/v1/remove_background"
headers = {
    "X-PRESTI-API-KEY": "your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
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
    const response = await fetch('https://sdk.presti.ai/v1/remove_background', {
    method: 'POST',
    headers: {
        'X-PRESTI-API-KEY': 'your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
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
curl -X POST 'https://sdk.presti.ai/v1/remove_background' \\
    -H 'X-PRESTI-API-KEY: your_api_key_here' \\
    -H 'Content-Type: 'application/json' \\
    -d '{
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }'
""",
            },
        ]
    },
)
def remove_background(request: RemoveBackgroundRequest, user: User = Depends(get_user)):
    """
    Remove the background from an image, isolating the main subject.

    The function will:
    1. Process the input image
    2. Identify and isolate the main subject
    3. Remove the background
    4. Return the result with a transparent background
    """
    t0 = time.time()
    # Decode the base64 string
    if request.image.startswith("data:image"):
        base64_image_data = request.image.split(",")[1]
    else:
        base64_image_data = request.image

    try:
        image_data = base64.b64decode(base64_image_data)
        input_image = Image.open(io.BytesIO(image_data))
    except (base64.binascii.Error, UnidentifiedImageError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid base64 image data: {e}",
        )

    result = remove_background_helper(input_image)

    # Convert the result image to base64
    base64_image = image_utils.image_to_base64_string(result)

    db_obj = BackgroundRemoval(
        user_id=user.id,
        execution_time_ms=int((time.time() - t0) * 1000),
    )
    create_bg_removal(db_obj)

    return RemoveBackgroundResponse(image=base64_image)
