from pydantic import BaseModel
from typing import Union, Dict, Literal


class PreprocessRequest(BaseModel):
    image: str  # base64
    margin: Union[float, Dict[str, float]] = 0.0
    horizontalAlignment: Literal["left", "center", "right"] = "center"
    verticalAlignment: Literal["top", "center", "bottom"] = "center"
    targetWidth: int
    targetHeight: int


class PreprocessResponse(BaseModel):
    image: str  # base64
