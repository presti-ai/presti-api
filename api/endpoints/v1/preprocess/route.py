from fastapi import APIRouter, HTTPException
from .schema import PreprocessRequest, PreprocessResponse
from api.services.preprocess_service import preprocess_image as preprocess_service_image

router = APIRouter()

# Accepted dimensions and their multiples
ACCEPTED_DIMENSIONS = [
    (1024, 1024),
    (1280, 720),
    (720, 1280),
    (768, 920),
    (920, 768),
    (1152, 768),
    (768, 1152),
]


def is_valid_dimension(width, height):
    for w, h in ACCEPTED_DIMENSIONS:
        for mul in [1, 2, 4, 8]:
            if width == w * mul and height == h * mul:
                return True
    return False


@router.post(
    "/preprocess",
    response_model=PreprocessResponse,
    responses={
        200: {
            "model": PreprocessResponse,
            "description": "Successfully preprocessed the image",
            "content": {
                "application/json": {
                    "example": {
                        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                    }
                }
            },
        },
        400: {"description": "Invalid target dimensions"},
        401: {"description": "API Key missing"},
        403: {"description": "Invalid API Key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
    openapi_extra={
        "summary": "Preprocess an image by removing background, adding margins, and aligning on a target canvas",
        "description": """
## Overview
This endpoint preprocesses an image by:
1. **Removing the background** using AI-powered segmentation
2. **Adding margins** around the image (default: 10% on all sides)
3. **Aligning the image** within the target canvas
4. **Resizing to fit** within the target dimensions while maintaining aspect ratio

## Accepted Target Dimensions
The `target_width` and `target_height` must be one of these base dimensions or their multiples (x2, x4, x8):

- **1024x1024** (1:1 square)
- **1280x720** (16:9 landscape) or **720x1280** (9:16 portrait)
- **768x920** (4:5 portrait) or **920x768** (5:4 landscape)
- **1152x768** (3:2 landscape) or **768x1152** (2:3 portrait)

**Multiples allowed:** 1x, 2x, 4x, 8x (e.g., 2048x2048, 2560x1440, etc.)

## Margin Options
- **Float value** (e.g., `0.1`): Adds the same percentage margin on all sides
- **Dictionary** (e.g., `{"left": 50, "right": 30, "top": 20, "bottom": 40}`): Adds specific pixel margins for each side

## Alignment Examples

### Horizontal Alignment
- `"left"`: Image positioned at the left edge of the available space
- `"center"`: Image centered horizontally within the available space
- `"right"`: Image positioned at the right edge of the available space

### Vertical Alignment
- `"top"`: Image positioned at the top edge of the available space
- `"center"`: Image centered vertically within the available space
- `"bottom"`: Image positioned at the bottom edge of the available space

## Example Use Cases
- **Product photography**: Remove background and center product on white canvas
- **Social media**: Align content to specific aspect ratios with consistent margins
- **E-commerce**: Standardize product images with uniform backgrounds and spacing
        """,
        "x-codeSamples": [
            {
                "lang": "Python",
                "source": """
import requests

url = "https://sdk.presti.ai/v1/preprocess"
headers = {
    "X-PRESTI-API-KEY": "your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "margin": 0.1,
    "horizontal_alignment": "center",
    "vertical_alignment": "center",
    "target_width": 1024,
    "target_height": 1024
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result["image"])
""",
            },
            {
                "lang": "JavaScript",
                "source": """
const response = await fetch('https://sdk.presti.ai/v1/preprocess', {
    method: 'POST',
    headers: {
        'X-PRESTI-API-KEY': 'your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        margin: 0.1,
        horizontal_alignment: 'center',
        vertical_alignment: 'center',
        target_width: 1024,
        target_height: 1024
    })
});

const result = await response.json();
console.log(result.image);
""",
            },
            {
                "lang": "cURL",
                "source": """
curl -X POST 'https://sdk.presti.ai/v1/preprocess' \\
    -H 'X-PRESTI-API-KEY: your_api_key_here' \\
    -H 'Content-Type: application/json' \\
    -d '{
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "margin": 0.1,
        "horizontal_alignment": "center",
        "vertical_alignment": "center",
        "target_width": 1024,
        "target_height": 1024
    }'
""",
            },
        ],
    },
)
def preprocess_image(request: PreprocessRequest):
    """
    Preprocess an image by removing background, adding margins, and aligning on a target canvas.

    The function will:
    1. Remove the background from the input image
    2. Crop the image to remove transparent borders
    3. Add margins around the image (default: 10% on all sides)
    4. Resize the image to fit within the target dimensions
    5. Align the image according to the specified parameters
    6. Return the result as a base64 encoded image
    """
    if not is_valid_dimension(request.target_width, request.target_height):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target dimensions. Accepted dimensions: {ACCEPTED_DIMENSIONS} and their multiples (x2, x4, x8)",
        )

    result_b64 = preprocess_service_image(
        request.image,
        request.margin,
        request.horizontal_alignment,
        request.vertical_alignment,
        request.target_width,
        request.target_height,
    )
    return PreprocessResponse(image=result_b64)
