import os
from fastapi import HTTPException

from api.endpoints.v1.generate_background.schema import GenerateBackgroundRequest
import api.utils.image as image_utils
import api.utils.translate as translate_utils
from PIL import Image
from decouple import config
from typing import Literal, Optional

from openai import OpenAI
from retry import retry

from api.utils.constants import FLUX_PROMPTING_SYSTEM_INSTRUCTIONS, NEGATIVE_PROMPT


@retry(tries=3, delay=1, backoff=2)
def get_flux_improved_prompt(translated_prompt: str, product_image: str) -> str:
    client = OpenAI(api_key=config("OPENAI_API_KEY", cast=str))

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": FLUX_PROMPTING_SYSTEM_INSTRUCTIONS},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Improve the following Flux prompt: {translated_prompt}. You need to first guess the packshot type using the image provided. Position it logically in the improved Flux prompt at the very beginning.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": product_image,
                        },
                    },
                ],
            },
        ],
    )

    return response.choices[0].message.content


def get_payload_for_model(
    model: Literal["presti_v1", "presti_v2", "presti_v3"],
    translated_prompt: str,
    enhance_prompt: bool,
    base64_string: str,
    seed: int,
    width: Optional[int],
    height: Optional[int],
) -> tuple[dict, str]:
    if model == "presti_v1":
        # SDXL Model
        final_prompt = f"{translated_prompt}, high resolution, professional photography"
        payload = {
            "input": {
                "prompt": final_prompt,
                "image": base64_string,
                "num_outputs": 1,
                "nb_steps": 50,
                "negative_prompt": NEGATIVE_PROMPT,
                "seed": seed,
            }
        }

    elif model == "presti_v2":
        # FLUX V2 Model
        final_prompt = (
            get_flux_improved_prompt(translated_prompt, base64_string)
            if enhance_prompt
            else translated_prompt + ", high resolution, professional photography"
        )
        payload = {
            "input": {
                "prompt": final_prompt,
                "image": base64_string,
                "num_outputs": 1,
                "nb_steps": 30,
                "seed": seed,
                "width": width,
                "height": height,
                "true_guidance_scale": 2.5,
            }
        }

    elif model == "presti_v3":
        # FLUX V5 Model
        final_prompt = (
            get_flux_improved_prompt(translated_prompt, base64_string)
            if enhance_prompt
            else translated_prompt + ", high resolution, professional photography"
        )
        payload = {
            "input": {
                "prompt": final_prompt,
                "image": base64_string,
                "num_outputs": 1,
                "nb_steps": 30,
                "seed": seed,
                "guidance_scale": 5.0,
                "guidance_scale_controlnet": 3.5,
                "linear_conditioning_scale": True,
                "true_guidance_scale": 1.0,
                "controlnet_conditioning_scale": 1.0,
            }
        }

    return payload, final_prompt


def preprocess(
    request: GenerateBackgroundRequest,
    packshot_image: Image.Image,
    width: int,
    height: int,
) -> tuple[dict, str, str]:
    # Prepare the control image
    control_image = Image.new("RGBA", (width, height))
    alpha_channel = packshot_image.split()[3]
    if request.model in ["presti_v2", "presti_v3"]:
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

    seed = int.from_bytes(os.urandom(2), "big")

    # Prepare payload for each model type
    payload, final_prompt = get_payload_for_model(
        model=request.model,
        translated_prompt=translated_prompt,
        base64_string=base64_string,
        enhance_prompt=request.enhance_prompt,
        seed=seed,
        width=width,
        height=height,
    )
    return payload, final_prompt, seed


def postprocess(
    image: Image.Image, packshot_image: Image.Image, width: int, height: int
):
    # Crop the generated image to the original resolution and re-paste the packshot
    generation_image = image_utils.crop_image(
        image=image,
        original_width=width,
        original_height=height,
    )
    generation_image.paste(
        im=packshot_image,
        mask=packshot_image,
    )
    return generation_image
