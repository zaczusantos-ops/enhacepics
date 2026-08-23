"""
ChurchPhoto Pro - Unified Deterministic Image Processor Pipeline
Orchestrates the deterministic transformation steps and generates high-resolution output with metadata.
"""

import time
import base64
import io
import numpy as np
from PIL import Image
from typing import Tuple, Dict, List, Optional

from ..schemas.colorimetry import ColorimetryParameters, ProcessedImageMetadata
from .color_curves import (
    apply_white_balance_and_tint,
    apply_exposure_compensation,
    apply_highlights_and_shadows,
    apply_s_curve_contrast,
    apply_saturation,
)
from .stage_lighting import attenuate_stage_led_spill
from .skin_tones import protect_and_restore_skin_tones
from .denoise_sharpen import apply_bilateral_denoise, apply_adaptive_unsharp_mask
from .raw_loader import load_image_to_rgb_array


class ChurchPhotoProcessor:
    """
    High-performance deterministic post-processing pipeline for church event photography.
    """

    def process(
        self,
        image_bytes: bytes,
        params: ColorimetryParameters,
        filename: str = "image.jpg",
        output_format: str = "JPEG",
        output_quality: int = 92,
        include_original_preview: bool = True
    ) -> Tuple[bytes, str, ProcessedImageMetadata, Optional[str]]:
        """
        Executes the entire deterministic pipeline.
        Returns:
            (processed_bytes, processed_base64, metadata, original_base64)
        """
        start_time = time.time()

        # Step 1: Decode input image / RAW format to float32 [0..1]
        original_rgb, detected_format = load_image_to_rgb_array(image_bytes, filename)
        height, width, _ = original_rgb.shape

        # Step 2: Denoise High-ISO noise (done early to prevent noise propagation)
        current = apply_bilateral_denoise(
            original_rgb,
            denoise_strength=params.denoise_strength
        )

        # Step 3: Exposure Compensation
        current = apply_exposure_compensation(
            current,
            ev=params.exposure_compensation
        )

        # Step 4: White Balance (Kelvin) & Tint
        current = apply_white_balance_and_tint(
            current,
            kelvin=params.temperature_kelvin,
            tint=params.tint
        )

        # Step 5: Highlights Recovery & Shadows Lift
        current = apply_highlights_and_shadows(
            current,
            highlights_recovery=params.highlights_recovery,
            shadows_lift=params.shadows_lift
        )

        # Step 6: Contrast S-Curve
        current = apply_s_curve_contrast(
            current,
            contrast=params.contrast
        )

        # Step 7: Stage Lighting & LED Spill Mitigation
        current = attenuate_stage_led_spill(
            current,
            stage_led_suppression=params.stage_led_tint_suppression,
            blue_attenuation=params.blue_led_attenuation,
            red_magenta_attenuation=params.red_magenta_attenuation
        )

        # Step 8: Saturation & Vibrance
        current = apply_saturation(
            current,
            saturation=params.saturation
        )

        # Step 9: Skin Tone Melanin Protection & Restoration
        current = protect_and_restore_skin_tones(
            processed_rgb=current,
            original_rgb=original_rgb,
            protection_strength=params.skin_tone_protection_strength
        )

        # Step 10: Adaptive Unsharp Masking
        current = apply_adaptive_unsharp_mask(
            current,
            amount=params.unsharp_mask_amount,
            radius=params.unsharp_mask_radius
        )

        # Step 11: Export to output buffer
        final_uint8 = np.clip(current * 255.0, 0, 255).astype(np.uint8)
        out_pil = Image.fromarray(final_uint8)

        out_buffer = io.BytesIO()
        save_fmt = "JPEG" if output_format.upper() in ["JPEG", "JPG"] else "PNG"
        
        if save_fmt == "JPEG":
            out_pil.save(out_buffer, format="JPEG", quality=output_quality, subsampling=0, optimize=True)
        else:
            out_pil.save(out_buffer, format="PNG", optimize=True)

        processed_bytes = out_buffer.getvalue()
        processed_base64 = f"data:image/{save_fmt.lower()};base64,{base64.b64encode(processed_bytes).decode('utf-8')}"

        # Generate original preview base64 for before/after comparison
        original_base64 = None
        if include_original_preview:
            orig_pil = Image.fromarray((original_rgb * 255.0).astype(np.uint8))
            orig_buffer = io.BytesIO()
            orig_pil.save(orig_buffer, format="JPEG", quality=85)
            original_base64 = f"data:image/jpeg;base64,{base64.b64encode(orig_buffer.getvalue()).decode('utf-8')}"

        # Calculate RGB Histogram
        histogram = self._calculate_histogram(final_uint8)

        execution_time = (time.time() - start_time) * 1000.0

        metadata = ProcessedImageMetadata(
            width=width,
            height=height,
            original_format=detected_format,
            output_format=save_fmt,
            execution_time_ms=round(execution_time, 2),
            parameters_applied=params,
            histogram=histogram
        )

        return processed_bytes, processed_base64, metadata, original_base64

    def _calculate_histogram(self, img_uint8: np.ndarray, bins: int = 64) -> Dict[str, List[int]]:
        """
        Calculates compressed RGB histogram for visual telemetry in the UI.
        """
        hist_r, _ = np.histogram(img_uint8[:, :, 0], bins=bins, range=(0, 256))
        hist_g, _ = np.histogram(img_uint8[:, :, 1], bins=bins, range=(0, 256))
        hist_b, _ = np.histogram(img_uint8[:, :, 2], bins=bins, range=(0, 256))

        # Normalize to 0..100
        max_val = max(hist_r.max(), hist_g.max(), hist_b.max(), 1)
        return {
            "r": [int(x * 100 / max_val) for x in hist_r],
            "g": [int(x * 100 / max_val) for x in hist_g],
            "b": [int(x * 100 / max_val) for x in hist_b],
        }
