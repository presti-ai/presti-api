from functools import lru_cache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import (
    generate_background,
    remove_background,
    erase_object,
    inpaint,
    swap_color,
)
from schemas.models import HealthResponse

description = """
### Description
This API provides the Presti AI services. These services are used to generate, edit, and enhance images on the Presti app.

The services that are or will be available are:
- Background Generation (/generate_background)
- Background Removal (/remove_background)
- Object Eraser (Magic Eraser) (/erase_object)
- Image Inpainting (Magic Replace & Accessorisation) (/inpaint)
- Color Swap (/swap_color)
- Image Relight (docs TBD)
- Product Replace (docs TBD)
- Image Upscaler (docs TBD)
- Image to Video (docs TBD)

You can find illustrations of these services in the [Presti app tutorials (click here)](https://presti-ai.notion.site/Presti-AI-Video-Tutorials-FAQ-b7837fa31a8f4760ae9d910a9bf87491).

The API is currently in beta and subject to change.

### Authentication
You will need your **API key** in order to make requests to this API. To get your API key, please contact us at support@presti.ai. 

Make sure you never share your API key with anyone, and you never commit it to a public repository. Include this key in the `Authorization` header of your requests.
"""

app = FastAPI(
    title="Presti AI API",
    description=description,
    version="1.0.0-beta",
    docs_url=None,
    redoc_url="/docs",
    contact={
        "name": "Presti AI Support",
        "email": "support@presti.ai",
    },
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all routers with appropriate tags
app.include_router(generate_background.router)
app.include_router(remove_background.router)
app.include_router(erase_object.router)
app.include_router(inpaint.router)
app.include_router(swap_color.router)


@app.get("/healthcheck", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
