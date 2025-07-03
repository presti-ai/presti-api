from typing import Union, Dict
from PIL import Image
import api.utils.image as image_utils
from api.endpoints.v1.remove_background.helpers import remove_background_helper

# TODO: Import necessary image processing utilities


def preprocess_image(
    image_b64: str,
    margin: Union[float, Dict[str, float]],
    h_align: str,
    v_align: str,
    target_w: int,
    target_h: int,
) -> str:
    """
    Process the image by removing background, adding margins, aligning, and resizing/canvas.
    Returns the processed image as base64.
    """
    # 1. Convert base64 to PIL Image
    if image_b64.startswith("data:image"):
        image_b64 = image_b64.split(",", 1)[1]
    input_image = image_utils.base64_string_to_image(image_b64)

    # 2. Remove background
    no_bg_image = remove_background_helper(input_image)

    # 3. Add margins
    if isinstance(margin, float) or isinstance(margin, int):
        margin_dict = {k: margin for k in ["left", "right", "top", "bottom"]}
    else:
        margin_dict = {
            k: float(margin.get(k, 0.0)) for k in ["left", "right", "top", "bottom"]
        }

    # Calculate margin in pixels (as percent of image size)
    width, height = no_bg_image.size
    left = (
        int(margin_dict["left"] * width)
        if margin_dict["left"] < 1
        else int(margin_dict["left"])
    )
    right = (
        int(margin_dict["right"] * width)
        if margin_dict["right"] < 1
        else int(margin_dict["right"])
    )
    top = (
        int(margin_dict["top"] * height)
        if margin_dict["top"] < 1
        else int(margin_dict["top"])
    )
    bottom = (
        int(margin_dict["bottom"] * height)
        if margin_dict["bottom"] < 1
        else int(margin_dict["bottom"])
    )

    new_width = width + left + right
    new_height = height + top + bottom
    image_with_margin = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    image_with_margin.paste(no_bg_image, (left, top))

    # 4. Place on target canvas with alignment
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    paste_w, paste_h = image_with_margin.size
    # Horizontal alignment
    if h_align == "left":
        x = 0
    elif h_align == "center":
        x = (target_w - paste_w) // 2
    elif h_align == "right":
        x = target_w - paste_w
    else:
        x = 0
    # Vertical alignment
    if v_align == "top":
        y = 0
    elif v_align == "center":
        y = (target_h - paste_h) // 2
    elif v_align == "bottom":
        y = target_h - paste_h
    else:
        y = 0
    canvas.paste(image_with_margin, (x, y), image_with_margin)

    # 5. Return as base64
    return image_utils.image_to_base64_string(canvas)
