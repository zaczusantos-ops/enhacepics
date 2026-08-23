"""
ChurchPhoto Pro - Multi-Format Image & Camera RAW Loader
Loads and normalizes JPEG, PNG, WebP, TIFF and Camera RAW files (CR2, NEF, ARW, DNG, etc.).
"""

import io
import numpy as np
from PIL import Image
from typing import Tuple, Optional


def load_image_to_rgb_array(image_bytes: bytes, filename: str = "") -> Tuple[np.ndarray, str]:
    """
    Loads an image from raw bytes into a normalized float32 RGB numpy array [0.0 .. 1.0].
    Returns (image_array, detected_format).
    """
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    raw_extensions = {"cr2", "cr3", "nef", "arw", "dng", "orf", "rw2", "pef", "raf"}

    # Attempt RAW decoding if file extension indicates camera RAW
    if ext in raw_extensions:
        raw_arr = _try_load_raw(image_bytes)
        if raw_arr is not None:
            return raw_arr, f"RAW ({ext.upper()})"

    # Standard image loading with PIL (JPEG, PNG, WebP, TIFF)
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Handle EXIF orientation
        try:
            from PIL import ImageOps
            pil_img = ImageOps.exif_transpose(pil_img)
        except Exception:
            pass

        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        arr = np.array(pil_img, dtype=np.float32) / 255.0
        fmt = pil_img.format or ext.upper() or "JPEG"
        return arr, fmt
    except Exception as e:
        raise ValueError(f"Failed to decode image file: {str(e)}")


def _try_load_raw(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Attempts to decode RAW file using rawpy if available, or extracts embedded preview.
    """
    try:
        import rawpy
        with rawpy.imread(io.BytesIO(image_bytes)) as raw:
            # Process RAW to standard sRGB 8-bit array with camera white balance
            rgb = raw.postprocess(
                use_camera_wb=True,
                half_size=False,
                no_auto_bright=False,
                output_bps=8,
                output_color=rawpy.ColorSpace.sRGB
            )
            return rgb.astype(np.float32) / 255.0
    except Exception as e:
        print(f"[RawLoader] rawpy decoding failed or unavailable: {e}. Attempting fallback preview extraction.")

    # Fallback: Try PIL or extract embedded JPEG from RAW stream
    try:
        # Search for embedded JPEG SOI marker (0xFFD8FFE0 or 0xFFD8FFE1)
        soi_idx = image_bytes.find(b"\xff\xd8\xff")
        if soi_idx != -1:
            jpeg_candidate = image_bytes[soi_idx:]
            pil_img = Image.open(io.BytesIO(jpeg_candidate)).convert("RGB")
            return np.array(pil_img, dtype=np.float32) / 255.0
    except Exception:
        pass

    return None
