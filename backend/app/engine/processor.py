"""
ChurchPhoto Pro - Unified 3-Stage Deterministic DSLR Image Processor Pipeline
Orchestrates:
- Vertente 1: Cor, Iluminação & Estilo (Look Cinematográfico)
- Vertente 2: Correção de Falhas, Anomalias de Lente & Luz Extrema
- Vertente 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh)
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
from .optical_corrections import (
    correct_chromatic_aberration,
    restore_extreme_led_clipping,
    correct_lens_vignetting_and_distortion,
    apply_selective_denoise,
)
from .depth_bokeh import (
    apply_optical_bokeh_and_dof,
    apply_subject_microcontrast,
)
from .stage_lighting import attenuate_stage_led_spill
from .skin_tones import protect_and_restore_skin_tones
from .raw_loader import load_image_to_rgb_array


class ChurchPhotoProcessor:
    """
    High-performance deterministic post-processing pipeline for church & event photography.
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
        Executes the 3-stage DSLR processing pipeline.
        Returns:
            (processed_bytes, processed_base64, metadata, original_base64)
        """
        start_time = time.time()

        # Step 0: Decode input image / RAW format to float32 [0..1]
        original_rgb, detected_format = load_image_to_rgb_array(image_bytes, filename)
        height, width, _ = original_rgb.shape
        current = original_rgb.copy()

        # =========================================================================
        # VERTENTE 2: Correção de Falhas, Anomalias de Lente & Luz Extrema
        # =========================================================================
        
        # Step 1: Selective Edge-preserving Denoising (High-ISO thermal noise reduction)
        current = apply_selective_denoise(
            current,
            strength=params.selective_denoise
        )

        # Step 2: Chromatic Aberration Fringe Suppression (Purple/Green halos around stage lights)
        current = correct_chromatic_aberration(
            current,
            strength=params.chromatic_aberration_fix
        )

        # Step 3: Extreme Stage LED Highlight Clipping Reconstruction
        current = restore_extreme_led_clipping(
            current,
            strength=params.led_clipping_restoration
        )

        # Step 4: Smartphone Lens Vignetting & Barrel Distortion Compensation
        current = correct_lens_vignetting_and_distortion(
            current,
            vignette_strength=params.vignette_correction,
            distortion_strength=params.lens_distortion_correction
        )

        # Step 5: Stage LED Spill Mitigation on Ambient Atmosphere
        current = attenuate_stage_led_spill(
            current,
            stage_led_suppression=params.stage_led_tint_suppression,
            blue_attenuation=params.blue_led_attenuation,
            red_magenta_attenuation=params.red_magenta_attenuation
        )

        # =========================================================================
        # VERTENTE 1: Cor, Iluminação & Estilo (Look Cinematográfico/Culto)
        # =========================================================================

        # Step 6: Exposure Compensation with Soft Knee Rolloff
        current = apply_exposure_compensation(
            current,
            ev=params.exposure_compensation
        )

        # Step 7: White Balance (Kelvin) & Tint Balance
        current = apply_white_balance_and_tint(
            current,
            kelvin=params.temperature_kelvin,
            tint=params.tint
        )

        # Step 8: Highlights Recovery & Shadows Lift
        current = apply_highlights_and_shadows(
            current,
            highlights_recovery=params.highlights_recovery,
            shadows_lift=params.shadows_lift
        )

        # Step 9: Contrast S-Curve
        current = apply_s_curve_contrast(
            current,
            contrast=params.contrast
        )

        # Step 10: Saturation & Vibrance
        current = apply_saturation(
            current,
            saturation=params.saturation,
            vibrance=params.vibrance
        )

        # Step 11: Skin Tone Melanin Protection & Natural Warmth
        current = protect_and_restore_skin_tones(
            processed_rgb=current,
            original_rgb=original_rgb,
            protection_strength=params.skin_tone_protection_strength
        )

        # =========================================================================
        # VERTENTE 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh)
        # =========================================================================

        # Step 12: Optical Bokeh Simulation & Subject Microcontrast Sharpening
        current = apply_optical_bokeh_and_dof(
            current,
            focal_x=params.focal_point_x,
            focal_y=params.focal_point_y,
            f_stop=params.f_stop_simulation,
            bokeh_smoothness=params.bokeh_smoothness,
            subject_microcontrast=params.subject_microcontrast
        )

        # =========================================================================
        # EXPORTAÇÃO E METADADOS
        # =========================================================================
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

        # Original preview base64
        original_base64 = None
        if include_original_preview:
            orig_pil = Image.fromarray((original_rgb * 255.0).astype(np.uint8))
            orig_buffer = io.BytesIO()
            orig_pil.save(orig_buffer, format="JPEG", quality=85)
            original_base64 = f"data:image/jpeg;base64,{base64.b64encode(orig_buffer.getvalue()).decode('utf-8')}"

        # RGB Histogram
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
