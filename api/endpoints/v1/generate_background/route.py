import base64
import datetime
from io import BytesIO
import os
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models.generation_models import Generation
from api.services.generation_service import create_generation
from api.utils.runpod import call_runpod_endpoint
from database.connection import get_db
from .helpers import get_payload_for_model
from api.utils.constants import OUTPAINT_MODELS_URL
import api.utils.image as image_utils
import api.utils.translate as translate_utils
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
    - Largest dimension must not exceed 1024 pixels

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

    authorized_width = 1024
    authorized_height = 1024

    # Check if the image is exactly 1024x1024
    if (
        packshot_image.size[0] != authorized_width
        or packshot_image.size[1] != authorized_height
    ):
        raise HTTPException(
            status_code=400,
            detail="The image must be exactly 1024x1024 pixels.",
        )

    # Prepare the control image
    control_image = Image.new("RGBA", (authorized_width, authorized_height))
    alpha_channel = packshot_image.split()[3]
    if request.model == "presti_v2":
        # For Flux models, we convert to a binary mask to avoid the appearance of an edge, it is very visible on
        # low-res packshots (https://presti-ai.slack.com/archives/C077N5HF9BP/p1738139806501099)
        alpha_channel = alpha_channel.point(lambda x: 255 if x >= 128 else 0)

    control_image.paste(
        im=packshot_image,
        mask=alpha_channel,
    )

    base64_string = image_utils.image_to_base64_string(control_image)

    # Use translate_prompt_if_needed function
    translated_prompt, _ = translate_utils.translate_prompt_if_needed(request.prompt)

    outpaint_model_url = OUTPAINT_MODELS_URL[request.model]

    seed = int.from_bytes(os.urandom(2), "big")

    # Prepare payload for each model type
    payload, final_prompt = get_payload_for_model(
        model=request.model,
        translated_prompt=translated_prompt,
        base64_string=base64_string,
        enhance_prompt=request.enhance_prompt,
        seed=seed,
        width=authorized_width,
        height=authorized_height,
    )

    # Call the RunPod endpoint
    generation_image = call_runpod_endpoint(outpaint_model_url, payload)

    # Crop the generated image to the original resolution and re-paste the packshot
    generation_image = image_utils.crop_image(
        image=generation_image,
        original_width=authorized_width,
        original_height=authorized_height,
    )
    generation_image.paste(
        im=packshot_image,
        mask=packshot_image,
    )

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = f"api/{user.id}/hd/{now}_{uuid.uuid4()}.png"
    output_url = storage_utils.upload_image_pil(generation_image, file_path)

    result = {
        "output_url": output_url,
        "final_prompt": final_prompt,
        "original_prompt": request.prompt,
        "generation_width": authorized_width,
        "generation_height": authorized_height,
        "seed": seed,
        "model": request.model,
        "execution_time_ms": int((time.time() - t0) * 1000),
    }
    print(result)

    # Save the generation to the database
    generation = Generation(
        author_id=user.id,
        output_url=output_url,
        final_prompt=final_prompt,
        original_prompt=request.prompt,
        generation_width=authorized_width,
        generation_height=authorized_height,
        seed=seed,
        model=request.model,
        execution_time_ms=int((time.time() - t0) * 1000),
    )
    generation = create_generation(generation)

    # Convert final image to base64 for the response
    final_base64_image = image_utils.image_to_base64_string(generation_image)

    return GenerateBackgroundResponse(image=final_base64_image)
