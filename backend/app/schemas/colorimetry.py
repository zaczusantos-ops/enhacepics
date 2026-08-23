"""
ChurchPhoto Pro - Pydantic Schemas for 3-Stage DSLR Colorimetry & Image Analysis
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PresetData(BaseModel):
    """
    Individual preset configuration recommended by Gemini or selected by user.
    """
    id: str = Field(..., description="Unique preset identifier")
    name: str = Field(..., description="Display name of the preset")
    description: str = Field(..., description="Description of the look and mood")
    icon: str = Field(default="fa-wand-magic-sparkles", description="FontAwesome icon class")
    exposure_compensation: float = Field(default=0.0, ge=-2.0, le=2.0)
    temperature_kelvin: int = Field(default=5500, ge=2500, le=9000)
    tint: float = Field(default=0.0, ge=-100.0, le=100.0)
    contrast: float = Field(default=1.08, ge=0.8, le=1.5)
    highlights_recovery: float = Field(default=0.4, ge=0.0, le=1.0)
    shadows_lift: float = Field(default=0.35, ge=0.0, le=1.0)
    saturation: float = Field(default=1.02, ge=0.5, le=1.5)
    vibrance: float = Field(default=1.05, ge=0.5, le=1.5)
    chromatic_aberration_fix: float = Field(default=0.5, ge=0.0, le=1.0)
    vignette_correction: float = Field(default=0.3, ge=0.0, le=1.0)
    led_clipping_restoration: float = Field(default=0.5, ge=0.0, le=1.0)
    selective_denoise: float = Field(default=0.3, ge=0.0, le=1.0)
    skin_tone_protection_strength: float = Field(default=0.85, ge=0.0, le=1.0)
    f_stop_simulation: float = Field(default=2.8, ge=1.4, le=8.0)
    subject_microcontrast: float = Field(default=0.7, ge=0.0, le=2.0)


class ColorimetryParameters(BaseModel):
    """
    Complete structured colorimetry & optical parameters calculated by Gemini for Church & Event Photography.
    Organized into 3 specialized professional DSLR branches.
    """
    # === VERTENTE 1: Cor, Iluminação & Estilo (Look Cinematográfico/Culto) ===
    exposure_compensation: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Compensação de exposição em stops EV (-2.0 a +2.0)."
    )
    temperature_kelvin: int = Field(
        default=5500,
        ge=2500,
        le=9000,
        description="Temperatura de cor em Kelvin (2500K a 9000K)."
    )
    tint: float = Field(
        default=0.0,
        ge=-100.0,
        le=100.0,
        description="Balanço Verde/Magenta de matiz (-100 a +100)."
    )
    contrast: float = Field(
        default=1.08,
        ge=0.8,
        le=1.5,
        description="Contraste de curva tonal S (0.8 a 1.5)."
    )
    highlights_recovery: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Recuperação de altas luzes em telões e refletores (0.0 a 1.0)."
    )
    shadows_lift: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Abertura de sombras na congregação e palco (0.0 a 1.0)."
    )
    saturation: float = Field(
        default=1.02,
        ge=0.5,
        le=1.5,
        description="Saturação geral de cor (0.5 a 1.5)."
    )
    vibrance: float = Field(
        default=1.06,
        ge=0.5,
        le=1.5,
        description="Vibração seletiva de médios tons sem super-saturar pele (0.5 a 1.5)."
    )

    # === VERTENTE 2: Correção de Falhas, Anomalias de Lente & Luz Extrema ===
    chromatic_aberration_fix: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Atenuação de aberrações cromáticas e franjas roxas/verdes em volta de luzes de palco (0.0 a 1.0)."
    )
    vignette_correction: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Compensação de vinhetagem e escurecimento de cantos de celular (0.0 a 1.0)."
    )
    lens_distortion_correction: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Correção de distorção de grande-angular de smartphones (0.0 a 1.0)."
    )
    led_clipping_restoration: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Restauração de detalhes e textura onde LEDs de palco saturaram/estouraram canais RGB (0.0 a 1.0)."
    )
    stage_led_tint_suppression: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Supressão de vazamento excessivo de LED cênico sobre peles (0.0 a 1.0)."
    )
    blue_led_attenuation: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Atenuação seletiva de canhões PAR LED Azuis/Cianos (0.0 a 1.0)."
    )
    red_magenta_attenuation: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Atenuação seletiva de canhões PAR LED Vermelhos/Magentas (0.0 a 1.0)."
    )
    selective_denoise: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Redução de ruído térmico/ISO alto preservando cabelos, olhos e tecidos (0.0 a 1.0)."
    )
    skin_tone_protection_strength: float = Field(
        default=0.88,
        ge=0.0,
        le=1.0,
        description="Proteção de melanina e tom natural de pele humana (0.0 a 1.0)."
    )

    # === VERTENTE 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh) ===
    focal_point_x: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Coordenada X normalizada do ponto de foco principal (0.0 esquerda a 1.0 direita)."
    )
    focal_point_y: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Coordenada Y normalizada do ponto de foco principal (0.0 topo a 1.0 base)."
    )
    f_stop_simulation: float = Field(
        default=2.8,
        ge=1.4,
        le=8.0,
        description="Simulação de abertura de lente f/Stop (f/1.4 = bokeh cremoso profundo, f/8.0 = plano nítido total)."
    )
    bokeh_smoothness: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Suavidade do desfoque progressivo do fundo (0.0 a 1.0)."
    )
    subject_microcontrast: float = Field(
        default=0.70,
        ge=0.0,
        le=2.0,
        description="Realce de nitidez e microcontraste concentrado exclusivamente no sujeito em foco (0.0 a 2.0)."
    )

    # === DIAGNÓSTICO & PRESETS CONTEXTUAIS ===
    scene_moment: str = Field(
        default="Louvor / Palco",
        description="Classificação do momento do culto: 'Louvor Intimista / Pouca Luz', 'Pregação / Palavra', 'Celebração / LEDs Cênicos', 'Retrato de Voluntário / Membro', 'Batismo / Cerimônia', 'Geral'."
    )
    detected_lighting_condition: str = Field(
        default="Iluminação mista de palco",
        description="Descrição técnica do ambiente de luz detectado."
    )
    detected_scene_type: str = Field(
        default="Culto / Palco",
        description="Tipo de cena fotográfica."
    )
    subject_description: str = Field(
        default="Pregador ou ministro no centro",
        description="Descrição do assunto principal focado pela IA."
    )
    analysis_summary: str = Field(
        default="Calibração DSLR: balanço de cor cinematográfico, restauração de LEDs estourados e isolamento óptico do sujeito.",
        description="Resumo fotográfico explicativo."
    )
    suggested_preset: str = Field(
        default="Luz Quente Natural",
        description="Preset principal sugerido."
    )
    alternative_presets: List[PresetData] = Field(
        default_factory=list,
        description="Lista de 3 presets contextuais alternativos calibrados para a cena específica."
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
