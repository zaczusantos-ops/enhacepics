"""
ChurchPhoto Pro - FastAPI Application & REST API Endpoints
"""

import time
import json
from typing import Optional, List, Dict
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .schemas.colorimetry import (
    ColorimetryParameters,
    AnalysisResponse,
    ProcessedImageMetadata,
    FullPipelineResponse,
)
from .services.gemini_analyzer import GeminiColorimetryAnalyzer
from .engine.processor import ChurchPhotoProcessor

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Pós-Processamento Fotográfico para Cultos e Eventos de Igreja",
)

# Enable CORS for Next.js frontend and local dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
analyzer = GeminiColorimetryAnalyzer()
processor = ChurchPhotoProcessor()

# Built-in Church Event Presets
CHURCH_PRESETS = [
    {
        "id": "culto_contemporaneo",
        "name": "Culto Contemporâneo (LEDs de Palco)",
        "description": "Atenua LEDs azuis/magentas, preserva calor de pele e recupera realces dos telões.",
        "params": ColorimetryParameters(
            exposure_compensation=0.25,
            temperature_kelvin=5400,
            tint=-5.0,
            contrast=1.12,
            highlights_recovery=0.60,
            shadows_lift=0.45,
            saturation=1.04,
            stage_led_tint_suppression=0.65,
            blue_led_attenuation=0.55,
            red_magenta_attenuation=0.50,
            skin_tone_protection_strength=0.90,
            denoise_strength=0.30,
            unsharp_mask_amount=0.75,
            unsharp_mask_radius=1.2,
            detected_lighting_condition="Palco contemporâneo com refletores LED e contraluz",
            detected_scene_type="Louvor / Ministério de Música",
            analysis_summary="Equilíbrio de iluminação de palco contemporânea com proteção estrita de tom de pele.",
            suggested_preset="Culto Contemporâneo"
        )
    },
    {
        "id": "culto_tradicional",
        "name": "Culto Tradicional (Madeira & Luz Quente)",
        "description": "Corrige sombras do púlpito, equilibra tons tungstênio/madeira e dá acabamento nítido.",
        "params": ColorimetryParameters(
            exposure_compensation=0.15,
            temperature_kelvin=5100,
            tint=2.0,
            contrast=1.05,
            highlights_recovery=0.35,
            shadows_lift=0.50,
            saturation=0.98,
            stage_led_tint_suppression=0.15,
            blue_led_attenuation=0.10,
            red_magenta_attenuation=0.15,
            skin_tone_protection_strength=0.85,
            denoise_strength=0.20,
            unsharp_mask_amount=0.60,
            unsharp_mask_radius=1.0,
            detected_lighting_condition="Iluminação incandescente e madeira com sombras suaves",
            detected_scene_type="Púlpito / Pregador",
            analysis_summary="Balanço tonal suave para púlpito tradicional sem saturação excessiva.",
            suggested_preset="Culto Tradicional"
        )
    },
    {
        "id": "louvor_adoracao",
        "name": "Louvor & Adoração (Baixa Luz / Intimista)",
        "description": "Forte redução de ruído de alto ISO, realce de sombras do público e suavização de contraste.",
        "params": ColorimetryParameters(
            exposure_compensation=0.50,
            temperature_kelvin=5600,
            tint=-3.0,
            contrast=1.08,
            highlights_recovery=0.70,
            shadows_lift=0.70,
            saturation=1.05,
            stage_led_tint_suppression=0.50,
            blue_led_attenuation=0.45,
            red_magenta_attenuation=0.40,
            skin_tone_protection_strength=0.92,
            denoise_strength=0.50,
            unsharp_mask_amount=0.80,
            unsharp_mask_radius=1.3,
            detected_lighting_condition="Ambiente de adoração em penumbra com focos de luz",
            detected_scene_type="Congregação / Público",
            analysis_summary="Ganho de exposição e redução de ruído ISO para momentos de adoração em baixa luz.",
            suggested_preset="Louvor & Adoração"
        )
    },
    {
        "id": "evento_externo",
        "name": "Batismo & Evento Externo (Luz Natural)",
        "description": "Cores naturais, céu equilibrado e tons de pele radiantes para eventos diurnos ao ar livre.",
        "params": ColorimetryParameters(
            exposure_compensation=0.0,
            temperature_kelvin=5800,
            tint=0.0,
            contrast=1.10,
            highlights_recovery=0.40,
            shadows_lift=0.25,
            saturation=1.08,
            stage_led_tint_suppression=0.0,
            blue_led_attenuation=0.0,
            red_magenta_attenuation=0.0,
            skin_tone_protection_strength=0.80,
            denoise_strength=0.10,
            unsharp_mask_amount=0.50,
            unsharp_mask_radius=1.0,
            detected_lighting_condition="Luz natural do dia / Área aberta",
            detected_scene_type="Batismo / Cerimônia",
            analysis_summary="Fotografia diurna nítida com preservação de céu e folhagens.",
            suggested_preset="Evento Externo"
        )
    }
]


@app.get("/api/health")
async def health_check():
    """Health check and status API."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10),
        "model": settings.GEMINI_MODEL,
    }


@app.get("/api/presets")
async def get_presets():
    """Returns curated church photo presets."""
    return {"presets": CHURCH_PRESETS}


@app.post("/api/analyze-and-process", response_model=FullPipelineResponse)
async def analyze_and_process_photo(
    file: UploadFile = File(...),
    output_format: str = Form("JPEG"),
    output_quality: int = Form(92),
    x_gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"),
):
    """
    Complete hybrid pipeline:
    1. Receives uploaded church photo (JPEG, PNG, RAW).
    2. Sends to Gemini API for structured JSON colorimetric analysis.
    3. Applies deterministic Python image processing engine (OpenCV/Pillow/NumPy).
    4. Returns processed image base64, before/after preview, telemetry metadata and applied parameters.
    """
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

        # Step 1: Gemini Analysis
        gemini_key = x_gemini_key or settings.GEMINI_API_KEY
        params = analyzer.analyze_image(
            image_bytes=contents,
            mime_type=file.content_type or "image/jpeg",
            api_key_override=gemini_key
        )

        # Step 2: Deterministic Image Processing
        _, processed_b64, metadata, orig_b64 = processor.process(
            image_bytes=contents,
            params=params,
            filename=file.filename or "photo.jpg",
            output_format=output_format,
            output_quality=output_quality,
            include_original_preview=True
        )

        return FullPipelineResponse(
            success=True,
            image_base64=processed_b64,
            original_base64=orig_b64,
            metadata=metadata,
            analysis=params
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no processamento da imagem: {str(e)}")


@app.post("/api/process-manual", response_model=FullPipelineResponse)
async def process_manual_adjustments(
    file: UploadFile = File(...),
    parameters_json: str = Form(...),
    output_format: str = Form("JPEG"),
    output_quality: int = Form(92),
):
    """
    Reprocesses the photo with custom/fine-tuned parameters from user sliders in real-time.
    """
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

        # Parse parameters JSON
        params_dict = json.loads(parameters_json)
        params = ColorimetryParameters(**params_dict)

        _, processed_b64, metadata, orig_b64 = processor.process(
            image_bytes=contents,
            params=params,
            filename=file.filename or "photo.jpg",
            output_format=output_format,
            output_quality=output_quality,
            include_original_preview=True
        )

        return FullPipelineResponse(
            success=True,
            image_base64=processed_b64,
            original_base64=orig_b64,
            metadata=metadata,
            analysis=params
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no reprocessamento: {str(e)}")


# Serve static web frontend if available
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "ChurchPhoto Pro API Backend está operando com sucesso."}
