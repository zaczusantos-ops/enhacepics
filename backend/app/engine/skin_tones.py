"""
ChurchPhoto Pro - Human Skin Tone Protection & Natural Melanin Preservation
Detects human skin regions in HSV and YCbCr color spaces and preserves/restores natural skin tones
without applying generative face distortion.
"""

import numpy as np
import cv2


def generate_skin_tone_mask(img_rgb_uint8: np.ndarray) -> np.ndarray:
    """
    Generates a soft probability mask [0..1] for human skin tones across diverse ethnicities
    combining HSV and YCbCr color metrics.
    """
    # 1. HSV Skin Detection
    hsv = cv2.cvtColor(img_rgb_uint8, cv2.COLOR_RGB2HSV)
    h = hsv[:, :, 0]  # 0..179
    s = hsv[:, :, 1]  # 0..255
    v = hsv[:, :, 2]  # 0..255

    # Human skin hues are typically 0° to 35° (OpenCV Hue 0..18) and 345° to 360° (OpenCV Hue 172..179)
    hsv_mask = (
        ((h <= 18) | (h >= 172)) &
        (s >= 35) & (s <= 180) &
        (v >= 45) & (v <= 245)
    )

    # 2. YCbCr Skin Detection (Standard human chrominance cluster)
    ycbcr = cv2.cvtColor(img_rgb_uint8, cv2.COLOR_RGB2YCrCb)
    # OpenCV YCrCb order is Y, Cr, Cb
    cr = ycbcr[:, :, 1]
    cb = ycbcr[:, :, 2]

    ycbcr_mask = (
        (cr >= 133) & (cr <= 173) &
        (cb >= 77) & (cb <= 127)
    )

    # Combined skin mask
    combined = (hsv_mask | ycbcr_mask).astype(np.float32)

    # Smooth the mask to create seamless, natural transitions
    blurred_mask = cv2.GaussianBlur(combined, (21, 21), 0)
    return np.clip(blurred_mask, 0.0, 1.0)


def protect_and_restore_skin_tones(
    processed_rgb: np.ndarray,
    original_rgb: np.ndarray,
    protection_strength: float = 0.85
) -> np.ndarray:
    """
    Blends and restores natural skin warmth onto the processed image.
    Ensures faces don't lose natural melanin or inherit stage light discoloration.
    """
    if protection_strength <= 0.01:
        return processed_rgb

    orig_uint8 = (original_rgb * 255.0).astype(np.uint8)
    proc_uint8 = (processed_rgb * 255.0).astype(np.uint8)

    # Compute skin probability mask
    skin_mask = generate_skin_tone_mask(orig_uint8)
    
    # If no significant skin detected, return processed
    if np.mean(skin_mask) < 0.001:
        return processed_rgb

    # 3D expand mask for RGB channels
    mask_3d = np.repeat(skin_mask[:, :, np.newaxis], 3, axis=2)
    effective_mask = mask_3d * protection_strength

    # Work with skin tone in Lab color space to correct color cast
    skin_lab = cv2.cvtColor(proc_uint8, cv2.COLOR_RGB2LAB).astype(np.float32)
    
    # a* channel is Green (-) to Red (+)
    # b* channel is Blue (-) to Yellow (+)
    # Healthy human skin naturally has positive a* and positive b* (warm peach/golden)
    a_chan = skin_lab[:, :, 1]
    b_chan = skin_lab[:, :, 2]

    # Neutralize bluish/cyan contamination in skin regions (boost b* towards warm yellow, balance a*)
    skin_lab[:, :, 1] = np.where(skin_mask > 0.3, np.clip(a_chan + 4.0 * protection_strength, 130, 175), a_chan)
    skin_lab[:, :, 2] = np.where(skin_mask > 0.3, np.clip(b_chan + 6.0 * protection_strength, 135, 185), b_chan)

    warmed_skin_rgb = cv2.cvtColor(skin_lab.astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

    # Final blend with soft mask
    blended = processed_rgb * (1.0 - effective_mask * 0.75) + warmed_skin_rgb * (effective_mask * 0.75)
    return np.clip(blended, 0.0, 1.0)
