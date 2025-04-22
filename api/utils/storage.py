from requests.exceptions import SSLError, ConnectionError
import aiohttp
from gcloud.aio.storage import Storage

from io import BytesIO
from google.cloud import storage
from PIL import Image
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

BUCKET_NAME = "presti-tmp-test"
DESTINATION_FOLDER = "gallery"

storage_client = None
async_storage_client = None
aiohttp_session = None


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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((SSLError, ConnectionError)),
)
def upload_image(image: bytes, file_path: str) -> str:
    """Uploads image bytes with retries."""
    path_uploaded_image = f"{DESTINATION_FOLDER}/{file_path}"
    return upload_blob_from_memory(BUCKET_NAME, image, path_uploaded_image)


def upload_image_pil(image: Image, file_path: str, format: str = "PNG") -> str:
    buffered = BytesIO()
    image.save(buffered, format=format)
    url = upload_image(buffered.getvalue(), file_path)
    return url


# --- Async versions using gcloud-aio-storage ---


async def get_async_storage_client() -> tuple[aiohttp.ClientSession, Storage]:
    """Get or create an async storage client and session."""
    global async_storage_client
    global aiohttp_session
    if not aiohttp_session:
        aiohttp_session = aiohttp.ClientSession()
    if not async_storage_client:
        async_storage_client = Storage(session=aiohttp_session)
    return aiohttp_session, async_storage_client


async def close_async_storage_client():
    """Close the shared aiohttp session."""
    global aiohttp_session
    if aiohttp_session:
        await aiohttp_session.close()
        aiohttp_session = None


async def upload_blob_from_memory_async(
    bucket_name: str, contents: bytes, destination_blob_name: str
) -> str:
    """Uploads data to a blob in the bucket asynchronously."""
    _session, storage_client = await get_async_storage_client()
    # Note: gcloud-aio-storage upload doesn't return the public URL directly.
    # We construct it manually. Ensure the object has public read access if needed.
    await storage_client.upload(bucket_name, destination_blob_name, contents)
    # Construct the public URL (adjust if using different access control)
    public_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    return public_url


# Note: The synchronous @retry decorator is removed.
# Using tenacity for async retries.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (aiohttp.ClientError, aiohttp.ClientConnectionError, aiohttp.ClientSSLError)
    ),
)
async def upload_image_async(image: bytes, file_path: str) -> str:
    """Uploads image bytes asynchronously with retries."""
    path_uploaded_image = f"{DESTINATION_FOLDER}/{file_path}"
    return await upload_blob_from_memory_async(BUCKET_NAME, image, path_uploaded_image)


async def upload_image_pil_async(
    image: Image, file_path: str, format: str = "PNG"
) -> str:
    """Saves a PIL image to a buffer and uploads it asynchronously."""
    print("Uploading image asynchronously...")
    buffered = BytesIO()
    image.save(buffered, format=format)
    buffered.seek(0)  # Reset buffer position to the beginning
    url = await upload_image_async(buffered.getvalue(), file_path)
    print("Image uploaded successfully.")
    return url
