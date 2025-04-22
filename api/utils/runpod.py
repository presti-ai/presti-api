import os
from typing import List, Union
import aiohttp

from PIL import Image

from api.utils.image import base64_string_to_image


def extract_base64_content(base64_string: str, output_format: str) -> str:
    """Remove the data URL prefix if present."""
    prefix = f"data:image/{output_format};base64,"
    return (
        base64_string[len(prefix) :]
        if base64_string.startswith(prefix)
        else base64_string
    )


async def call_runpod_endpoint_async(
    url: str, payload: dict, output_format: str = "png"
) -> Union[Image.Image, List[Image.Image]]:
    """Asynchronously call a RunPod endpoint and process the image response.

    Args:
        url: The RunPod endpoint URL
        payload: The request payload
        output_format: The expected image format (default: png)

    Returns:
        A single image or list of images depending on the response

    Raises:
        aiohttp.ClientResponseError: If the API request fails
        ValueError: If the response cannot be parsed or processed
    """
    headers = {
        "Authorization": f"Bearer {os.environ['RUNPOD_API_KEY']}",
        "Content-Type": "application/json",
    }

    print("Calling RunPod endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()  # Raises ClientResponseError for bad responses
            response_json = await response.json()
            print("RunPod endpoint response:")

    outputs = (
        [response_json["output"]]
        if isinstance(response_json["output"], str)
        else response_json["output"]
    )

    images = [
        base64_string_to_image(extract_base64_content(output, output_format))
        for output in outputs
    ]

    return images[0] if len(images) == 1 else images
