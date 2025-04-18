from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps.auth import get_user
from api.endpoints.v1.router import api_router_v1

from api.endpoints.healthcheck.route import router as healthcheck_router

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


# Healthcheck endpoint
app.include_router(healthcheck_router)
app.include_router(api_router_v1, prefix="/v1", dependencies=[Depends(get_user)])
