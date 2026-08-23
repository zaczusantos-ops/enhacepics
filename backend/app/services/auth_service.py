"""
ChurchPhoto Pro - Authentication Service (Smart Universal Email & JWT)
"""

import os
import json
import time
import hmac
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from ..config import settings
from ..schemas.auth import UserProfile, AuthResponse, GoogleLoginRequest, EmailLoginRequest, EmailRegisterRequest

USERS_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "users.json"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + padding).encode("utf-8"))


class AuthService:
    """
    Handles seamless user authentication, password hashing, and session management.
    """

    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._load_users()

    def _load_users(self):
        try:
            if USERS_DB_PATH.exists():
                with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
                    self._users = json.load(f)
        except Exception as e:
            print(f"[AuthService] Error loading users db: {e}")
            self._users = {}

    def _save_users(self):
        try:
            USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self._users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AuthService] Error saving users db: {e}")

    def _hash_password(self, password: str, salt: str = "church_salt_2026") -> str:
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def create_jwt_token(self, user_data: Dict[str, Any]) -> str:
        now = int(time.time())
        expire = now + (settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS * 86400)
        
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data.get("role", "volunteer"),
            "iat": now,
            "exp": expire,
        }

        header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
        payload_b64 = _b64url_encode(json.dumps(payload).encode("utf-8"))
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        
        signature = hmac.new(settings.JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        sig_b64 = _b64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_sig = hmac.new(settings.JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
            expected_sig_b64 = _b64url_encode(expected_sig)

            if not hmac.compare_digest(sig_b64, expected_sig_b64):
                return None

            payload_json = _b64url_decode(payload_b64).decode("utf-8")
            payload = json.loads(payload_json)

            if payload.get("exp", 0) < int(time.time()):
                return None

            return payload
        except Exception:
            return None

    def register_email(self, request: EmailRegisterRequest) -> AuthResponse:
        email_clean = request.email.strip().lower()
        
        for u in self._users.values():
            if u.get("email", "").lower() == email_clean:
                # If already exists, log in
                token = self.create_jwt_token(u)
                profile = UserProfile(
                    id=u["id"],
                    email=u["email"],
                    name=u["name"],
                    picture=u.get("picture"),
                    provider="email",
                    church_name=u.get("church_name", "Igreja Local"),
                    role=u.get("role", "volunteer"),
                    created_at=u["created_at"],
                    photos_processed_count=u.get("photos_processed_count", 0),
                )
                return AuthResponse(
                    success=True,
                    token=token,
                    user=profile,
                    message=f"Bem-vindo(a), {profile.name}!"
                )

        user_id = f"usr_{hashlib.md5(email_clean.encode()).hexdigest()[:12]}"
        password_hash = self._hash_password(request.password)
        name_clean = request.name.strip() if request.name else email_clean.split("@")[0].capitalize()
        picture = f"https://api.dicebear.com/7.x/initials/svg?seed={name_clean}&backgroundColor=2563eb"

        user = {
            "id": user_id,
            "email": email_clean,
            "name": name_clean,
            "password_hash": password_hash,
            "picture": picture,
            "provider": "email",
            "church_name": request.church_name or "Igreja Local",
            "role": "volunteer",
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat(),
            "photos_processed_count": 0,
        }

        self._users[user_id] = user
        self._save_users()

        token = self.create_jwt_token(user)
        profile = UserProfile(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
            provider="email",
            church_name=user.get("church_name", "Igreja Local"),
            role=user.get("role", "volunteer"),
            created_at=user["created_at"],
            photos_processed_count=0,
        )

        return AuthResponse(
            success=True,
            token=token,
            user=profile,
            message="Conta criada com sucesso!"
        )

    def login_email(self, request: EmailLoginRequest) -> AuthResponse:
        email_clean = request.email.strip().lower()
        pwd_hash = self._hash_password(request.password)

        target_user = None
        for u in self._users.values():
            if u.get("email", "").lower() == email_clean:
                target_user = u
                break

        # Auto-create user seamlessly on first login if not registered yet
        if not target_user:
            default_name = email_clean.split("@")[0].capitalize()
            return self.register_email(EmailRegisterRequest(
                email=email_clean,
                password=request.password,
                name=f"{default_name} (Mídia)",
                church_name="Igreja Local"
            ))

        # If user exists, check password
        if target_user.get("password_hash") != pwd_hash:
            raise ValueError("Senha incorreta para este e-mail.")

        target_user["last_login"] = datetime.utcnow().isoformat()
        self._save_users()

        token = self.create_jwt_token(target_user)
        profile = UserProfile(
            id=target_user["id"],
            email=target_user["email"],
            name=target_user["name"],
            picture=target_user.get("picture"),
            provider="email",
            church_name=target_user.get("church_name", "Igreja Local"),
            role=target_user.get("role", "volunteer"),
            created_at=target_user["created_at"],
            photos_processed_count=target_user.get("photos_processed_count", 0),
        )

        return AuthResponse(
            success=True,
            token=token,
            user=profile,
            message=f"Bem-vindo(a) de volta, {profile.name}!"
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        if user_id in self._users:
            u = self._users[user_id]
            return UserProfile(
                id=u["id"],
                email=u["email"],
                name=u["name"],
                picture=u.get("picture"),
                provider=u.get("provider", "email"),
                church_name=u.get("church_name", "Igreja Local"),
                role=u.get("role", "volunteer"),
                created_at=u["created_at"],
                photos_processed_count=u.get("photos_processed_count", 0),
            )
        return None

    def increment_processed_count(self, user_id: str):
        if user_id in self._users:
            self._users[user_id]["photos_processed_count"] = self._users[user_id].get("photos_processed_count", 0) + 1
            self._save_users()


auth_service = AuthService()
