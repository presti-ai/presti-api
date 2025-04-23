import http.client
import io
from decouple import config
import uuid
from fastapi import HTTPException
from PIL import Image
from retry import retry


@retry(tries=3, delay=1, backoff=2)
def remove_background_helper(input_image: Image.Image) -> Image.Image:
    # Define multipart boundary
    boundary = "----------{}".format(uuid.uuid4().hex)

    # Convert the PIL Image to bytes (ensure PNG format for PhotoRoom)
    image_io = io.BytesIO()
    # Ensure the image has a format attribute, default to PNG if not present or needed
    image_format = getattr(input_image, "format", "PNG")

    input_image.save(image_io, format=image_format)
    image_data = image_io.getvalue()

    # Generate a filename (optional, for content-disposition header)
    filename = f"image.{image_format.lower()}"

    # Set the content type
    content_type = f"image/{image_format.lower()}"

    # Prepare the POST data
    body = (
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image_file"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
        + image_data
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    # Set up the HTTP connection and headers
    conn = http.client.HTTPSConnection("sdk.photoroom.com")
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "x-api-key": config("PHOTOROOM_API_KEY"),
    }

    try:
        # Make the POST request
        conn.request("POST", "/v1/segment", body=body, headers=headers)
        response = conn.getresponse()

        # Handle the response
        if response.status == 200:
            response_data = response.read()
            image = Image.open(io.BytesIO(response_data))
            return image
        else:
            print(f"Error: {response.status} - {response.reason}")
            # Read the response body for more details, but be careful with large responses
            error_details = response.read().decode("utf-8", errors="ignore")
            print(error_details)
            raise HTTPException(
                status_code=response.status,  # Use actual status code if appropriate
                detail=f"Error removing background: {response.reason} - {error_details}",
            )
    finally:
        # Ensure the connection is closed
        conn.close()
