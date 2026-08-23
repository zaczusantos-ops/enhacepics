"""
ChurchPhoto Pro - Gemini Photographic Colorimetry Analyzer
Integrates with Google AI Studio / Gemini API SDK using Structured Outputs (JSON Schema).
"""

import json
import time
import base64
import io
from typing import Optional
from PIL import Image

from ..config import settings
from ..schemas.colorimetry import ColorimetryParameters, AnalysisResponse

# Specialized System Instruction for Church and Live Event Photography
CHURCH_PHOTOGRAPHY_SYSTEM_INSTRUCTION = """
Você é um Arquiteto e Engenheiro de Colorimetria Fotográfica Sênior especializado em fotografia de cultos, shows ao vivo e eventos eclesiásticos.
Sua missão é analisar visualmente a fotografia enviada e calcular com extrema precisão os parâmetros de tratamento e calibração de cor em JSON estruturado.

Diretrizes de Análise Colorimétrica Eclesiástica:
1. ILUMINAÇÃO DE PALCO E LEDS CÊNICOS:
   - Identifique contaminações de canhões PAR LED azuis, cianos, roxos ou vermelhos que descaracterizam a cena ou "mancham" a pele dos membros.
   - Ative 'stage_led_tint_suppression', 'blue_led_attenuation' e 'red_magenta_attenuation' adequadamente para neutralizar vazamentos sem apagar a ambiência do culto.

2. PRESERVAÇÃO E PROTEÇÃO DE TONS DE PELE (Melanina Natural):
   - Os rostos dos pregadores, ministros de louvor e fiéis NUNCA devem ficar cadavéricos, azulados, magenta estourado ou com perda de textura natural.
   - Ajuste 'skin_tone_protection_strength' (recomendado 0.75 a 0.95) e equilibre a temperatura de cor (Kelvin) e tint para que a pele humana permaneça com calor saudável e natural.

3. FAIXA DINÂMICA (High Dynamic Range) & AMBIENTE ESCURO:
   - Cultos frequentemente possuem telões de LED ou refletores de alta luminosidade (altas luzes estouradas) e público na penumbra (sombras profundas).
   - Use 'highlights_recovery' para recuperar detalhes nos telões e tecidos brilhantes.
   - Use 'shadows_lift' para revelar a congregação e detalhes no palco sem esbranquiçar os níveis de preto (sem causar milky blacks).

4. EXPOSIÇÃO E CONTRASTE:
   - Fotos capturadas por celulares costumam vir subexpostas ou com alto contraste artificial. Calcule 'exposure_compensation' e 'contrast' para uma curva tonal natural de câmera profissional Full-Frame.

5. RUÍDO DE ALTO ISO E NITIDEZ:
   - Ambientes com baixa luz geram ruído de crominância/luminância. Defina 'denoise_strength' e 'unsharp_mask_amount' para suavizar o granulado mantendo olhos, cabelos e roupas nítidos.

6. LIMITES E DETERMINISMO:
   - NUNCA sugira valores fora dos limites especificados no schema.
   - Forneça uma análise fotográfica sucinta e profissional em 'analysis_summary'.
"""


class GeminiColorimetryAnalyzer:
    """
    Analyzes church photographs using Gemini Vision API with structured JSON output.
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
        Send image to Gemini API with response_schema to receive strictly-typed colorimetry values.
        """
        active_key = api_key_override or self.api_key
        
        # If API key is available, call Gemini API
        if active_key and len(active_key.strip()) > 10:
            try:
                return self._call_gemini_api(image_bytes, mime_type, active_key)
            except Exception as e:
                print(f"[GeminiAnalyzer] API Call failed: {e}. Falling back to visual heuristic engine.")
                return self._fallback_heuristic_analysis(image_bytes)
        else:
            # Fallback heuristic analyzer based on image histogram and pixel statistics
            return self._fallback_heuristic_analysis(image_bytes)

    def _call_gemini_api(
        self,
        image_bytes: bytes,
        mime_type: str,
        api_key: str
    ) -> ColorimetryParameters:
        """
        Executes structured output call to Gemini using the google-genai or google.generativeai SDK.
        """
        # Ensure image is resized to max 1600px for fast telemetry analysis
        pil_img = Image.open(io.BytesIO(image_bytes))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
            
        max_dim = 1600
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG", quality=85)
        optimized_bytes = buffered.getvalue()

        # Method 1: Use google-genai SDK (v2.x)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            
            prompt = (
                "Analise esta fotografia de culto/evento e calcule a calibração colorimétrica ideal "
                "para restaurar tons de pele naturais, atenuar luzes de palco duras (LEDs) e equilibrar a exposição."
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

        # Method 2: Fallback to google.generativeai legacy SDK
        try:
            import google.generativeai as legacy_genai

            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=CHURCH_PHOTOGRAPHY_SYSTEM_INSTRUCTION,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": ColorimetryParameters,
                    "temperature": 0.2,
                }
            )

            response = model.generate_content([
                {"mime_type": "image/jpeg", "data": optimized_bytes},
                "Analise esta foto de evento e calcule os parâmetros de colorimetria estruturados."
            ])

            if response.text:
                data = json.loads(response.text)
                return ColorimetryParameters(**data)
        except Exception as e:
            print(f"[GeminiAnalyzer] legacy genai error: {e}")

        # If both SDK calls fail, use robust deterministic heuristic
        return self._fallback_heuristic_analysis(image_bytes)

    def _fallback_heuristic_analysis(self, image_bytes: bytes) -> ColorimetryParameters:
        """
        Deterministic image statistics analysis (calculates mean luminance, color channel bias,
        highlight/shadow clipping and stage LED saturation in HSV) when Gemini key is not supplied.
        """
        import numpy as np

        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Downsample for fast telemetry
            pil_img.thumbnail((400, 400), Image.Resampling.BOX)
            img_arr = np.array(pil_img, dtype=np.float32)

            r, g, b = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            mean_lum = float(np.mean(luminance))
            
            # Exposure compensation heuristic
            target_lum = 128.0
            lum_diff = target_lum - mean_lum
            # Map -128..128 to EV compensation -1.2..+1.5
            exposure = float(np.clip(lum_diff / 80.0, -1.5, 1.5))

            # Temperature heuristic (Red vs Blue ratio)
            mean_r = float(np.mean(r))
            mean_b = float(np.mean(b))
            mean_g = float(np.mean(g))
            
            rb_ratio = (mean_r + 1e-5) / (mean_b + 1e-5)
            if rb_ratio > 1.3:
                # Very warm/tungsten, cool it down slightly
                kelvin = int(np.clip(5200 - (rb_ratio - 1.0) * 1200, 3200, 6500))
            elif rb_ratio < 0.8:
                # Very blue/LED stage lighting, warm it up
                kelvin = int(np.clip(5500 + (1.0 - rb_ratio) * 2000, 4500, 8000))
            else:
                kelvin = 5600

            # Tint heuristic (Green vs (Red+Blue)/2)
            rb_avg = (mean_r + mean_b) / 2.0
            tint_val = float(np.clip((mean_g - rb_avg) * 0.8, -35.0, 35.0))

            # Shadows / Highlights detection
            shadow_pixels = np.sum(luminance < 40) / luminance.size
            highlight_pixels = np.sum(luminance > 220) / luminance.size

            shadows_lift = float(np.clip(shadow_pixels * 1.5 + 0.25, 0.15, 0.75))
            highlights_recovery = float(np.clip(highlight_pixels * 2.0 + 0.3, 0.2, 0.85))

            # Stage LED detection (High blue or magenta saturation)
            blue_spill = float(np.sum((b > 180) & (b > r * 1.4)) / b.size)
            red_spill = float(np.sum((r > 190) & (r > g * 1.5)) / r.size)

            blue_attenuation = float(np.clip(blue_spill * 3.0 + 0.25, 0.1, 0.85))
            red_attenuation = float(np.clip(red_spill * 3.0 + 0.2, 0.1, 0.8))
            stage_led_suppression = max(blue_attenuation, red_attenuation)

            detected_lights = []
            if blue_spill > 0.05:
                detected_lights.append("Forte iluminação cênica de LED Azul/Ciano")
            if red_spill > 0.05:
                detected_lights.append("Canhões PAR LED Vermelho/Magenta")
            if shadow_pixels > 0.3:
                detected_lights.append("Ambiente de congregação em baixa luz")
            if highlight_pixels > 0.1:
                detected_lights.append("Telões ou refletores de palco de alta intensidade")

            if not detected_lights:
                detected_lights.append("Iluminação mista de culto e palco")

            lighting_str = " | ".join(detected_lights)

            return ColorimetryParameters(
                exposure_compensation=round(exposure, 2),
                temperature_kelvin=kelvin,
                tint=round(tint_val, 1),
                contrast=1.08,
                highlights_recovery=round(highlights_recovery, 2),
                shadows_lift=round(shadows_lift, 2),
                saturation=1.02,
                stage_led_tint_suppression=round(stage_led_suppression, 2),
                blue_led_attenuation=round(blue_attenuation, 2),
                red_magenta_attenuation=round(red_attenuation, 2),
                skin_tone_protection_strength=0.85,
                denoise_strength=0.30,
                unsharp_mask_amount=0.65,
                unsharp_mask_radius=1.2,
                detected_lighting_condition=lighting_str,
                detected_scene_type="Culto / Palco",
                analysis_summary=(
                    f"Calibração automática: Balanço de branco calibrado para {kelvin}K, "
                    f"compensação de exposição de {exposure:+.2f} EV, realce de sombras em "
                    f"{shadows_lift*100:.0f}% e proteção avançada de tom de pele contra luzes de palco."
                ),
                suggested_preset="Culto Contemporâneo"
            )
        except Exception as e:
            print(f"[GeminiAnalyzer] Heuristic fallback error: {e}")
            return ColorimetryParameters()
