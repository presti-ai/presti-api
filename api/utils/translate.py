from decouple import config
from pydantic import BaseModel
from openai import OpenAI
from langdetect import detect
import os
from typing import Tuple
from retry import retry


class TranslatedPromptSchema(BaseModel):
    translated_prompt_to_english: str
    original_prompt_language_ISO_639: str


@retry(tries=3, delay=1, backoff=2)
def translate_prompt_if_needed(prompt: str) -> Tuple[str, str]:
    try:
        prompt_language = detect(prompt)
    except:
        prompt_language = "unknown"

    if prompt_language == "en":
        return prompt, prompt_language

    client = OpenAI(api_key=config("OPENAI_API_KEY", cast=str))
    chat_completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that translates prompts to english if they are not already in english. If the prompt is already in english, you return it as is.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format=TranslatedPromptSchema,
        model="gpt-4o-mini",
    )

    response = chat_completion.choices[0].message.parsed
    return response.translated_prompt_to_english, prompt_language
