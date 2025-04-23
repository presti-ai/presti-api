import base64
import datetime
from io import BytesIO
import time
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from api.models.generation_models import Generation
from api.services.generation_service import create_generation
from api.utils.runpod import call_runpod_endpoint
from .helpers import postprocess, preprocess
from api.utils.constants import ALLOWED_DIMENSIONS, OUTPAINT_MODELS_URL
import api.utils.image as image_utils
from .schema import ErrorResponse, GenerateBackgroundRequest, GenerateBackgroundResponse
from PIL import Image, UnidentifiedImageError
from api.deps.auth import get_user
from api.models.user_models import User
import api.utils.storage as storage_utils

router = APIRouter()


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
import time
import uuid
import datetime
from fastapi import Depends

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
async def generate_background(
    request: GenerateBackgroundRequest,
    user: User = Depends(get_user),
):
    """
    Generate a background scene for a product image.

    The input image must meet the following requirements:
    - Product must be on a transparent background
    - The transparent areas will be filled with the generated scene
    - Dimensions must be one of the accepted formats:
        - 1024x1024 (1:1)
        - 1280x720 (16:9) or 720x1280 (9:16)
        - 768x920 (4:5) or 920x768 (5:4)
        - 1152x768 (3:2) or 768x1152 (2:3)
        - Multiples of these dimensions (x2, x4, x8) are also accepted.

    The function will generate a background based on the prompt and compose
    the product image over it.
    """
    t0 = time.time()
    # Remove data URI prefix if present
    if request.product_image.startswith("data:image"):
        base64_image_data = request.product_image.split(",")[1]
    else:
        base64_image_data = request.product_image

    try:
        image_data = base64.b64decode(base64_image_data)
        packshot_image = Image.open(BytesIO(image_data))
    except (base64.binascii.Error, UnidentifiedImageError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid base64 image data: {e}",
        )

    image_width, image_height = packshot_image.size

    # Check if the image dimensions are allowed
    if (image_width, image_height) not in ALLOWED_DIMENSIONS:
        allowed_dims_str = ", ".join(
            [f"{w}x{h}" for w, h in sorted(list(ALLOWED_DIMENSIONS))]
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image dimensions ({image_width}x{image_height}). Accepted dimensions are: {allowed_dims_str}.",
        )

    # Pre-process
    payload, final_prompt, seed = preprocess(
        request, packshot_image, image_width, image_height
    )

    # Prepare paths and URLs
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    packshot_image_path = f"api/{user.id}/hd/packshot-{now}_{uuid.uuid4()}.png"
    outpaint_model_url = OUTPAINT_MODELS_URL[request.model]

    # Run upload and RunPod call concurrently
    packshot_upload_task = asyncio.create_task(
        asyncio.to_thread(
            storage_utils.upload_image_pil, packshot_image, packshot_image_path
        )
    )
    runpod_call_task = asyncio.create_task(
        asyncio.to_thread(call_runpod_endpoint, outpaint_model_url, payload)
    )

    packshot_output_url, generation_image = await asyncio.gather(
        packshot_upload_task, runpod_call_task
    )

    # Post-process the image
    processed_generation_image = postprocess(
        generation_image, packshot_image, image_width, image_height
    )

    file_path = f"api/{user.id}/hd/{now}_{uuid.uuid4()}.png"
    output_url = storage_utils.upload_image_pil(processed_generation_image, file_path)

    # Save the generation to the database
    generation = Generation(
        user_id=user.id,
        output_url=output_url,
        packshot_url=packshot_output_url,
        final_prompt=final_prompt,
        original_prompt=request.prompt,
        generation_width=image_width,
        generation_height=image_height,
        seed=seed,
        model=request.model,
        execution_time_ms=int((time.time() - t0) * 1000),
    )
    generation = create_generation(generation)

    # Convert final image to base64 for the response
    final_base64_image = image_utils.image_to_base64_string(processed_generation_image)

    return GenerateBackgroundResponse(image=final_base64_image)
