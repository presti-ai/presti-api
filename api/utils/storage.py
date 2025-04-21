from requests.exceptions import SSLError, ConnectionError

from io import BytesIO
from google.cloud import storage
from PIL import Image
from retry import retry

BUCKET_NAME = "presti-tmp-test"
DESTINATION_FOLDER = "gallery"

storage_client = None


# To cache the google cloud storage client
def get_storage_client() -> storage.Client:
    global storage_client
    if not storage_client:
        storage_client = storage.Client()
    return storage_client


def upload_blob_from_memory(
    bucket_name: str, contents: bytes, destination_blob_name: str
) -> str:
    """Uploads a file to the bucket."""

    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(contents)

    return blob.public_url


@retry(exceptions=(SSLError, ConnectionError), tries=3, delay=1, backoff=2)
def upload_image(image: bytes, file_path: str) -> str:
    path_uploaded_image = f"{DESTINATION_FOLDER}/{file_path}"
    return upload_blob_from_memory(BUCKET_NAME, image, path_uploaded_image)


def upload_image_pil(image: Image, file_path: str, format: str = "PNG") -> str:
    buffered = BytesIO()
    image.save(buffered, format=format)
    url = upload_image(buffered.getvalue(), file_path)
    return url
