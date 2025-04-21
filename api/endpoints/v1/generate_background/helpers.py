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
    model: Literal["presti_v1", "presti_v2"],
    translated_prompt: str,
    enhance_prompt: bool,
    base64_string: str,
    seed: int,
    width: Optional[int],
    height: Optional[int],
) -> tuple[dict, str]:
    if model == "presti_v1":
        # SDXM Model
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
            }
        }
        # if model in OUTPAINTING_MODEL_PARAMETERS:
        #     payload["input"].update(OUTPAINTING_MODEL_PARAMETERS[model])

    elif model in FLUX_ASSISTED_PROMPT_MODELS:
        final_prompt = f"{translated_prompt}, high resolution, professional photography"
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
    else:
        raise HTTPException(
            status_code=400, detail="Invalid model or model not implemented"
        )

    return payload, final_prompt
