"""
Unit tests for Authentication (Google OAuth & JWT & Email/Password)
"""

import json
import base64
from backend.app.schemas.auth import (
    GoogleLoginRequest,
    EmailLoginRequest,
    EmailRegisterRequest,
    UserProfile,
    AuthResponse
)
from backend.app.services.auth_service import AuthService, _b64url_encode


def test_auth_jwt_flow():
    auth = AuthService()
    user_data = {
        "id": "usr_test_123",
        "email": "pastor@igreja.org",
        "name": "Pastor Claudio",
        "role": "leader"
    }

    token = auth.create_jwt_token(user_data)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = auth.verify_jwt_token(token)
    assert payload is not None
    assert payload["sub"] == "usr_test_123"
    assert payload["email"] == "pastor@igreja.org"
    assert payload["name"] == "Pastor Claudio"
    assert payload["role"] == "leader"


def test_email_registration_and_login():
    auth = AuthService()
    reg_req = EmailRegisterRequest(
        email="midia_central@igreja.org",
        password="secretpassword123",
        name="Equipe Mídia",
        church_name="Igreja Batista Central"
    )

    reg_resp = auth.register_email(reg_req)
    assert reg_resp.success is True
    assert reg_resp.user.email == "midia_central@igreja.org"
    assert reg_resp.user.name == "Equipe Mídia"
    assert reg_resp.user.church_name == "Igreja Batista Central"

    # Test login with valid credentials
    login_req = EmailLoginRequest(
        email="midia_central@igreja.org",
        password="secretpassword123"
    )
    login_resp = auth.login_email(login_req)
    assert login_resp.success is True
    assert login_resp.user.id == reg_resp.user.id


def test_google_credential_auth():
    auth = AuthService()
    
    # Generate mock Google ID token JWT
    mock_header = {"alg": "RS256", "kid": "mock_key_id", "typ": "JWT"}
    mock_payload = {
        "iss": "https://accounts.google.com",
        "sub": "109876543210987654321",
        "email": "voluntario.midia@gmail.com",
        "name": "Voluntário de Louvor",
        "picture": "https://lh3.googleusercontent.com/a/mock_photo",
        "email_verified": True,
        "iat": 1700000000,
        "exp": 1800000000
    }
    
    h_b64 = _b64url_encode(json.dumps(mock_header).encode())
    p_b64 = _b64url_encode(json.dumps(mock_payload).encode())
    mock_google_jwt = f"{h_b64}.{p_b64}.mock_signature"

    req = GoogleLoginRequest(credential=mock_google_jwt)
    resp = auth.authenticate_google(req)

    assert resp.success is True
    assert resp.user.email == "voluntario.midia@gmail.com"
    assert resp.user.name == "Voluntário de Louvor"
    assert resp.user.picture == "https://lh3.googleusercontent.com/a/mock_photo"
    assert resp.user.provider == "google"
    print("Authentication tests passed successfully!")


if __name__ == "__main__":
    test_auth_jwt_flow()
    test_email_registration_and_login()
    test_google_credential_auth()
    print("All Auth tests passed 100%!")
