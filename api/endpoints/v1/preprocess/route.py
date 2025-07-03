from fastapi import APIRouter
from .schema import PreprocessRequest, PreprocessResponse
from api.services.preprocess_service import preprocess_image as preprocess_service_image
from fastapi import HTTPException

router = APIRouter()

ACCEPTED_DIMENSIONS = [
    (1024, 1024),
    (1280, 720),
    (720, 1280),
    (768, 920),
    (920, 768),
    (1152, 768),
    (768, 1152),
]


def is_valid_dimension(width, height):
    for w, h in ACCEPTED_DIMENSIONS:
        for mul in [1, 2, 4, 8]:
            if width == w * mul and height == h * mul:
                return True
    return False


@router.post("/preprocess", response_model=PreprocessResponse)
def preprocess_image(request: PreprocessRequest):
    if not is_valid_dimension(request.targetWidth, request.targetHeight):
        raise HTTPException(status_code=400, detail="Invalid target dimensions.")
    result_b64 = preprocess_service_image(
        request.image,
        request.margin,
        request.horizontalAlignment,
        request.verticalAlignment,
        request.targetWidth,
        request.targetHeight,
    )
    return PreprocessResponse(image=result_b64)
