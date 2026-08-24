"""
ChurchPhoto Pro - Enterprise Database Service
Handles persistent storage for Users, Teams, Members, Shared Presets, and Projects.
"""

import os
import json
import time
import hmac
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..config import settings
from ..schemas.enterprise import (
    UserPublicProfile, UserRegisterRequest, UserLoginRequest, AuthTokenResponse,
    TeamResponse, TeamCreateRequest, TeamMember,
    TeamPresetResponse, TeamPresetCreateRequest, TeamPresetParams
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "churchphoto_db.json"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + padding).encode("utf-8"))


class DatabaseService:
    """
    Enterprise Data Store for ChurchPhoto Pro with structured collections.
    """

    def __init__(self):
        self._data: Dict[str, Any] = {
            "users": {},        # id -> user_dict
            "teams": {},        # id -> team_dict
            "presets": {},      # id -> preset_dict
            "projects": {},     # id -> project_dict
        }
        self._load()
        self._seed_default_data()

    def _load(self):
        try:
            if DB_PATH.exists():
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception as e:
            print(f"[DB] Load error: {e}")

    def _save(self):
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DB] Save error: {e}")

    def _hash_password(self, password: str, salt: str = "churchphoto_salt_2026") -> str:
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def _seed_default_data(self):
        """Seed a default Team and Shared Presets if empty."""
        if not self._data.get("presets"):
            default_presets = [
                {
                    "id": "preset_luz_quente",
                    "team_id": "global",
                    "name": "Luz Quente Natural (Equipe)",
                    "description": "Tons de pele acolhedores e calor orgânico para louvor e palavra.",
                    "category": "Louvor",
                    "params": {
                        "exposure_compensation": 0.20,
                        "temperature_kelvin": 5700,
                        "tint": -2.0,
                        "contrast": 1.06,
                        "highlights_recovery": 0.45,
                        "shadows_lift: 0.40": 0.40,
                        "saturation": 1.04,
                        "vibrance": 1.08,
                        "chromatic_aberration_fix": 0.50,
                        "led_clipping_restoration": 0.60,
                        "stage_led_tint_suppression": 0.45,
                        "vignette_correction": 0.35,
                        "selective_denoise": 0.28,
                        "skin_tone_protection_strength": 0.92,
                        "f_stop_simulation": 2.4,
                        "bokeh_smoothness": 0.75,
                        "subject_microcontrast": 0.80,
                        "target_aspect_ratio": "4:5"
                    },
                    "created_by_name": "Sistema",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "id": "preset_clean_neutro",
                    "team_id": "global",
                    "name": "Clean / Moderno Neutro (Equipe)",
                    "description": "Equilíbrio de estúdio limpo com atenuação precisa de reflexos de LED.",
                    "category": "Pregação",
                    "params": {
                        "exposure_compensation": 0.10,
                        "temperature_kelvin": 5400,
                        "tint": 0.0,
                        "contrast": 1.10,
                        "highlights_recovery": 0.55,
                        "shadows_lift": 0.35,
                        "saturation": 0.98,
                        "vibrance": 1.02,
                        "chromatic_aberration_fix": 0.65,
                        "led_clipping_restoration": 0.70,
                        "stage_led_tint_suppression": 0.55,
                        "vignette_correction": 0.40,
                        "selective_denoise": 0.35,
                        "skin_tone_protection_strength": 0.88,
                        "f_stop_simulation": 2.8,
                        "bokeh_smoothness": 0.75,
                        "subject_microcontrast": 0.75,
                        "target_aspect_ratio": "4:5"
                    },
                    "created_by_name": "Sistema",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            self._data["presets"] = {p["id"]: p for p in default_presets}
            self._save()

    # ================= AUTHENTICATION & USERS =================

    def create_jwt_token(self, user_dict: Dict[str, Any]) -> str:
        now = int(time.time())
        expire = now + (settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS * 86400)
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
            "name": user_dict["name"],
            "role": user_dict.get("role", "photographer"),
            "iat": now,
            "exp": expire,
        }
        h_b64 = _b64url_encode(json.dumps(header).encode())
        p_b64 = _b64url_encode(json.dumps(payload).encode())
        sig = hmac.new(settings.JWT_SECRET_KEY.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
        return f"{h_b64}.{p_b64}.{_b64url_encode(sig)}"

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        # 1. Try verifying with Auth0 RS256 JWKS
        try:
            import jwt
            import requests

            auth0_domain = "dev-veq7kptegw2rh1ue.us.auth0.com"
            api_audience = "https://dev-veq7kptegw2rh1ue.us.auth0.com/api/v2/"
            
            jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
            jwks = requests.get(jwks_url, timeout=3).json()
            unverified_header = jwt.get_unverified_header(token)

            if unverified_header.get("alg") == "RS256":
                rsa_key = {}
                for key in jwks.get("keys", []):
                    if key.get("kid") == unverified_header.get("kid"):
                        rsa_key = {
                            "kty": key["kty"],
                            "kid": key["kid"],
                            "use": key.get("use"),
                            "n": key["n"],
                            "e": key["e"]
                        }
                        break

                if rsa_key:
                    payload = jwt.decode(
                        token,
                        key=jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key),
                        algorithms=["RS256"],
                        audience=api_audience,
                        issuer=f"https://{auth0_domain}/"
                    )
                    return payload
        except Exception:
            pass

        # 2. Fallback to local HMAC token verification
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            h_b64, p_b64, s_b64 = parts
            expected_sig = hmac.new(settings.JWT_SECRET_KEY.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
            if not hmac.compare_digest(s_b64, _b64url_encode(expected_sig)):
                return None
            payload = json.loads(_b64url_decode(p_b64).decode())
            if payload.get("exp", 0) < int(time.time()):
                return None
            return payload
        except Exception:
            return None

    def register_user(self, req: UserRegisterRequest) -> AuthTokenResponse:
        email_clean = req.email.strip().lower()
        username_clean = req.username.strip().lower().replace(" ", "_")
        
        # Check existing username or email
        for u in self._data["users"].values():
            if u.get("email", "").lower() == email_clean or u.get("username", "").lower() == username_clean:
                # Log in if already exists
                token = self.create_jwt_token(u)
                profile = UserPublicProfile(
                    id=u["id"],
                    username=u["username"],
                    email=u["email"],
                    name=u["name"],
                    church_name=u.get("church_name", "Igreja Local"),
                    role=u.get("role", "photographer"),
                    avatar_url=u.get("avatar_url"),
                    created_at=u["created_at"],
                    teams_count=len(self.get_user_teams(u["id"]))
                )
                return AuthTokenResponse(
                    success=True,
                    token=token,
                    user=profile,
                    message=f"Bem-vindo(a) de volta, {profile.name}!"
                )

        user_id = f"usr_{hashlib.md5(username_clean.encode()).hexdigest()[:12]}"
        pwd_hash = self._hash_password(req.password)
        avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={req.name}&backgroundColor=2563eb"

        user = {
            "id": user_id,
            "username": username_clean,
            "email": email_clean,
            "name": req.name.strip(),
            "password_hash": pwd_hash,
            "church_name": req.church_name or "Igreja Local",
            "role": "photographer",
            "avatar_url": avatar,
            "created_at": datetime.utcnow().isoformat()
        }

        self._data["users"][user_id] = user

        # Automatically create default team for this user
        default_team_id = f"team_{user_id[:8]}"
        default_team = {
            "id": default_team_id,
            "name": f"Mídia {req.church_name or 'Igreja'}",
            "description": "Equipe principal de fotografia e cobertura de cultos.",
            "church_name": req.church_name or "Igreja Local",
            "owner_id": user_id,
            "members": [
                {
                    "user_id": user_id,
                    "username": username_clean,
                    "name": req.name.strip(),
                    "avatar_url": avatar,
                    "role": "owner",
                    "joined_at": datetime.utcnow().isoformat()
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }
        self._data["teams"][default_team_id] = default_team
        self._save()

        token = self.create_jwt_token(user)
        profile = UserPublicProfile(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            name=user["name"],
            church_name=user["church_name"],
            role=user["role"],
            avatar_url=user["avatar_url"],
            created_at=user["created_at"],
            teams_count=1
        )

        return AuthTokenResponse(
            success=True,
            token=token,
            user=profile,
            message="Cadastro e equipe criados com sucesso!"
        )

    def login_user(self, req: UserLoginRequest) -> AuthTokenResponse:
        query = req.email_or_username.strip().lower()
        pwd_hash = self._hash_password(req.password)

        target = None
        for u in self._data["users"].values():
            if u.get("email", "").lower() == query or u.get("username", "").lower() == query:
                target = u
                break

        if not target:
            # Seamless auto-registration if first time
            username = query.split("@")[0].replace(" ", "_")
            name = username.capitalize()
            return self.register_user(UserRegisterRequest(
                username=username,
                email=f"{username}@igreja.org" if "@" not in query else query,
                password=req.password,
                name=f"{name} (Mídia)",
                church_name="Igreja Local"
            ))

        if target.get("password_hash") != pwd_hash:
            raise ValueError("Senha incorreta.")

        token = self.create_jwt_token(target)
        profile = UserPublicProfile(
            id=target["id"],
            username=target["username"],
            email=target["email"],
            name=target["name"],
            church_name=target.get("church_name", "Igreja Local"),
            role=target.get("role", "photographer"),
            avatar_url=target.get("avatar_url"),
            created_at=target["created_at"],
            teams_count=len(self.get_user_teams(target["id"]))
        )

        return AuthTokenResponse(
            success=True,
            token=token,
            user=profile,
            message=f"Bem-vindo(a), {profile.name}!"
        )

    def search_users_by_username(self, query: str) -> List[UserPublicProfile]:
        q = query.strip().lower()
        if not q:
            return []
        results = []
        for u in self._data["users"].values():
            if q in u.get("username", "").lower() or q in u.get("name", "").lower():
                results.append(UserPublicProfile(
                    id=u["id"],
                    username=u["username"],
                    email=u["email"],
                    name=u["name"],
                    church_name=u.get("church_name", "Igreja Local"),
                    role=u.get("role", "photographer"),
                    avatar_url=u.get("avatar_url"),
                    created_at=u["created_at"],
                    teams_count=0
                ))
        return results[:10]

    # ================= TEAMS & WORKSPACES =================

    def get_user_teams(self, user_id: str) -> List[TeamResponse]:
        user_teams = []
        for t in self._data.get("teams", {}).values():
            is_member = any(m["user_id"] == user_id for m in t.get("members", []))
            if is_member or t.get("owner_id") == user_id:
                user_teams.append(TeamResponse(
                    id=t["id"],
                    name=t["name"],
                    description=t.get("description", ""),
                    church_name=t.get("church_name", "Igreja Local"),
                    owner_id=t["owner_id"],
                    members=[TeamMember(**m) for m in t.get("members", [])],
                    created_at=t["created_at"]
                ))
        return user_teams

    def create_team(self, user_id: str, req: TeamCreateRequest) -> TeamResponse:
        user = self._data["users"].get(user_id)
        team_id = f"team_{hashlib.md5((req.name + str(time.time())).encode()).hexdigest()[:10]}"
        
        team_dict = {
            "id": team_id,
            "name": req.name.strip(),
            "description": req.description or "",
            "church_name": req.church_name or "Igreja Local",
            "owner_id": user_id,
            "members": [
                {
                    "user_id": user_id,
                    "username": user["username"] if user else "user",
                    "name": user["name"] if user else "Voluntário",
                    "avatar_url": user.get("avatar_url") if user else None,
                    "role": "owner",
                    "joined_at": datetime.utcnow().isoformat()
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }

        self._data["teams"][team_id] = team_dict
        self._save()

        return TeamResponse(
            id=team_dict["id"],
            name=team_dict["name"],
            description=team_dict["description"],
            church_name=team_dict["church_name"],
            owner_id=team_dict["owner_id"],
            members=[TeamMember(**m) for m in team_dict["members"]],
            created_at=team_dict["created_at"]
        )

    def add_member_to_team(self, team_id: str, username_to_add: str, role: str = "member") -> TeamResponse:
        if team_id not in self._data.get("teams", {}):
            raise ValueError("Equipe não encontrada.")

        target_user = None
        u_clean = username_to_add.strip().lower()
        for u in self._data["users"].values():
            if u.get("username", "").lower() == u_clean or u.get("email", "").lower() == u_clean:
                target_user = u
                break

        if not target_user:
            # Create invited user placeholder
            user_id = f"usr_{hashlib.md5(u_clean.encode()).hexdigest()[:12]}"
            name = u_clean.split("@")[0].capitalize()
            target_user = {
                "id": user_id,
                "username": u_clean,
                "email": f"{u_clean}@igreja.org" if "@" not in u_clean else u_clean,
                "name": name,
                "password_hash": self._hash_password("123456"),
                "church_name": "Igreja Local",
                "role": "photographer",
                "avatar_url": f"https://api.dicebear.com/7.x/initials/svg?seed={name}&backgroundColor=2563eb",
                "created_at": datetime.utcnow().isoformat()
            }
            self._data["users"][user_id] = target_user

        team = self._data["teams"][team_id]
        # Check if already a member
        if not any(m["user_id"] == target_user["id"] for m in team.get("members", [])):
            team["members"].append({
                "user_id": target_user["id"],
                "username": target_user["username"],
                "name": target_user["name"],
                "avatar_url": target_user.get("avatar_url"),
                "role": role,
                "joined_at": datetime.utcnow().isoformat()
            })
            self._save()

        return TeamResponse(
            id=team["id"],
            name=team["name"],
            description=team.get("description", ""),
            church_name=team.get("church_name", "Igreja Local"),
            owner_id=team["owner_id"],
            members=[TeamMember(**m) for m in team["members"]],
            created_at=team["created_at"]
        )

    # ================= TEAM PRESETS =================

    def get_team_presets(self, team_id: str) -> List[TeamPresetResponse]:
        presets = []
        for p in self._data.get("presets", {}).values():
            if p.get("team_id") == team_id or p.get("team_id") == "global":
                presets.append(TeamPresetResponse(
                    id=p["id"],
                    team_id=p["team_id"],
                    name=p["name"],
                    description=p.get("description", ""),
                    category=p.get("category", "Geral"),
                    params=TeamPresetParams(**p["params"]),
                    created_by_name=p.get("created_by_name", "Voluntário"),
                    created_at=p["created_at"]
                ))
        return presets

    def create_team_preset(self, team_id: str, creator_name: str, req: TeamPresetCreateRequest) -> TeamPresetResponse:
        preset_id = f"preset_{hashlib.md5((req.name + str(time.time())).encode()).hexdigest()[:10]}"
        preset_dict = {
            "id": preset_id,
            "team_id": team_id,
            "name": req.name.strip(),
            "description": req.description or "",
            "category": req.category or "Geral",
            "params": req.params.dict(),
            "created_by_name": creator_name,
            "created_at": datetime.utcnow().isoformat()
        }

        self._data["presets"][preset_id] = preset_dict
        self._save()

        return TeamPresetResponse(
            id=preset_dict["id"],
            team_id=preset_dict["team_id"],
            name=preset_dict["name"],
            description=preset_dict["description"],
            category=preset_dict["category"],
            params=TeamPresetParams(**preset_dict["params"]),
            created_by_name=preset_dict["created_by_name"],
            created_at=preset_dict["created_at"]
        )


db_service = DatabaseService()
