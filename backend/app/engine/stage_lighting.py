"""
ChurchPhoto Pro - Stage Lighting & LED Spill Mitigation
Detects and attenuates aggressive PAR LED lights (Blue/Cyan, Magenta/Purple, Hyper-Red)
common in church stages and worship events.
"""

import numpy as np
import cv2


def attenuate_stage_led_spill(
    img_rgb: np.ndarray,
    stage_led_suppression: float = 0.4,
    blue_attenuation: float = 0.3,
    red_magenta_attenuation: float = 0.3
) -> np.ndarray:
    """
    Selectively attenuates oversaturated stage LED spill in HSV and Lab color spaces.
    Targets:
    - High-saturation Blue/Cyan PAR LEDs (Hue ~180°-260° in standard 360° scale)
    - High-saturation Magenta/Purple wash (Hue ~280°-340°)
    - Unnatural clipped red stage wash (Hue ~345°-360° / 0°-10° with extreme saturation)
    """
    if stage_led_suppression <= 0.01 and blue_attenuation <= 0.01 and red_magenta_attenuation <= 0.01:
        return img_rgb

    img_uint8 = (img_rgb * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)

    # OpenCV Hue is 0..179 (representing 0..360 deg)
    h = hsv[:, :, 0]  # 0..179
    s = hsv[:, :, 1] / 255.0  # 0..1
    v = hsv[:, :, 2] / 255.0  # 0..1

    # Blue LED range: OpenCV Hue ~90..135 (180°..270°) with high saturation (S > 0.45)
    blue_mask = (h >= 90) & (h <= 135) & (s > 0.45)
    # Magenta/Purple range: OpenCV Hue ~140..170 (280°..340°) with high saturation (S > 0.45)
    magenta_mask = (h >= 140) & (h <= 170) & (s > 0.45)
    # Extreme red wash (excluding warm skin tones which usually have lower saturation or higher brightness)
    red_wash_mask = ((h <= 8) | (h >= 172)) & (s > 0.85) & (v > 0.70)

    # Apply selective desaturation and luminance balancing
    total_blue_factor = np.clip(blue_attenuation * 0.7 + stage_led_suppression * 0.3, 0.0, 0.85)
    total_mag_factor = np.clip(red_magenta_attenuation * 0.7 + stage_led_suppression * 0.3, 0.0, 0.85)
    total_red_factor = np.clip(red_magenta_attenuation * 0.5 + stage_led_suppression * 0.2, 0.0, 0.75)

    # Soft transition masks using Gaussian blur to avoid hard boundary artifacts
    blue_weight = cv2.GaussianBlur(blue_mask.astype(np.float32), (15, 15), 0)
    mag_weight = cv2.GaussianBlur(magenta_mask.astype(np.float32), (15, 15), 0)
    red_weight = cv2.GaussianBlur(red_wash_mask.astype(np.float32), (15, 15), 0)

    # Reduce oversaturated color spill
    s = s * (1.0 - blue_weight * total_blue_factor * 0.65)
    s = s * (1.0 - mag_weight * total_mag_factor * 0.65)
    s = s * (1.0 - red_weight * total_red_factor * 0.50)

    # Balance extreme brightness peaks in LED hot-spots
    v = v * (1.0 - blue_weight * total_blue_factor * 0.15)
    v = v * (1.0 - mag_weight * total_mag_factor * 0.15)

    hsv[:, :, 1] = np.clip(s * 255.0, 0.0, 255.0)
    hsv[:, :, 2] = np.clip(v * 255.0, 0.0, 255.0)

    result_uint8 = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return result_uint8.astype(np.float32) / 255.0
