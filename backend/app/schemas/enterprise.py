"""
ChurchPhoto Pro - Enterprise Schemas
Users, Teams, Members, Presets, Culling Funnel & Smart Crop
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ================= USER & AUTH SCHEMAS =================

class UserBase(BaseModel):
    username: str
    email: str
    name: str
    church_name: Optional[str] = "Igreja Local"
    role: Optional[str] = "photographer"
    avatar_url: Optional[str] = None


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str
    church_name: Optional[str] = "Igreja Local"


class UserLoginRequest(BaseModel):
    email_or_username: str
    password: str


class UserPublicProfile(UserBase):
    id: str
    created_at: str
    teams_count: int = 0


class AuthTokenResponse(BaseModel):
    success: bool
    token: str
    user: UserPublicProfile
    message: str


# ================= TEAM & WORKSPACE SCHEMAS =================

class TeamMember(BaseModel):
    user_id: str
    username: str
    name: str
    avatar_url: Optional[str] = None
    role: str = "member"  # "owner", "admin", "member"
    joined_at: str


class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    church_name: Optional[str] = "Igreja Local"


class TeamAddMemberRequest(BaseModel):
    username: str
    role: str = "member"


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    church_name: str
    owner_id: str
    members: List[TeamMember] = []
    created_at: str


# ================= TEAM SHARED PRESETS =================

class TeamPresetParams(BaseModel):
    exposure_compensation: float = 0.0
    temperature_kelvin: int = 5500
    tint: float = 0.0
    contrast: float = 1.10
    highlights_recovery: float = 0.45
    shadows_lift: float = 0.35
    saturation: float = 1.0
    vibrance: float = 1.05
    chromatic_aberration_fix: float = 0.50
    led_clipping_restoration: float = 0.60
    stage_led_tint_suppression: float = 0.45
    vignette_correction: float = 0.35
    selective_denoise: float = 0.30
    skin_tone_protection_strength: float = 0.88
    f_stop_simulation: float = 2.8
    bokeh_smoothness: float = 0.75
    subject_microcontrast: float = 0.75
    target_aspect_ratio: Optional[str] = "4:5"


class TeamPresetCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str = "Geral"  # "Louvor", "Pregação", "Comunhão", "Geral"
    params: TeamPresetParams


class TeamPresetResponse(BaseModel):
    id: str
    team_id: str
    name: str
    description: str
    category: str
    params: TeamPresetParams
    created_by_name: str
    created_at: str


# ================= CULLING FUNNEL & SMART CROP SCHEMAS =================

# Phase 1: Deduplication & Best Shot
class PhotoCandidate(BaseModel):
    photo_id: str
    file_name: str
    image_base64: Optional[str] = None
    width: Optional[int] = 0
    height: Optional[int] = 0


class CullingGroup(BaseModel):
    group_id: str
    group_name: str
    champion_photo_id: str
    confidence: float = 0.95
    reason: str = "Melhor nitidez, olhos abertos e expressividade"
    all_photo_ids: List[str] = []
    discarded_photo_ids: List[str] = []


class CullingDeduplicateResponse(BaseModel):
    success: bool
    total_photos_analyzed: int
    total_groups_formed: int
    champions_count: int
    discarded_count: int
    groups: List[CullingGroup]


# Phase 2: Top 20 Instagram Ranking
class RankedPhotoItem(BaseModel):
    photo_id: str
    file_name: str
    ai_score: float = Field(..., description="Pontuação técnica de 0.0 a 10.0")
    rank_position: int
    is_top_20: bool = True
    composition_highlight: str
    lighting_evaluation: str
    expression_note: str


class CullingRankingResponse(BaseModel):
    success: bool
    total_evaluated: int
    top_20_count: int
    ranked_photos: List[RankedPhotoItem]


# Phase 3: Smart Crop Coordinates
class CropCoordinates(BaseModel):
    x: float = Field(..., description="Coordenada X normalizada (0.0 a 1.0)")
    y: float = Field(..., description="Coordenada Y normalizada (0.0 a 1.0)")
    width: float = Field(..., description="Largura normalizada (0.0 a 1.0)")
    height: float = Field(..., description="Altura normalizada (0.0 a 1.0)")
    aspect_ratio: str = "4:5"
    composition_rule: str = "Regra dos terços com sujeito centralizado"


class SmartCropResponse(BaseModel):
    success: bool
    photo_id: str
    suggested_crop: CropCoordinates
    alternative_square_crop: CropCoordinates
