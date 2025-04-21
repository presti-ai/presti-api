import base64
from io import BytesIO
from PIL import Image


def image_to_base64_string(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    base64_bytes = base64.b64encode(buffered.getvalue())
    base64_string = base64_bytes.decode()
    return f"data:image/png;base64,{base64_string}"


def base64_string_to_image(bytes64_string: str) -> Image.Image:
    image_bytes = base64.b64decode(bytes64_string)
    return Image.open(BytesIO(image_bytes))


def crop_image(
    image: Image.Image,
    original_width: int,
    original_height: int,
) -> Image.Image:
    """Crop image to remove the padding added by pad_image."""
    width_added = image.width - original_width
    height_added = image.height - original_height

    left_remove = width_added // 2
    right_remove = width_added - left_remove
    top_remove = height_added // 2
    bottom_remove = height_added - top_remove

    return image.crop(
        (
            left_remove,
            top_remove,
            image.width - right_remove,
            image.height - bottom_remove,
        )
    )
