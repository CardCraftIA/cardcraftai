"""Bounded, metadata-free upload decoding before any paid analysis."""
from io import BytesIO
from pathlib import Path
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_PIXELS = 25_000_000
FORMATS = {'JPEG': ({'.jpg', '.jpeg'}, {'image/jpeg'}),
           'PNG': ({'.png'}, {'image/png'}), 'WEBP': ({'.webp'}, {'image/webp'})}


def load_upload(upload, max_bytes=15 * 1024 * 1024, max_pixels=MAX_IMAGE_PIXELS):
    if int(getattr(upload, 'size', 0) or 0) > max_bytes:
        raise ValueError('Image exceeds byte limit')
    upload.seek(0)
    data = upload.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise ValueError('Invalid image size')
    extension = Path(getattr(upload, 'name', '')).suffix.lower()
    mime = str(getattr(upload, 'type', '') or '').lower()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as probe:
                allowed = FORMATS.get(probe.format)
                if not allowed or (extension and extension not in allowed[0]):
                    raise ValueError('Unsupported image format')
                if mime and mime not in allowed[1] | {'application/octet-stream'}:
                    raise ValueError('MIME does not match image')
                if probe.width * probe.height > max_pixels or getattr(probe, 'n_frames', 1) != 1:
                    raise ValueError('Image exceeds pixel/frame limit')
                probe.verify()
            with Image.open(BytesIO(data)) as decoded:
                decoded.load()
                result = ImageOps.exif_transpose(decoded).convert('RGB')
                result.info.clear()
                return result
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        raise ValueError('Invalid image') from error
