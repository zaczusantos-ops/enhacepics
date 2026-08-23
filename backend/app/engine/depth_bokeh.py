"""
ChurchPhoto Pro - Vertente 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh)
Implements:
1. Focal point tracking (normalized x, y)
2. Synthetic distance & subject segmentation map
3. Progressive optical bokeh / DoF blur based on f/Stop (f/1.4 to f/8.0)
4. Localized microcontrast & unsharp masking strictly on in-focus subjects
"""

import cv2
import numpy as np


def generate_depth_and_subject_mask(
    img_rgb: np.ndarray,
    focal_x: float = 0.50,
    focal_y: float = 0.40
) -> np.ndarray:
    """
    Generates a normalized depth gradient and subject isolation mask [0..1]
    where 1.0 represents the subject at the focal plane (in-focus) and 0.0 is the background (out-of-focus).
    
    Args:
        img_rgb: Float32 image [0..1], shape (H, W, 3).
        focal_x: Normalized X coordinate (0.0 to 1.0).
        focal_y: Normalized Y coordinate (0.0 to 1.0).
        
    Returns:
        mask: Float32 array (H, W), with 1.0 = sharp focus, 0.0 = maximum background distance.
    """
    h, w, _ = img_rgb.shape
    f_px_x = int(np.clip(focal_x * w, 0, w - 1))
    f_px_y = int(np.clip(focal_y * h, 0, h - 1))

    # 1. Base Elliptical Distance Field from Focal Point (typical human portrait perspective)
    y, x = np.ogrid[:h, :w]
    # Human portraits tend to have more vertical tolerance than horizontal
    rx = w * 0.28
    ry = h * 0.35
    dist = np.sqrt(((x - f_px_x) / rx)**2 + ((y - f_px_y) / ry)**2)
    # Distance field: 1.0 at center of focus, decays smoothly outward
    geo_mask = np.clip(1.0 - (dist * 0.7), 0.0, 1.0)
    geo_mask = geo_mask ** 1.8  # Smooth falloff

    # 2. Refine with Edge & Skin Luminance Features
    img_uint8 = np.clip(img_rgb * 255.0, 0, 255).astype(np.uint8)
    gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY)
    
    # Segment potential subject using GrabCut-inspired color clustering around focal point
    # Sample color distribution around focal point
    pad_w = max(5, int(w * 0.04))
    pad_h = max(5, int(h * 0.04))
    roi = img_rgb[
        max(0, f_px_y - pad_h):min(h, f_px_y + pad_h),
        max(0, f_px_x - pad_w):min(w, f_px_x + pad_w)
    ]
    mean_subject_color = np.mean(roi, axis=(0, 1)) if roi.size > 0 else np.array([0.5, 0.5, 0.5])
    
    # Color similarity map
    color_diff = np.sqrt(np.sum((img_rgb - mean_subject_color)**2, axis=2))
    color_similarity = np.clip(1.0 - (color_diff / 0.65), 0.0, 1.0)

    # 3. Fuse geometric falloff with color segmentation
    fused_mask = (geo_mask * 0.70) + (color_similarity * geo_mask * 0.30)
    
    # Smooth the mask using bilateral/guided blur to align with subject contours
    fused_uint8 = (np.clip(fused_mask, 0.0, 1.0) * 255.0).astype(np.uint8)
    refined_mask = cv2.GaussianBlur(fused_uint8, (21, 21), 0)
    
    return refined_mask.astype(np.float32) / 255.0


def apply_optical_bokeh_and_dof(
    img_rgb: np.ndarray,
    focal_x: float = 0.50,
    focal_y: float = 0.40,
    f_stop: float = 2.8,
    bokeh_smoothness: float = 0.75,
    subject_microcontrast: float = 0.70
) -> np.ndarray:
    """
    Applies simulated optical Depth of Field (DoF) and bokeh to emulate dedicated Full-Frame DSLR prime lenses.
    
    Args:
        img_rgb: Float32 image [0..1], shape (H, W, 3).
        focal_x: Focus point X [0..1].
        focal_y: Focus point Y [0..1].
        f_stop: Aperture simulation (f/1.4 = creamy bokeh, f/2.8 = portrait, f/8.0 = all sharp).
        bokeh_smoothness: Smoothness quality factor (0.0 to 1.0).
        subject_microcontrast: Unsharp sharpening on the in-focus subject.
    """
    h, w, _ = img_rgb.shape
    
    # If f_stop >= 7.5, depth of field is infinite (everything sharp, no bokeh needed)
    if f_stop >= 7.5:
        # Only apply localized microcontrast
        if subject_microcontrast > 0.05:
            return apply_subject_microcontrast(img_rgb, focal_x, focal_y, subject_microcontrast)
        return img_rgb

    # 1. Calculate blur radius from f/Stop (e.g. f/1.4 -> large blur, f/5.6 -> small blur)
    # In optics: blur diameter is inversely proportional to f-number
    max_ksize = int(np.clip((8.0 / max(1.4, f_stop)) * (w / 120.0) * bokeh_smoothness, 3, 31))
    if max_ksize % 2 == 0:
        max_ksize += 1

    # 2. Generate Depth Map (1.0 = sharp focus, 0.0 = far background)
    focus_mask = generate_depth_and_subject_mask(img_rgb, focal_x, focal_y)
    focus_mask_3d = focus_mask[:, :, np.newaxis]

    # 3. Create Multi-layer progressive Bokeh Blur
    # Layer 1: Medium blur (mid-ground)
    k_mid = max(3, (max_ksize // 2) | 1)
    img_mid_blur = cv2.GaussianBlur(img_rgb, (k_mid, k_mid), 0)
    
    # Layer 2: Deep optical bokeh blur (far background)
    img_deep_blur = cv2.GaussianBlur(img_rgb, (max_ksize, max_ksize), 0)

    # Blend progressive layers based on distance
    background_bokeh = (img_mid_blur * 0.4) + (img_deep_blur * 0.6)

    # 4. Composite in-focus foreground with out-of-focus background
    # foreground * focus_mask + background * (1 - focus_mask)
    dof_composite = (img_rgb * focus_mask_3d) + (background_bokeh * (1.0 - focus_mask_3d))

    # 5. Apply localized microcontrast only to in-focus foreground
    if subject_microcontrast > 0.05:
        dof_composite = apply_subject_microcontrast(
            dof_composite,
            focal_x=focal_x,
            focal_y=focal_y,
            amount=subject_microcontrast,
            mask=focus_mask
        )

    return np.clip(dof_composite, 0.0, 1.0)


def apply_subject_microcontrast(
    img_rgb: np.ndarray,
    focal_x: float = 0.50,
    focal_y: float = 0.40,
    amount: float = 0.70,
    mask: np.ndarray = None
) -> np.ndarray:
    """
    Applies high-frequency microcontrast and texture sharpening strictly to the in-focus subject.
    """
    if amount <= 0.02:
        return img_rgb

    if mask is None:
        mask = generate_depth_and_subject_mask(img_rgb, focal_x, focal_y)
        
    mask_3d = mask[:, :, np.newaxis]

    # Unsharp Masking
    gaussian = cv2.GaussianBlur(img_rgb, (0, 0), sigmaX=1.2)
    unsharp = cv2.addWeighted(img_rgb, 1.0 + amount * 0.85, gaussian, -(amount * 0.85), 0)

    # Blend exclusively onto masked subject
    sharpened_subject = (unsharp * mask_3d) + (img_rgb * (1.0 - mask_3d))
    return np.clip(sharpened_subject, 0.0, 1.0)
