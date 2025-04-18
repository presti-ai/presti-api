from fastapi import APIRouter, Depends

from api.deps.auth import get_user
from .generate_background import router as generate_background_router
from .remove_background import router as remove_background_router
from .erase_object import router as erase_object_router
from .inpaint import router as inpaint_router
from .swap_color import router as swap_color_router


api_router_v1 = APIRouter()

api_router_v1.include_router(generate_background_router)
api_router_v1.include_router(remove_background_router)
api_router_v1.include_router(erase_object_router)
api_router_v1.include_router(inpaint_router)
api_router_v1.include_router(swap_color_router)
