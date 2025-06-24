from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from decouple import config
import sentry_sdk

from fastapi.exceptions import RequestValidationError
from api.deps.auth import get_user
from api.endpoints.v1.router import api_router_v1

from api.endpoints.healthcheck.route import router as healthcheck_router

description = """
### Description
This API provides the Presti AI services. These services are used to generate, edit, and enhance images on the Presti app.

The services that are ALREADY available are:
- Background Generation (/generate_background)
- Background Removal (/remove_background)

The services that can be developed upon request are:
- Image Upscaler
- Object Eraser (Magic Eraser)
- Image Inpainting (Magic Replace & Accessorisation)
- Color Swap
- Image Relight
- Product Replace
- Image to Video

You can find illustrations of these services in the [Presti app tutorials (click here)](https://presti-ai.notion.site/2-Video-Tutorials-1c080e96f63d80a3a0bae99c97320716).

The API is currently in beta and subject to change.

### Authentication
You will need your **API key** in order to make requests to this API. To get your API key, please contact us at support@presti.ai. 

Make sure you never share your API key with anyone, and you never commit it to a public repository. Include this key in the `Authorization` header of your requests.
"""

SENTRY_DSN = config("SENTRY_DSN", cast=str)
sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # To collect profiles for all profile sessions,
    # set `profile_session_sample_rate` to 1.0.
    profile_session_sample_rate=1.0,
    # Profiles will be automatically collected while
    # there is an active span.
    profile_lifecycle="trace",
)


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    simple_errors = []
    errors = exc.errors()
    for error in errors:
        loc = error.get("loc")
        msg = error.get("msg")
        if loc and msg:
            field = loc[-1] if isinstance(loc[-1], str) else "unknown"
            simple_errors.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": simple_errors,
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


app.include_router(api_router_v1, prefix="/v1", dependencies=[Depends(get_user)])
app.include_router(healthcheck_router)
