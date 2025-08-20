from fastapi import status


def test_login_success(client, create_user):
    email = "john_doe@example.com"
    password = "topsecret123"
    create_user(email, password)

    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "access_token" in data and data["token_type"] == "bearer"


def test_login_invalid_credentials(client, create_user):
    email = "jane_doe@example.com"
    password = "secret123"
    create_user(email, password)

    resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
