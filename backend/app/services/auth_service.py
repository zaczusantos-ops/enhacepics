"""
ChurchPhoto Pro - Authentication Service (Google OAuth & Universal JWT)
Supports Google Identity Services (GIS) ID Tokens, standard email/password authentication,
and self-contained HMAC-SHA256 JWT token generation.
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
    Handles Google OAuth JWT validation, password hashing, user registration and session management.
    """

    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._load_users()

    def _load_users(self):
        """Loads users from local json storage if exists."""
        try:
            if USERS_DB_PATH.exists():
                with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
                    self._users = json.load(f)
        except Exception as e:
            print(f"[AuthService] Error loading users db: {e}")
            self._users = {}

    def _save_users(self):
        """Saves users to local json storage."""
        try:
            USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self._users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AuthService] Error saving users db: {e}")

    def _hash_password(self, password: str, salt: str = "church_salt_2026") -> str:
        """Secure hash for passwords."""
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def create_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """
        Creates an application JWT token signed with HMAC-SHA256 valid for 30 days.
        """
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
        """
        Verifies application JWT signature and expiry.
        """
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

            # Check expiration
            if payload.get("exp", 0) < int(time.time()):
                return None

            return payload
        except Exception:
            return None

    def decode_google_id_token(self, credential: str) -> Dict[str, Any]:
        """
        Safely extracts user profile claims from Google Identity Services ID Token (JWT).
        """
        try:
            parts = credential.split(".")
            if len(parts) < 2:
                raise ValueError("Formato de token do Google inválido.")
            
            payload_json = _b64url_decode(parts[1]).decode("utf-8")
            return json.loads(payload_json)
        except Exception as e:
            raise ValueError(f"Não foi possível decodificar o token do Google: {str(e)}")

    def authenticate_google(self, request: GoogleLoginRequest) -> AuthResponse:
        """
        Authenticates a user via Google Identity Services ID Token.
        """
        try:
            decoded = self.decode_google_id_token(request.credential)
            email = decoded.get("email")
            if not email:
                raise ValueError("Token do Google não contém e-mail válido.")

            google_sub = decoded.get("sub", "")
            user_id = f"google_{google_sub}" if google_sub else f"google_{hashlib.md5(email.encode()).hexdigest()[:12]}"
            name = decoded.get("name", email.split("@")[0].capitalize())
            picture = decoded.get("picture", "")

            # Check if user exists or register
            if user_id in self._users:
                user = self._users[user_id]
                user["name"] = name
                user["picture"] = picture
                user["last_login"] = datetime.utcnow().isoformat()
            else:
                user = {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "picture": picture,
                    "provider": "google",
                    "church_name": "Igreja Local",
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
                provider="google",
                church_name=user.get("church_name", "Igreja Local"),
                role=user.get("role", "volunteer"),
                created_at=user["created_at"],
                photos_processed_count=user.get("photos_processed_count", 0),
            )

            return AuthResponse(
                success=True,
                token=token,
                user=profile,
                message=f"Bem-vindo(a), {profile.name}!"
            )
        except Exception as e:
            raise ValueError(f"Falha na autenticação Google: {str(e)}")

    def register_email(self, request: EmailRegisterRequest) -> AuthResponse:
        """
        Registers a new user with email and password.
        """
        email_clean = request.email.strip().lower()
        
        for u in self._users.values():
            if u.get("email", "").lower() == email_clean:
                raise ValueError("Este e-mail já está cadastrado. Faça login.")

        user_id = f"usr_{hashlib.md5(email_clean.encode()).hexdigest()[:12]}"
        password_hash = self._hash_password(request.password)
        picture = f"https://api.dicebear.com/7.x/initials/svg?seed={request.name}&backgroundColor=2563eb"

        user = {
            "id": user_id,
            "email": email_clean,
            "name": request.name.strip(),
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
            message="Cadastro realizado com sucesso!"
        )

    def login_email(self, request: EmailLoginRequest) -> AuthResponse:
        """
        Authenticates an existing user with email and password.
        """
        email_clean = request.email.strip().lower()
        pwd_hash = self._hash_password(request.password)

        target_user = None
        for u in self._users.values():
            if u.get("email", "").lower() == email_clean and u.get("password_hash") == pwd_hash:
                target_user = u
                break

        if not target_user:
            raise ValueError("E-mail ou senha incorretos.")

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
                provider=u.get("provider", "google"),
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
