from PIL import Image
from pyzbar.pyzbar import decode
import pyheif
from io import BytesIO
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ImageProcessor:
    @staticmethod
    def process_image(file_data: bytes, is_heic: bool = False) -> Optional[Image.Image]:
        try:
            if is_heic:
                heif_file = pyheif.read(file_data)
                return Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride
                )
            return Image.open(BytesIO(file_data))
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None

    @staticmethod
    def decode_codes(image: Image.Image) -> List:
        try:
            return decode(image)
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return []
