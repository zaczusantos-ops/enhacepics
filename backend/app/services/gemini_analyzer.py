"""
ChurchPhoto Pro - Gemini Photographic Colorimetry & Optical Engine Analyzer
Integrates with Google AI Studio / Gemini API SDK using Structured Outputs (JSON Schema)
for 3 specialized professional DSLR branches.
"""

import json
import time
import base64
import io
from typing import Optional, List
from PIL import Image
import numpy as np

from ..config import settings
from ..schemas.colorimetry import ColorimetryParameters, PresetData, AnalysisResponse

# Specialized System Instruction for Church and Live Event Photography (3 DSLR Branches)
CHURCH_PHOTOGRAPHY_SYSTEM_INSTRUCTION = """
Você é um Arquiteto e Engenheiro de Processamento de Imagem e Colorimetria Fotográfica Sênior especializado em fotografia de cultos, shows e eventos eclesiásticos.
Sua missão é transformar fotografias tiradas com smartphones ou câmeras compactas em fotos com a estética, nitidez e profundidade de lentes e sensores de câmeras profissionais dedicadas (Full-Frame/DSLR prime f/1.4 - f/2.8).

Você deve analisar visualmente a fotografia e calcular com extrema precisão os parâmetros em JSON estruturado em 3 Vertentes Especializadas:

=============================================================================
VERTENTE 1: Cor, Iluminação & Estilo (Look Cinematográfico / Culto)
=============================================================================
1. Classificação do Momento do Culto:
   - Identifique com precisão o momento da foto: 'Louvor Intimista / Pouca Luz', 'Pregação / Palavra', 'Celebração / LEDs Cênicos', 'Retrato de Voluntário / Membro', 'Batismo / Cerimônia' ou 'Geral'.
2. Balanço Kelvin e Matiz (Tint):
   - Elimine dominantes esverdeadas ou azuladas fluorescentes, garantindo calor humano saudável na pele.
3. Faixa Dinâmica (HDR Eclesiástico):
   - 'highlights_recovery': recupere textura em telões de LED e tecidos brancos brilhantes.
   - 'shadows_lift': revele fiéis na penumbra sem esbranquiçar os níveis de preto (sem milky blacks).
4. Contraste, Saturação e Vibração:
   - Aplique uma curva S elegante e aumente a vibração sem supersaturar a melanina da pele.
5. Presets Inteligentes Contextuais:
   - Recomende 1 Preset Principal (`suggested_preset`).
   - Retorne exatamente 3 Presets Alternativos (`alternative_presets`) contextuais para a cena:
     a) "Luz Quente Natural" (Tons terrosos e orgânicos, acolhedor)
     b) "Clean / Moderno Neutro" (Balanço de estúdio limpo, alta fidelidade de cor)
     c) "Moody / Contraste Cênico" (Cinematográfico, sombras profundas e luzes dramáticas)

=============================================================================
VERTENTE 2: Correção de Falhas, Anomalias de Lente & Luz Extrema
=============================================================================
1. Aberrações Cromáticas (`chromatic_aberration_fix`):
   - Detecte e atenue franjas roxas/verdes (fringing) em volta de canhões de luz e contornos contraluz.
2. Restauração de LEDs Estourados (`led_clipping_restoration`):
   - Reconstrua áreas onde LEDs azuis, vermelhos ou magenta saturaram completamente o sensor (clipping).
3. Vinheta e Distorção (`vignette_correction`, `lens_distortion_correction`):
   - Compense o escurecimento periférico e a deformação de grande-angular de celulares.
4. Denoising Seletivo (`selective_denoise`):
   - Reduza o ruído térmico/ISO alto sem perder textura em cabelos, olhos e tecidos.
5. Proteção de Melanina (`skin_tone_protection_strength`):
   - Preserve tons de pele naturais saudáveis (0.80 a 0.95).

=============================================================================
VERTENTE 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh DSLR)
=============================================================================
1. Ponto Focal Inteligente (`focal_point_x`, `focal_point_y`):
   - Identifique com coordenadas normalizadas [0.0..1.0] o centro do assunto principal (ex: rosto do pregador, mãos do instrumentista, pessoa em oração).
2. Simulação de Abertura f/Stop (`f_stop_simulation`):
   - Sugira abertura ideal (ex: f/1.8 a f/2.8 para retratos/louvor com bokeh de fundo, f/4.0 a f/5.6 para grupos).
3. Microcontraste e Nitidez Seletiva (`subject_microcontrast`):
   - Aplique ganho de nitidez exclusivamente sobre o sujeito focado.

Retorne SEMPRE o JSON estrito correspondente ao schema ColorimetryParameters.
"""


class GeminiColorimetryAnalyzer:
    """
    Analyzes church photographs using Gemini Vision API with structured JSON output
    divided into 3 specialized DSLR branches.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        api_key_override: Optional[str] = None
    ) -> ColorimetryParameters:
        """
        Send image to Gemini API with response_schema to receive strictly-typed parameters.
        """
        active_key = api_key_override or self.api_key
        
        if active_key and len(active_key.strip()) > 10:
            try:
                return self._call_gemini_api(image_bytes, mime_type, active_key)
            except Exception as e:
                print(f"[GeminiAnalyzer] API Call failed: {e}. Falling back to 3-stage heuristic engine.")
                return self._fallback_heuristic_analysis(image_bytes)
        else:
            return self._fallback_heuristic_analysis(image_bytes)

    def _call_gemini_api(
        self,
        image_bytes: bytes,
        mime_type: str,
        api_key: str
    ) -> ColorimetryParameters:
        """
        Executes structured output call to Gemini using the google-genai SDK.
        """
        pil_img = Image.open(io.BytesIO(image_bytes))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
            
        max_dim = 1600
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG", quality=85)
        optimized_bytes = buffered.getvalue()

        # Method 1: Use google-genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            
            prompt = (
                "Analise esta fotografia de culto/evento e calcule a calibração fotográfica profissional DSLR "
                "nas 3 vertentes: (1) Cor/Luz/Estilo e Presets contextuais, (2) Correção Óptica e LEDs estourados, "
                "e (3) Ponto focal e simulação de Bokeh/Profundidade de campo."
            )

            models_to_try = [settings.GEMINI_MODEL] + [m for m in settings.GEMINI_FALLBACK_MODELS if m != settings.GEMINI_MODEL]
            
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=optimized_bytes, mime_type="image/jpeg"),
                            prompt,
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction=CHURCH_PHOTOGRAPHY_SYSTEM_INSTRUCTION,
                            response_mime_type="application/json",
                            response_schema=ColorimetryParameters,
                            temperature=0.2,
                        ),
                    )

                    if response.text:
                        data = json.loads(response.text)
                        return ColorimetryParameters(**data)
                except Exception as model_err:
                    print(f"[GeminiAnalyzer] Model {model_name} attempt failed: {model_err}")
                    continue
        except ImportError:
            pass
        except Exception as e:
            print(f"[GeminiAnalyzer] google-genai method error: {e}")

        # Fallback to heuristic
        return self._fallback_heuristic_analysis(image_bytes)

    def _fallback_heuristic_analysis(self, image_bytes: bytes) -> ColorimetryParameters:
        """
        Deterministic image analysis calculating scene metrics across all 3 DSLR branches.
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Downsample for fast analysis
            pil_img.thumbnail((400, 400), Image.Resampling.BOX)
            w, h = pil_img.size
            img_arr = np.array(pil_img, dtype=np.float32) / 255.0

            r, g, b = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            mean_lum = float(np.mean(luminance))
            
            # Exposure compensation
            lum_diff = 0.50 - mean_lum
            exposure = float(np.clip(lum_diff * 1.8, -1.2, 1.4))

            # Temperature heuristic (Red vs Blue ratio)
            mean_r = float(np.mean(r))
            mean_b = float(np.mean(b))
            mean_g = float(np.mean(g))
            
            rb_ratio = (mean_r + 1e-4) / (mean_b + 1e-4)
            if rb_ratio > 1.3:
                kelvin = int(np.clip(5200 - (rb_ratio - 1.0) * 1200, 3200, 6200))
            elif rb_ratio < 0.8:
                kelvin = int(np.clip(5500 + (1.0 - rb_ratio) * 2200, 4800, 8200))
            else:
                kelvin = 5500

            # Tint heuristic
            tint_val = float(np.clip((mean_g - (mean_r + mean_b) / 2.0) * 120.0, -35.0, 35.0))

            # Shadows / Highlights
            shadow_pixels = float(np.sum(luminance < 0.18) / luminance.size)
            highlight_pixels = float(np.sum(luminance > 0.85) / luminance.size)

            shadows_lift = float(np.clip(shadow_pixels * 1.5 + 0.25, 0.20, 0.75))
            highlights_recovery = float(np.clip(highlight_pixels * 2.2 + 0.30, 0.25, 0.85))

            # Stage LED Spill & Clipping detection
            blue_spill = float(np.sum((b > 0.70) & (b > r * 1.35)) / b.size)
            red_spill = float(np.sum((r > 0.75) & (r > g * 1.45)) / r.size)
            led_clipping = float(np.clip((blue_spill + red_spill) * 2.5 + 0.30, 0.25, 0.85))

            # Ponto Focal Heurístico (Centro de massa ponderado por luminância e contraste facial)
            # Find center of highest contrast & luminance in upper 60% of image
            upper_lum = luminance[:int(h * 0.75), :]
            if upper_lum.size > 0:
                # Weighted center of mass
                weights = (upper_lum ** 2)
                sum_w = np.sum(weights) + 1e-5
                y_coords, x_coords = np.indices(upper_lum.shape)
                focal_px_y = float(np.sum(y_coords * weights) / sum_w)
                focal_px_x = float(np.sum(x_coords * weights) / sum_w)
                focal_norm_x = float(np.clip(focal_px_x / w, 0.2, 0.8))
                focal_norm_y = float(np.clip(focal_px_y / h, 0.2, 0.7))
            else:
                focal_norm_x, focal_norm_y = 0.50, 0.40

            # Scene Classification
            if shadow_pixels > 0.35 and mean_lum < 0.30:
                scene_moment = "Louvor Intimista / Pouca Luz"
                suggested_preset = "Moody / Contraste Cênico"
                f_stop = 1.8
            elif blue_spill > 0.06 or red_spill > 0.06:
                scene_moment = "Celebração / LEDs Cênicos"
                suggested_preset = "Clean / Moderno Neutro"
                f_stop = 2.8
            elif mean_lum > 0.55:
                scene_moment = "Pregação / Palavra"
                suggested_preset = "Luz Quente Natural"
                f_stop = 2.8
            else:
                scene_moment = "Retrato de Voluntário / Membro"
                suggested_preset = "Luz Quente Natural"
                f_stop = 2.0

            # Presets Contextuais Alternativos
            alt_presets = [
                PresetData(
                    id="luz_quente_natural",
                    name="Luz Quente Natural",
                    description="Tons de pele acolhedores e temperatura orgânica para louvor e palavra.",
                    icon="fa-sun text-amber-400",
                    exposure_compensation=round(exposure + 0.15, 2),
                    temperature_kelvin=max(5200, kelvin + 300),
                    tint=-2.0,
                    contrast=1.06,
                    highlights_recovery=round(highlights_recovery, 2),
                    shadows_lift=round(min(1.0, shadows_lift + 0.10), 2),
                    saturation=1.04,
                    vibrance=1.08,
                    chromatic_aberration_fix=0.50,
                    vignette_correction=0.35,
                    led_clipping_restoration=round(led_clipping, 2),
                    selective_denoise=0.28,
                    skin_tone_protection_strength=0.92,
                    f_stop_simulation=2.4,
                    subject_microcontrast=0.80
                ),
                PresetData(
                    id="clean_moderno_neutro",
                    name="Clean / Moderno Neutro",
                    description="Balanço neutro de estúdio com alta fidelidade e atenuação de reflexos de LED.",
                    icon="fa-wand-magic text-blue-400",
                    exposure_compensation=round(exposure, 2),
                    temperature_kelvin=5400,
                    tint=0.0,
                    contrast=1.10,
                    highlights_recovery=round(min(1.0, highlights_recovery + 0.15), 2),
                    shadows_lift=round(shadows_lift, 2),
                    saturation=0.98,
                    vibrance=1.02,
                    chromatic_aberration_fix=0.65,
                    vignette_correction=0.40,
                    led_clipping_restoration=round(min(1.0, led_clipping + 0.20), 2),
                    selective_denoise=0.35,
                    skin_tone_protection_strength=0.88,
                    f_stop_simulation=2.8,
                    subject_microcontrast=0.75
                ),
                PresetData(
                    id="moody_contraste_cenico",
                    name="Moody / Contraste Cênico",
                    description="Visual cinematográfico com sombras profundas e realce cênico no sujeito.",
                    icon="fa-film text-purple-400",
                    exposure_compensation=round(exposure - 0.10, 2),
                    temperature_kelvin=max(4800, kelvin - 200),
                    tint=4.0,
                    contrast=1.20,
                    highlights_recovery=0.65,
                    shadows_lift=0.25,
                    saturation=1.06,
                    vibrance=1.12,
                    chromatic_aberration_fix=0.55,
                    vignette_correction=0.20,
                    led_clipping_restoration=0.60,
                    selective_denoise=0.25,
                    skin_tone_protection_strength=0.85,
                    f_stop_simulation=1.8,
                    subject_microcontrast=0.90
                )
            ]

            return ColorimetryParameters(
                exposure_compensation=round(exposure, 2),
                temperature_kelvin=kelvin,
                tint=round(tint_val, 1),
                contrast=1.10,
                highlights_recovery=round(highlights_recovery, 2),
                shadows_lift=round(shadows_lift, 2),
                saturation=1.03,
                vibrance=1.07,
                chromatic_aberration_fix=0.50,
                vignette_correction=0.35,
                lens_distortion_correction=0.20,
                led_clipping_restoration=round(led_clipping, 2),
                stage_led_tint_suppression=round(led_clipping * 0.8, 2),
                blue_led_attenuation=round(min(1.0, blue_spill * 3.0 + 0.2), 2),
                red_magenta_attenuation=round(min(1.0, red_spill * 3.0 + 0.2), 2),
                selective_denoise=0.30,
                skin_tone_protection_strength=0.88,
                focal_point_x=round(focal_norm_x, 2),
                focal_point_y=round(focal_norm_y, 2),
                f_stop_simulation=f_stop,
                bokeh_smoothness=0.75,
                subject_microcontrast=0.75,
                scene_moment=scene_moment,
                detected_lighting_condition=f"Iluminação cênica ({scene_moment}) com compensação de LEDs",
                detected_scene_type="Culto / Palco",
                subject_description="Sujeito principal no foco da cena",
                analysis_summary=(
                    f"Diagnóstico DSLR ({scene_moment}): Balanço a {kelvin}K, "
                    f"exposição {exposure:+.2f} EV, restauração de LEDs estourados ({int(led_clipping*100)}%) "
                    f"e profundidade de campo f/{f_stop:.1f} com foco no sujeito."
                ),
                suggested_preset=suggested_preset,
                alternative_presets=alt_presets
            )
        except Exception as e:
            print(f"[GeminiAnalyzer] Heuristic fallback error: {e}")
            return ColorimetryParameters()
