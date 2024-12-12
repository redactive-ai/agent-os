import logging

from google.cloud.secretmanager import SecretManagerServiceClient
from google_crc32c import Checksum

logger = logging.getLogger(__name__)

_gsm_client = SecretManagerServiceClient()

def get_secret(secret_name: str) -> str:
    secret_path = f"projects/redactive-dev/secrets/{secret_name}/versions/latest"

    logger.debug("Getting GSM secret %s", secret_name)
    response = _gsm_client.access_secret_version(request={"name": secret_path})

    crc32c = Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        raise ValueError("Checksum did not match when attempted to fetch a secret")

    return response.payload.data.decode()