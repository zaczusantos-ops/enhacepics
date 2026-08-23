"""
Unit tests for deterministic ChurchPhoto image processing engine.
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
from backend.app.engine.stage_lighting import attenuate_stage_led_spill
from backend.app.engine.skin_tones import protect_and_restore_skin_tones, generate_skin_tone_mask
from backend.app.engine.denoise_sharpen import apply_bilateral_denoise, apply_adaptive_unsharp_mask


def create_synthetic_church_image(width=300, height=200) -> bytes:
    """Creates a synthetic test image with stage blue LED, pulpit highlight and human skin tones."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Background (Dark sanctuary)
    img[:, :] = [25, 20, 30]

    # Stage Blue LED Wash on the left
    img[:, :100] = [30, 80, 240]

    # Warm human face simulation in the center (Skin tone)
    # Natural skin tone RGB approx: [220, 160, 130]
    face_y, face_x = height // 2, width // 2
    cv2_face = cv2 = None
    img[face_y-30:face_y+30, face_x-25:face_x+25] = [220, 160, 130]

    # Blown spotlight / screen on top right
    img[:50, 200:] = [250, 250, 245]

    pil_img = Image.fromarray(img)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_kelvin_multipliers():
    # Warm tungsten (3000K) should boost red more than blue
    r_warm, g_warm, b_warm = kelvin_to_rgb_multipliers(3000)
    assert r_warm > b_warm

    # Cool daylight/shade (7500K) should boost blue more than red
    r_cool, g_cool, b_cool = kelvin_to_rgb_multipliers(7500)
    assert b_cool > r_cool


def test_exposure_compensation():
    arr = np.ones((50, 50, 3), dtype=np.float32) * 0.4
    boosted = apply_exposure_compensation(arr, ev=1.0)
    # +1 EV should roughly double intensity
    assert np.mean(boosted) > np.mean(arr)
    assert np.max(boosted) <= 1.0


def test_skin_tone_mask():
    # Warm skin block
    skin_patch = np.full((50, 50, 3), [215, 155, 125], dtype=np.uint8)
    mask = generate_skin_tone_mask(skin_patch)
    assert np.mean(mask) > 0.6


def test_full_processor_pipeline():
    image_bytes = create_synthetic_church_image(400, 300)
    processor = ChurchPhotoProcessor()
    params = ColorimetryParameters(
        exposure_compensation=0.3,
        temperature_kelvin=5400,
        tint=-5.0,
        contrast=1.1,
        highlights_recovery=0.5,
        shadows_lift=0.4,
        saturation=1.05,
        stage_led_tint_suppression=0.6,
        blue_led_attenuation=0.5,
        red_magenta_attenuation=0.4,
        skin_tone_protection_strength=0.85,
        denoise_strength=0.3,
        unsharp_mask_amount=0.7,
        unsharp_mask_radius=1.2,
    )

    processed_bytes, processed_b64, metadata, orig_b64 = processor.process(
        image_bytes=image_bytes,
        params=params,
        filename="test_church_event.jpg"
    )

    assert len(processed_bytes) > 0
    assert processed_b64.startswith("data:image/jpeg;base64,")
    assert orig_b64 is not None
    assert metadata.width == 400
    assert metadata.height == 300
    assert metadata.execution_time_ms > 0
    assert "r" in metadata.histogram
    assert len(metadata.histogram["r"]) == 64
    print("Processor test passed successfully!")


if __name__ == "__main__":
    test_kelvin_multipliers()
    test_exposure_compensation()
    test_skin_tone_mask()
    test_full_processor_pipeline()
    print("All deterministic engine tests passed!")
