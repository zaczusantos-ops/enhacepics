"""
Unit tests for deterministic ChurchPhoto 3-Stage DSLR image processing engine.
"""

import numpy as np
from PIL import Image
import io

from backend.app.schemas.colorimetry import ColorimetryParameters
from backend.app.engine.processor import ChurchPhotoProcessor
from backend.app.engine.color_curves import (
    kelvin_to_rgb_multipliers,
    apply_white_balance_and_tint,
    apply_exposure_compensation,
    apply_highlights_and_shadows,
    apply_s_curve_contrast,
    apply_saturation,
)
from backend.app.engine.optical_corrections import (
    correct_chromatic_aberration,
    restore_extreme_led_clipping,
    correct_lens_vignetting_and_distortion,
    apply_selective_denoise,
)
from backend.app.engine.depth_bokeh import (
    generate_depth_and_subject_mask,
    apply_optical_bokeh_and_dof,
    apply_subject_microcontrast,
)
from backend.app.engine.stage_lighting import attenuate_stage_led_spill
from backend.app.engine.skin_tones import protect_and_restore_skin_tones, generate_skin_tone_mask


def create_synthetic_church_image(width=400, height=300) -> bytes:
    """Creates a synthetic test image with stage blue LED, pulpit highlight and human skin tones."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Background (Dark sanctuary)
    img[:, :] = [25, 20, 30]

    # Stage Blue LED Wash on the left
    img[:, :100] = [30, 80, 240]

    # Warm human face simulation in the center (Skin tone)
    face_y, face_x = height // 2, width // 2
    img[face_y-30:face_y+30, face_x-25:face_x+25] = [220, 160, 130]

    # Blown spotlight / screen on top right
    img[:50, 250:] = [250, 250, 245]

    pil_img = Image.fromarray(img)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_kelvin_multipliers():
    r_warm, g_warm, b_warm = kelvin_to_rgb_multipliers(3000)
    assert r_warm > b_warm

    r_cool, g_cool, b_cool = kelvin_to_rgb_multipliers(7500)
    assert b_cool > r_cool


def test_exposure_compensation():
    arr = np.ones((50, 50, 3), dtype=np.float32) * 0.4
    boosted = apply_exposure_compensation(arr, ev=1.0)
    assert np.mean(boosted) > np.mean(arr)
    assert np.max(boosted) <= 1.0


def test_optical_corrections_led_clipping():
    # Saturated blue spot
    arr = np.zeros((50, 50, 3), dtype=np.float32)
    arr[:, :] = [0.1, 0.2, 0.95]
    repaired = restore_extreme_led_clipping(arr, strength=0.8)
    # Blue should be attenuated and red/green slightly boosted into natural highlight
    assert repaired[0, 0, 2] < arr[0, 0, 2]
    assert repaired[0, 0, 0] > arr[0, 0, 0]


def test_depth_bokeh_engine():
    arr = np.random.uniform(0.2, 0.8, (200, 300, 3)).astype(np.float32)
    # Apply f/1.8 optical bokeh at center (0.5, 0.5)
    blurred = apply_optical_bokeh_and_dof(
        arr,
        focal_x=0.5,
        focal_y=0.5,
        f_stop=1.8,
        bokeh_smoothness=0.8,
        subject_microcontrast=0.8
    )
    assert blurred.shape == arr.shape
    assert np.min(blurred) >= 0.0
    assert np.max(blurred) <= 1.0


def test_full_dslr_3stage_pipeline():
    image_bytes = create_synthetic_church_image(400, 300)
    processor = ChurchPhotoProcessor()
    params = ColorimetryParameters(
        exposure_compensation=0.25,
        temperature_kelvin=5400,
        tint=-3.0,
        contrast=1.12,
        highlights_recovery=0.55,
        shadows_lift=0.40,
        saturation=1.04,
        vibrance=1.08,
        chromatic_aberration_fix=0.50,
        vignette_correction=0.35,
        lens_distortion_correction=0.20,
        led_clipping_restoration=0.65,
        stage_led_tint_suppression=0.50,
        selective_denoise=0.30,
        skin_tone_protection_strength=0.90,
        focal_point_x=0.50,
        focal_point_y=0.50,
        f_stop_simulation=2.4,
        bokeh_smoothness=0.75,
        subject_microcontrast=0.80,
        scene_moment="Louvor / Palco",
    )

    processed_bytes, processed_b64, metadata, orig_b64 = processor.process(
        image_bytes=image_bytes,
        params=params,
        filename="test_church_dslr.jpg"
    )

    assert len(processed_bytes) > 0
    assert processed_b64.startswith("data:image/jpeg;base64,")
    assert orig_b64 is not None
    assert metadata.width == 400
    assert metadata.height == 300
    assert metadata.execution_time_ms > 0
    assert "r" in metadata.histogram
    assert len(metadata.histogram["r"]) == 64
    print("Full 3-stage DSLR processor pipeline test passed successfully!")


if __name__ == "__main__":
    test_kelvin_multipliers()
    test_exposure_compensation()
    test_optical_corrections_led_clipping()
    test_depth_bokeh_engine()
    test_full_dslr_3stage_pipeline()
    print("All 3-stage DSLR engine tests passed!")
