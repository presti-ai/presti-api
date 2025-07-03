from typing import Union, Dict
from PIL import Image
import api.utils.image as image_utils
from api.endpoints.v1.remove_background.helpers import remove_background_helper

# TODO: Import necessary image processing utilities


def crop_to_content(image: Image.Image) -> Image.Image:
    # Crop out fully transparent borders
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    bbox = image.getbbox()
    if bbox:
        return image.crop(bbox)
    return image


def preprocess_image(
    image_b64: str,
    margin: Union[float, Dict[str, float]],
    h_align: str,
    v_align: str,
    target_w: int,
    target_h: int,
) -> str:
    """
    Process the image by removing background, cropping, adding margins, aligning, and resizing/canvas.
    Returns the processed image as base64.
    """
    # 1. Convert base64 to PIL Image
    if image_b64.startswith("data:image"):
        image_b64 = image_b64.split(",", 1)[1]
    input_image = image_utils.base64_string_to_image(image_b64)

    # 2. Remove background
    no_bg_image = remove_background_helper(input_image)

    # 2b. Crop to content (remove transparent borders)
    no_bg_image = crop_to_content(no_bg_image)

    # 3. Calculate margins
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

    # 4. Calculate available space for the image after margins
    available_width = target_w - left - right
    available_height = target_h - top - bottom

    # 5. Calculate scale factor to fit image within available space
    scale_x = available_width / width if available_width > 0 else 1
    scale_y = available_height / height if available_height > 0 else 1
    scale = min(scale_x, scale_y)  # Use the smaller scale to maintain aspect ratio

    # 6. Resize the image to fit within available space
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = no_bg_image.resize(
        (new_width, new_height), Image.Resampling.LANCZOS
    )

    # 7. Place on target canvas with alignment
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))

    # Calculate position based on alignment
    if h_align == "left":
        x = left
    elif h_align == "center":
        x = left + (available_width - new_width) // 2
    elif h_align == "right":
        x = target_w - right - new_width
    else:
        x = left

    if v_align == "top":
        y = top
    elif v_align == "center":
        y = top + (available_height - new_height) // 2
    elif v_align == "bottom":
        y = target_h - bottom - new_height
    else:
        y = top

    canvas.paste(resized_image, (x, y), resized_image)

    # 8. Return as base64
    return image_utils.image_to_base64_string(canvas)
