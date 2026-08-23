"""
ChurchPhoto Pro - Pydantic Schemas for Colorimetry & Image Analysis
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ColorimetryParameters(BaseModel):
    """
    Structured colorimetry parameters calculated by Gemini for Church & Event Photography.
    All values are strictly bounded and deterministic.
    """
    exposure_compensation: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Exposure compensation in EV stops (-2.0 = underexpose by 2 stops, +2.0 = overexpose by 2 stops)."
    )
    temperature_kelvin: int = Field(
        default=5500,
        ge=2500,
        le=9000,
        description="Target color temperature in Kelvin (2500K = warm/tungsten, 5500K = daylight, 9000K = cool/shade)."
    )
    tint: float = Field(
        default=0.0,
        ge=-100.0,
        le=100.0,
        description="Green/Magenta tint balance (-100 = strong green compensation, +100 = strong magenta compensation)."
    )
    contrast: float = Field(
        default=1.0,
        ge=0.8,
        le=1.5,
        description="Tonal contrast curve multiplier (0.8 = soft/flat, 1.0 = neutral, 1.5 = high contrast S-curve)."
    )
    highlights_recovery: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Highlights recovery strength (0.0 = none, 1.0 = maximum recovery of blown stage spots and screens)."
    )
    shadows_lift: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Shadows lift factor (0.0 = dark church environment, 1.0 = maximum fill light on faces and congregation)."
    )
    saturation: float = Field(
        default=1.0,
        ge=0.7,
        le=1.3,
        description="Overall color saturation multiplier (0.7 = desaturated/muted, 1.0 = natural, 1.3 = vibrant)."
    )
    stage_led_tint_suppression: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Aggressiveness of stage LED spill reduction on skin and subjects (0.0 = no filter, 1.0 = maximum suppression)."
    )
    blue_led_attenuation: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Selective attenuation for aggressive stage blue/cyan PAR LEDs (0.0 = disabled, 1.0 = high attenuation)."
    )
    red_magenta_attenuation: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Selective attenuation for aggressive stage red/magenta/purple wash (0.0 = disabled, 1.0 = high attenuation)."
    )
    skin_tone_protection_strength: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Strength of skin melanin preservation mask (0.0 = no protection, 1.0 = strict natural skin tone priority)."
    )
    denoise_strength: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="High-ISO noise reduction strength (0.0 = no denoise, 1.0 = maximum smoothing of sensor noise)."
    )
    unsharp_mask_amount: float = Field(
        default=0.6,
        ge=0.0,
        le=2.0,
        description="Adaptive unsharp masking amount for crisp facial features and fabric textures (0.0 = off, 2.0 = strong)."
    )
    unsharp_mask_radius: float = Field(
        default=1.2,
        ge=0.5,
        le=3.0,
        description="Radius in pixels for unsharp mask filter."
    )
    detected_lighting_condition: str = Field(
        default="Iluminação mista de palco",
        description="Brief description of the detected church lighting environment (e.g. 'Forte luz de LED azul com contraluz', 'Luz quente de púlpito com sombras duras')."
    )
    detected_scene_type: str = Field(
        default="Culto / Palco",
        description="Scene type detected: 'Púlpito / Pregador', 'Louvor / Ministério de Música', 'Congregação / Público', 'Batismo / Cerimônia', 'Geral'."
    )
    analysis_summary: str = Field(
        default="Ajuste colorimétrico para correção de luz cênica e realce de tons de pele.",
        description="Photographic explanation of the adjustments made for the media team."
    )
    suggested_preset: str = Field(
        default="Culto Contemporâneo",
        description="Matching church preset: 'Culto Contemporâneo', 'Culto Tradicional', 'Louvor & Adoração', 'Iluminação Intimista', 'Evento Externo'."
    )


class AnalysisResponse(BaseModel):
    success: bool
    parameters: ColorimetryParameters
    model_used: str
    processing_time_ms: float


class ProcessImageRequest(BaseModel):
    parameters: Optional[ColorimetryParameters] = None
    output_format: str = "JPEG"
    output_quality: int = 92


class ProcessedImageMetadata(BaseModel):
    width: int
    height: int
    original_format: str
    output_format: str
    execution_time_ms: float
    parameters_applied: ColorimetryParameters
    histogram: Optional[Dict[str, List[int]]] = None


class FullPipelineResponse(BaseModel):
    success: bool
    image_base64: str
    original_base64: Optional[str] = None
    metadata: ProcessedImageMetadata
    analysis: ColorimetryParameters
