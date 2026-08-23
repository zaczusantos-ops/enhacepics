"""
ChurchPhoto Pro - Color Curves & White Balance Mathematics
Deterministic algorithms for Exposure, Kelvin Color Temperature, Tint, Highlights, Shadows and S-Curves.
"""

import numpy as np
import cv2


def kelvin_to_rgb_multipliers(kelvin: int) -> tuple[float, float, float]:
    """
    Computes RGB multipliers to shift an image towards the target Kelvin temperature.
    Based on Tanner Helland's Planckian radiator approximation calibrated for 5500K daylight baseline.
    """
    temp = np.clip(kelvin, 2500, 9000) / 100.0

    # Calculate Red
    if temp <= 66:
        r = 255.0
    else:
        r = temp - 60
        r = 329.698727446 * (r ** -0.1332047592)
        r = np.clip(r, 0, 255.0)

    # Calculate Green
    if temp <= 66:
        g = temp
        g = 99.4708025861 * np.log(g) - 161.1195681661
    else:
        g = temp - 60
        g = 288.1221695283 * (g ** -0.0755148492)
    g = np.clip(g, 0, 255.0)

    # Calculate Blue
    if temp >= 66:
        b = 255.0
    elif temp <= 19:
        b = 0.0
    else:
        b = temp - 10
        b = 138.5177312231 * np.log(b) - 305.0447927307
        b = np.clip(b, 0, 255.0)

    # Normalize to 5500K neutral reference (R=255, G=243, B=232)
    ref_r, ref_g, ref_b = 255.0, 243.6, 232.4
    
    scale_r = (r / ref_r)
    scale_g = (g / ref_g)
    scale_b = (b / ref_b)

    # Soften the multiplier response to prevent extreme unnatural shifts on 8-bit images
    strength = 0.55
    final_r = 1.0 + (scale_r - 1.0) * strength
    final_g = 1.0 + (scale_g - 1.0) * strength
    final_b = 1.0 + (scale_b - 1.0) * strength

    return float(final_r), float(final_g), float(final_b)


def apply_white_balance_and_tint(
    img_rgb: np.ndarray,
    kelvin: int = 5500,
    tint: float = 0.0
) -> np.ndarray:
    """
    Applies color temperature (Kelvin) and Green/Magenta tint balance to float32 [0..1] RGB image.
    """
    mult_r, mult_g, mult_b = kelvin_to_rgb_multipliers(kelvin)

    # Tint adjustment (-100 = more green, +100 = more magenta/red+blue)
    # Scaled safely between [-0.15, +0.15]
    tint_factor = tint / 100.0 * 0.12
    mult_g *= (1.0 - tint_factor)
    mult_r *= (1.0 + tint_factor * 0.5)
    mult_b *= (1.0 + tint_factor * 0.5)

    # Apply channel multipliers
    result = img_rgb.copy()
    result[:, :, 0] *= mult_r
    result[:, :, 1] *= mult_g
    result[:, :, 2] *= mult_b

    return np.clip(result, 0.0, 1.0)


def apply_exposure_compensation(
    img_rgb: np.ndarray,
    ev: float = 0.0
) -> np.ndarray:
    """
    Applies photographic exposure compensation in EV stops with a soft knee highlight rolloff
    to avoid harsh digital clipping.
    """
    if abs(ev) < 0.01:
        return img_rgb

    multiplier = 2.0 ** ev
    scaled = img_rgb * multiplier

    # Reinhard / Film-style soft knee highlight compression for overexposed regions
    if ev > 0:
        # Blend with soft-clip highlight rolloff
        threshold = 0.75
        mask = scaled > threshold
        scaled[mask] = threshold + (1.0 - threshold) * np.tanh((scaled[mask] - threshold) / (1.0 - threshold + 1e-5))

    return np.clip(scaled, 0.0, 1.0)


def apply_highlights_and_shadows(
    img_rgb: np.ndarray,
    highlights_recovery: float = 0.0,
    shadows_lift: float = 0.0
) -> np.ndarray:
    """
    Recovers blown stage highlights (screens, spotlights) and lifts deep church shadows
    using smooth luminance spline weighting.
    """
    if highlights_recovery == 0.0 and shadows_lift == 0.0:
        return img_rgb

    # Work in Lab color space to preserve color purity while modifying Luminance
    img_uint8 = (img_rgb * 255.0).astype(np.uint8)
    lab = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2LAB).astype(np.float32)
    l_chan = lab[:, :, 0] / 255.0  # Normalized [0..1]

    # Highlights recovery: Compress values in range [0.5..1.0]
    if highlights_recovery > 0:
        # Smooth weight curve for highlights
        h_weight = np.clip((l_chan - 0.45) / 0.55, 0.0, 1.0) ** 1.8
        # Compress highlights down
        h_compression = highlights_recovery * 0.25
        l_chan = l_chan - (h_weight * h_compression * l_chan)

    # Shadows lift: Lift values in range [0.0..0.5] preserving true black (0.0)
    if shadows_lift > 0:
        # Smooth bell weight for shadows with maximum around 0.15-0.25
        s_weight = (1.0 - np.clip(l_chan / 0.65, 0.0, 1.0)) ** 1.5
        s_boost = shadows_lift * 0.35
        # Quadratic lift preserving 0
        l_chan = l_chan + (s_weight * s_boost * (1.0 - l_chan) * l_chan * 2.5)

    lab[:, :, 0] = np.clip(l_chan * 255.0, 0.0, 255.0)
    result_uint8 = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB)
    return result_uint8.astype(np.float32) / 255.0


def apply_s_curve_contrast(
    img_rgb: np.ndarray,
    contrast: float = 1.0
) -> np.ndarray:
    """
    Applies a photographic S-curve contrast adjustment anchored at 50% gray.
    contrast = 1.0 is neutral. 1.2 is punchy professional contrast. 0.85 is soft portrait.
    """
    if abs(contrast - 1.0) < 0.01:
        return img_rgb

    # Sigmoidal S-Curve
    # f(x) = (x^contrast) / (x^contrast + (1 - x)^contrast)
    eps = 1e-6
    x = np.clip(img_rgb, eps, 1.0 - eps)
    gamma = contrast
    
    s_curved = (x ** gamma) / ((x ** gamma) + ((1.0 - x) ** gamma))
    return np.clip(s_curved, 0.0, 1.0)


def apply_saturation(
    img_rgb: np.ndarray,
    saturation: float = 1.0,
    vibrance: float = 1.0
) -> np.ndarray:
    """
    Adjusts color saturation and vibrance in HSV space with protection for skin tones and already-saturated pixels.
    """
    if abs(saturation - 1.0) < 0.01 and abs(vibrance - 1.0) < 0.01:
        return img_rgb

    img_uint8 = (img_rgb * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)

    # Scale saturation channel
    s = hsv[:, :, 1] / 255.0
    
    # 1. Base Saturation
    s = s * saturation

    # 2. Vibrance: boost muted/dull colors more than already saturated colors
    if abs(vibrance - 1.0) > 0.01:
        v_factor = (vibrance - 1.0) * (1.0 - (s ** 1.2) * 0.7)
        s = np.clip(s * (1.0 + v_factor), 0.0, 1.0)

    hsv[:, :, 1] = np.clip(s * 255.0, 0.0, 255.0)
    result_uint8 = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return result_uint8.astype(np.float32) / 255.0
