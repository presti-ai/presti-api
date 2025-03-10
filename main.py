from fastapi import FastAPI
from api.endpoints import (
    generate_background,
    remove_background,
    erase_object,
    inpaint,
    swap_color,
)

description = """
### Description
This API provides Presti AI services. The services that are or will be available are:
- Background Generation (/generate_background)
- Background Removal (/remove_background)
- Object Eraser (Magic Eraser) (/erase_object)
- Image Inpainting (Magic Replace & Accessorisation) (/inpaint)
- Color Swap (/swap_color)
- Image Upscaler (docs TBD)
- Image to Video (docs TBD)

The API is currently in beta and subject to change.

### Authentication
You will need your **API key** in order to make requests to this API. To get your API key, please contact us at support@presti.ai. 

Make sure you never share your API key with anyone, and you never commit it to a public repository. Include this key in the `Authorization` header of your requests.
"""

app = FastAPI(
    title="Presti AI API",
    description=description,
    version="2.0.0-beta",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Presti AI Support",
        "email": "support@presti.ai",
    },
)

# Include all routers with appropriate tags
app.include_router(generate_background.router)
app.include_router(remove_background.router)
app.include_router(erase_object.router)
app.include_router(inpaint.router)
app.include_router(swap_color.router)
