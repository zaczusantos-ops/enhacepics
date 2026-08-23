"""
ChurchPhoto Pro - FastAPI Application & REST API Endpoints with Authentication
"""

import time
import json
from typing import Optional, List, Dict
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .schemas.colorimetry import (
    ColorimetryParameters,
    AnalysisResponse,
    ProcessedImageMetadata,
    FullPipelineResponse,
)
from .schemas.auth import (
    GoogleLoginRequest,
    EmailLoginRequest,
    EmailRegisterRequest,
    UserProfile,
    AuthResponse,
)
from .services.gemini_analyzer import GeminiColorimetryAnalyzer
from .services.auth_service import auth_service
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

# Security bearer scheme
security = HTTPBearer(auto_error=False)

# Initialize singletons
analyzer = GeminiColorimetryAnalyzer()
processor = ChurchPhotoProcessor()

# Built-in Church Event Presets
CHURCH_PRESETS = [
    {
        "id": "luz_quente_natural",
        "name": "Luz Quente Natural",
        "description": "Tons de pele acolhedores e calor orgânico para louvor e palavra.",
        "params": ColorimetryParameters(
            exposure_compensation=0.20,
            temperature_kelvin=5700,
            tint=-2.0,
            contrast=1.06,
            highlights_recovery=0.45,
            shadows_lift=0.40,
            saturation=1.04,
            vibrance=1.08,
            chromatic_aberration_fix=0.50,
            vignette_correction=0.35,
            lens_distortion_correction=0.20,
            led_clipping_restoration=0.60,
            stage_led_tint_suppression=0.45,
            selective_denoise=0.28,
            skin_tone_protection_strength=0.92,
            f_stop_simulation=2.4,
            bokeh_smoothness: 0.75,
            subject_microcontrast: 0.80,
            scene_moment="Louvor / Palco",
            analysis_summary="Equilíbrio de calor humano com proteção de pele e profundidade f/2.4."
        )
    },
    {
        "id": "clean_moderno_neutro",
        "name": "Clean / Moderno Neutro",
        "description": "Balanço de estúdio limpo com atenuação precisa de reflexos de LED.",
        "params": ColorimetryParameters(
            exposure_compensation=0.10,
            temperature_kelvin=5400,
            tint=0.0,
            contrast=1.10,
            highlights_recovery=0.55,
            shadows_lift=0.35,
            saturation=0.98,
            vibrance=1.02,
            chromatic_aberration_fix=0.65,
            vignette_correction=0.40,
            lens_distortion_correction=0.20,
            led_clipping_restoration=0.70,
            stage_led_tint_suppression=0.55,
            selective_denoise=0.35,
            skin_tone_protection_strength=0.88,
            f_stop_simulation=2.8,
            bokeh_smoothness: 0.75,
            subject_microcontrast: 0.75,
            scene_moment="Celebração / LEDs Cênicos",
            analysis_summary="Balanço neutro de estúdio com alta fidelidade de cor."
        )
    },
    {
        "id": "moody_contraste_cenico",
        "name": "Moody / Contraste Cênico",
        "description": "Visual cinematográfico com sombras profundas e isolamento cênico.",
        "params": ColorimetryParameters(
            exposure_compensation=-0.05,
            temperature_kelvin=5100,
            tint=4.0,
            contrast=1.22,
            highlights_recovery=0.65,
            shadows_lift=0.25,
            saturation=1.06,
            vibrance=1.12,
            chromatic_aberration_fix=0.55,
            vignette_correction=0.20,
            lens_distortion_correction=0.20,
            led_clipping_restoration=0.60,
            stage_led_tint_suppression=0.40,
            selective_denoise=0.25,
            skin_tone_protection_strength=0.85,
            f_stop_simulation=1.8,
            bokeh_smoothness: 0.85,
            subject_microcontrast: 0.90,
            scene_moment="Louvor Intimista / Pouca Luz",
            analysis_summary="Visual cinematográfico com profundidade bokeh f/1.8."
        )
    }
]


# Dependency to get currently authenticated user (optional)
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserProfile]:
    if credentials and credentials.credentials:
        payload = auth_service.verify_jwt_token(credentials.credentials)
        if payload and "sub" in payload:
            return auth_service.get_user_by_id(payload["sub"])
    return None


@app.get("/api/health")
async def health_check():
    """Health check and status API."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10),
        "model": settings.GEMINI_MODEL,
        "auth_enabled": True,
    }


# =========================================================================
# AUTHENTICATION ENDPOINTS (Google OAuth & Email/Password)
# =========================================================================

@app.post("/api/auth/google", response_model=AuthResponse)
async def auth_google(request: GoogleLoginRequest):
    """
    Login / Registration using Google Identity Services (GIS) Credential Token.
    """
    try:
        response = auth_service.authenticate_google(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/auth/register", response_model=AuthResponse)
async def auth_register_email(request: EmailRegisterRequest):
    """
    Register new user with email and password.
    """
    try:
        response = auth_service.register_email(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/auth/login", response_model=AuthResponse)
async def auth_login_email(request: EmailLoginRequest):
    """
    Login with email and password.
    """
    try:
        response = auth_service.login_email(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get("/api/auth/me", response_model=UserProfile)
async def auth_get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get profile of the currently logged-in user.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido.")

    payload = auth_service.verify_jwt_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.")

    user = auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    return user


# =========================================================================
# PRESETS & IMAGE PROCESSING ENDPOINTS
# =========================================================================

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
    current_user: Optional[UserProfile] = Depends(get_optional_user),
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

        if current_user:
            auth_service.increment_processed_count(current_user.id)

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
