from datetime import timedelta

import jwt

from app import security


def register_user(client, username="tokenuser", password="password123"):
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200


def login_user(client, username="tokenuser", password="password123"):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response


def set_refresh_cookie(client, token):
    client.cookies.clear()
    client.cookies.set("refresh_token", token, domain="testserver.local", path="/auth")


def test_login_returns_access_token_and_sets_refresh_cookie(client):
    register_user(client)

    response = login_user(client)

    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert response.cookies.get("refresh_token")
    assert "HttpOnly" in response.headers["set-cookie"]


def test_refresh_rotates_refresh_token_and_revokes_old_token(client):
    register_user(client)
    old_refresh_token = login_user(client).cookies.get("refresh_token")

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"]
    new_refresh_token = response.cookies.get("refresh_token")
    assert new_refresh_token
    assert new_refresh_token != old_refresh_token

    set_refresh_cookie(client, old_refresh_token)
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token reuse detected"


def test_reused_refresh_token_revokes_all_active_refresh_tokens_for_user(client):
    register_user(client)
    first_refresh_token = login_user(client).cookies.get("refresh_token")
    second_refresh_token = login_user(client).cookies.get("refresh_token")

    set_refresh_cookie(client, first_refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 200

    set_refresh_cookie(client, first_refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token reuse detected"

    set_refresh_cookie(client, second_refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token reuse detected"


def test_access_token_is_not_accepted_as_refresh_token(client):
    register_user(client)
    access_token = login_user(client).json()["access_token"]

    set_refresh_cookie(client, access_token)
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


def test_refresh_token_is_not_accepted_for_protected_routes(client):
    register_user(client)
    refresh_token = login_user(client).cookies.get("refresh_token")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


def test_expired_access_token_is_rejected(client):
    register_user(client)
    expired_token = jwt.encode(
        {
            "sub": "1",
            "type": "access",
            "exp": security.utc_now() - timedelta(minutes=1),
        },
        security.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


def test_expired_refresh_token_is_rejected(client):
    register_user(client)
    expired_token = jwt.encode(
        {
            "sub": "1",
            "jti": "expired-refresh-token",
            "type": "refresh",
            "iat": security.utc_now() - timedelta(days=2),
            "exp": security.utc_now() - timedelta(days=1),
        },
        security.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )

    set_refresh_cookie(client, expired_token)
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"
