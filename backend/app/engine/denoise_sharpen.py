"""
ChurchPhoto Pro - High-ISO Noise Reduction & Adaptive Unsharp Masking
Reduces sensor noise from low-light church environments and enhances crispness
without creating facial plastic artifacts or noise haloing.
"""

import numpy as np
import cv2


def apply_bilateral_denoise(
    img_rgb: np.ndarray,
    denoise_strength: float = 0.25
) -> np.ndarray:
    """
    Applies edge-preserving bilateral filtering to reduce High-ISO luminance and chrominance noise.
    """
    if denoise_strength <= 0.01:
        return img_rgb

    img_uint8 = (img_rgb * 255.0).astype(np.uint8)

    # Convert to Lab to denoise chroma channels (A and B) more aggressively than Luminance (L)
    lab = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    # Scale filter parameters with denoise_strength
    d = int(np.clip(5 + denoise_strength * 6, 3, 11))
    sigma_color_l = float(np.clip(denoise_strength * 30.0, 5.0, 45.0))
    sigma_space_l = float(np.clip(denoise_strength * 30.0, 5.0, 45.0))

    # Luminance: edge-preserving bilateral filter
    l_filtered = cv2.bilateralFilter(l, d=d, sigmaColor=sigma_color_l, sigmaSpace=sigma_space_l)

    # Chroma channels: slightly stronger smoothing to eliminate purple/green chroma noise
    sigma_chroma = float(np.clip(denoise_strength * 50.0, 10.0, 65.0))
    a_filtered = cv2.bilateralFilter(a, d=d, sigmaColor=sigma_chroma, sigmaSpace=sigma_space_l)
    b_filtered = cv2.bilateralFilter(b, d=d, sigmaColor=sigma_chroma, sigmaSpace=sigma_space_l)

    merged_lab = cv2.merge([l_filtered, a_filtered, b_filtered])
    denoised_rgb = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2RGB)

    return denoised_rgb.astype(np.float32) / 255.0


def apply_adaptive_unsharp_mask(
    img_rgb: np.ndarray,
    amount: float = 0.6,
    radius: float = 1.2,
    threshold: float = 0.02
) -> np.ndarray:
    """
    Applies an adaptive unsharp mask that sharpens edges (eyes, hair, clothes, instruments)
    while ignoring flat background areas to prevent noise amplification.
    """
    if amount <= 0.01:
        return img_rgb

    # Gaussian blur
    # Calculate kernel size based on radius
    ksize = int(2 * np.ceil(2 * radius) + 1)
    if ksize % 2 == 0:
        ksize += 1

    blurred = cv2.GaussianBlur(img_rgb, (ksize, ksize), radius)

    # Calculate high-frequency detail difference
    diff = img_rgb - blurred

    # Create edge threshold mask (only sharpen where details exceed noise threshold)
    diff_magnitude = np.abs(diff)
    edge_mask = np.where(diff_magnitude > threshold, 1.0, (diff_magnitude / (threshold + 1e-6)) ** 2)

    # Apply weighted sharpening
    sharpened = img_rgb + (diff * amount * edge_mask)

    return np.clip(sharpened, 0.0, 1.0)
