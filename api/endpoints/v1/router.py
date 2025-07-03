from fastapi import APIRouter

from .generate_background.route import router as generate_background_router
from .remove_background.route import router as remove_background_router
from .preprocess.route import router as preprocess_router

# from .erase_object import router as erase_object_router
# from .inpaint.route import router as inpaint_router
# from .swap_color.route import router as swap_color_router


api_router_v1 = APIRouter()

api_router_v1.include_router(generate_background_router)
api_router_v1.include_router(remove_background_router)
api_router_v1.include_router(preprocess_router)
# api_router_v1.include_router(erase_object_router)
# api_router_v1.include_router(inpaint_router)
# api_router_v1.include_router(swap_color_router)
