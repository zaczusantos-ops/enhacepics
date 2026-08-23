"""
ChurchPhoto Pro - Vertente 2: Correção de Falhas, Anomalias de Lente & Luz Extrema
Implements:
1. Chromatic aberration fringe suppression (purple/green edges)
2. Extreme stage LED clipping & highlight desaturation/restoration
3. Smartphone lens vignetting & distortion compensation
4. Edge-preserving selective high-ISO denoising
"""

import cv2
import numpy as np


def correct_chromatic_aberration(
    img_rgb: np.ndarray,
    strength: float = 0.5
) -> np.ndarray:
    """
    Suppresses purple and green chromatic aberration fringing that occurs around
    harsh stage lights and backlight edges on smartphone lenses.
    
    Args:
        img_rgb: Float32 image [0..1], shape (H, W, 3) in RGB order.
        strength: Strength from 0.0 (off) to 1.0 (maximum desaturation of fringes).
    """
    if strength <= 0.02:
        return img_rgb

    # Work in HSV color space
    img_uint8 = np.clip(img_rgb * 255.0, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # Find edges in luminance (where chromatic aberration primarily shows up)
    gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 160)
    # Dilate edges slightly to cover fringing halo
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edge_mask = cv2.dilate(edges, kernel, iterations=1) > 0

    # Purple/Magenta hue range in OpenCV (135 to 175 in 0..180 scale)
    purple_mask = (h >= 130) & (h <= 175) & (s > 45) & edge_mask
    
    # Green/Cyan fringe hue range in OpenCV (35 to 85)
    green_mask = (h >= 35) & (h <= 85) & (s > 45) & (v > 120) & edge_mask

    fringe_mask = purple_mask | green_mask

    if np.any(fringe_mask):
        # Desaturate the chromatic aberration fringe areas
        desat_factor = 1.0 - (0.85 * strength)
        s_float = s.astype(np.float32)
        s_float[fringe_mask] *= desat_factor
        hsv[:, :, 1] = np.clip(s_float, 0, 255).astype(np.uint8)
        
        corrected = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return corrected.astype(np.float32) / 255.0

    return img_rgb


def restore_extreme_led_clipping(
    img_rgb: np.ndarray,
    strength: float = 0.6
) -> np.ndarray:
    """
    Detects severe sensor clipping where saturated red, blue, or magenta stage LEDs
    blow out details, and reconstructs texture and smooth luminance falloff.
    
    Args:
        img_rgb: Float32 image [0..1], shape (H, W, 3).
        strength: Factor from 0.0 to 1.0.
    """
    if strength <= 0.02:
        return img_rgb

    r = img_rgb[:, :, 0]
    g = img_rgb[:, :, 1]
    b = img_rgb[:, :, 2]
    out = img_rgb.copy()

    # 1. Extreme Blue LED Clipping (B saturated near 1.0 while R/G are low or clipped)
    blue_clip = (b > 0.82) & (b > r * 1.35)
    if np.any(blue_clip):
        excess_blue = np.maximum(0.0, b - np.maximum(r * 1.25, g * 1.25))
        # Rebalance blue highlight into realistic specular glow
        desat_weight = np.clip(excess_blue * strength * 0.75, 0.0, 0.45)
        out[:, :, 0] += desat_weight * 0.35  # Lift red slightly into neutral white highlight
        out[:, :, 1] += desat_weight * 0.35  # Lift green slightly
        out[:, :, 2] -= desat_weight * 0.40  # Soften blue ceiling

    # 2. Extreme Red/Magenta LED Clipping
    red_clip = (r > 0.85) & (r > g * 1.5)
    if np.any(red_clip):
        excess_red = np.maximum(0.0, r - g * 1.35)
        desat_red = np.clip(excess_red * strength * 0.65, 0.0, 0.40)
        out[:, :, 1] += desat_red * 0.30  # Add green to convert harsh neon red into warm highlight
        out[:, :, 0] -= desat_red * 0.35

    return np.clip(out, 0.0, 1.0)


def correct_lens_vignetting_and_distortion(
    img_rgb: np.ndarray,
    vignette_strength: float = 0.35,
    distortion_strength: float = 0.20
) -> np.ndarray:
    """
    Compensates for dark corners (vignetting) and wide-angle barrel distortion typical of smartphone lenses.
    """
    h, w, _ = img_rgb.shape
    out = img_rgb.copy()

    # 1. Vignette Correction: Radial luminance boost towards edges
    if vignette_strength > 0.02:
        y, x = np.ogrid[:h, :w]
        center_x, center_y = w / 2.0, h / 2.0
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        norm_dist = dist_from_center / max_dist  # 0.0 at center, 1.0 at corner
        
        # Vignette compensation curve
        gain = 1.0 + (norm_dist**2) * (vignette_strength * 0.45)
        out = np.clip(out * gain[:, :, np.newaxis], 0.0, 1.0)

    # 2. Barrel Distortion Correction (subtle barrel unwrapping)
    if distortion_strength > 0.05:
        # Camera matrix approximation
        fx = fy = max(w, h)
        cx, cy = w / 2.0, h / 2.0
        camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
        # Negative k1 undoes barrel distortion
        k1 = -0.08 * distortion_strength
        dist_coeffs = np.array([k1, 0, 0, 0], dtype=np.float32)
        
        img_uint8 = (out * 255.0).astype(np.uint8)
        undistorted = cv2.undistort(img_uint8, camera_matrix, dist_coeffs)
        out = undistorted.astype(np.float32) / 255.0

    return out


def apply_selective_denoise(
    img_rgb: np.ndarray,
    strength: float = 0.30
) -> np.ndarray:
    """
    Edge-preserving bilateral denoising to eliminate thermal and high-ISO noise
    without turning human skin or clothing into plastic wax.
    """
    if strength <= 0.02:
        return img_rgb

    img_uint8 = np.clip(img_rgb * 255.0, 0, 255).astype(np.uint8)
    
    # Bilateral filter parameters scaled with strength
    d = int(np.clip(5 + strength * 4, 3, 9))
    sigma_color = float(np.clip(18.0 + strength * 35.0, 15.0, 60.0))
    sigma_space = float(np.clip(12.0 + strength * 25.0, 10.0, 45.0))

    denoised = cv2.bilateralFilter(img_uint8, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)
    return denoised.astype(np.float32) / 255.0
