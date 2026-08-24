"""
ChurchPhoto Pro - Main FastAPI Application
Includes Authentication, Team Workspaces, Shared Presets, Culling Funnel & DSLR Processing.
"""

from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .services.auth_service import auth_service
from .services.db_service import db_service
from .services.culling_service import culling_service
from .services.dslr_processor import dslr_processor
from .services.gemini_analyzer import gemini_analyzer
from .schemas.photo import PhotoAnalysisResponse, BatchProcessingResponse
from .schemas.enterprise import (
    UserRegisterRequest, UserLoginRequest, AuthTokenResponse, UserPublicProfile,
    TeamCreateRequest, TeamAddMemberRequest, TeamResponse,
    TeamPresetCreateRequest, TeamPresetResponse,
    PhotoCandidate, CullingDeduplicateResponse, CullingRankingResponse, SmartCropResponse
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Motor Profissional de Curadoria, Equipes e Edição DSLR para Fotos de Culto",
    version="3.3.0"
)

# Enable CORS for frontend clients (GitHub Pages, localhost, Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to extract optional user from JWT Bearer Token
def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    return db_service.verify_jwt_token(token)


# ================= HEALTH & STATUS =================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.3.0",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "engine": "DSLR 3.0 LUT Accelerated + 3-Stage Culling Funnel"
    }


# ================= AUTHENTICATION & USERS =================

@app.post("/api/auth/register", response_model=AuthTokenResponse)
async def register(req: UserRegisterRequest):
    try:
        return db_service.register_user(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", response_model=AuthTokenResponse)
async def login(req: UserLoginRequest):
    try:
        return db_service.login_user(req)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
async def get_me(user: Optional[dict] = Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    return user


@app.get("/api/users/search", response_model=List[UserPublicProfile])
async def search_users(q: str):
    return db_service.search_users_by_username(q)


# ================= TEAMS & WORKSPACES =================

@app.get("/api/teams", response_model=List[TeamResponse])
async def list_teams(user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = user.get("sub") if user else "guest"
    return db_service.get_user_teams(user_id)


@app.post("/api/teams", response_model=TeamResponse)
async def create_team(req: TeamCreateRequest, user: Optional[dict] = Depends(get_current_user_optional)):
    user_id = user.get("sub") if user else "guest"
    return db_service.create_team(user_id, req)


@app.post("/api/teams/{team_id}/members", response_model=TeamResponse)
async def add_team_member(team_id: str, req: TeamAddMemberRequest):
    try:
        return db_service.add_member_to_team(team_id, req.username, req.role)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ================= TEAM SHARED PRESETS =================

@app.get("/api/teams/{team_id}/presets", response_model=List[TeamPresetResponse])
async def list_team_presets(team_id: str):
    return db_service.get_team_presets(team_id)


@app.post("/api/teams/{team_id}/presets", response_model=TeamPresetResponse)
async def create_team_preset(
    team_id: str,
    req: TeamPresetCreateRequest,
    user: Optional[dict] = Depends(get_current_user_optional)
):
    creator = user.get("name") if user else "Voluntário"
    return db_service.create_team_preset(team_id, creator, req)


# ================= CULLING FUNNEL (3 STAGES) =================

@app.post("/api/culling/deduplicate", response_model=CullingDeduplicateResponse)
async def culling_deduplicate(photos: List[PhotoCandidate]):
    """
    Phase 1: Groups burst / sequence shots and elects the Champion (Best Shot).
    """
    return culling_service.deduplicate_and_group(photos)


@app.post("/api/culling/ranking", response_model=CullingRankingResponse)
async def culling_ranking(photos: List[PhotoCandidate]):
    """
    Phase 2: Ranks unique photos and selects the Instagram Top 20 for carousels.
    """
    return culling_service.rank_top_photos(photos)


@app.get("/api/culling/smart-crop", response_model=SmartCropResponse)
async def culling_smart_crop(photo_id: str, width: int = 1920, height: int = 1080):
    """
    Phase 3: Computes optimal 4:5 vertical and 1:1 square crop coordinates.
    """
    return culling_service.calculate_smart_crop(photo_id, width, height)


# ================= DSLR IMAGE PROCESSING =================

@app.post("/api/analyze-and-process")
async def analyze_and_process(
    file: UploadFile = File(...),
    output_format: str = Form("JPEG"),
    output_quality: int = Form(90),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    # 1. AI Analysis
    analysis = gemini_analyzer.analyze_church_scene(contents, file.filename or "culto.jpg")

    # 2. DSLR Processing
    result = dslr_processor.process_image(
        image_bytes=contents,
        params=analysis,
        output_format=output_format,
        output_quality=output_quality
    )

    return {
        "success": True,
        "image_base64": result.image_base64,
        "original_base64": result.original_base64,
        "analysis": analysis.dict(),
        "metadata": result.metadata.dict(),
    }
