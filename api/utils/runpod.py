import os
from typing import List, Union

from decouple import config
import requests
from PIL import Image
from retry import retry

from api.utils.image import base64_string_to_image


def extract_base64_content(base64_string: str, output_format: str) -> str:
    """Remove the data URL prefix if present."""
    prefix = f"data:image/{output_format};base64,"
    return (
        base64_string[len(prefix) :]
        if base64_string.startswith(prefix)
        else base64_string
    )


@retry(tries=3, delay=1, backoff=2)
def call_runpod_endpoint(
    url: str, payload: dict, output_format: str = "png"
) -> Union[Image.Image, List[Image.Image]]:
    """Call a RunPod endpoint and process the image response.

    Args:
        url: The RunPod endpoint URL
        payload: The request payload
        output_format: The expected image format (default: png)

    Returns:
        A single image or list of images depending on the response

    Raises:
        requests.exceptions.HTTPError: If the API request fails
        ValueError: If the response cannot be parsed or processed
    """
    headers = {
        "Authorization": f"Bearer {config('RUNPOD_API_KEY', cast=str)}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises HTTPError for bad responses

    response_json = response.json()
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
