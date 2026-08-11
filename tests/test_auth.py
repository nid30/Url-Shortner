def test_register_creates_user(client):
    resp = client.post(
        "/auth/register", json={"email": "a@b.com", "password": "password123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@b.com"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_is_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    resp = client.post(
        "/auth/register", json={"email": "a@b.com", "password": "password123"}
    )
    assert resp.status_code == 400


def test_login_with_correct_credentials_returns_token(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    resp = client.post(
        "/auth/login", data={"username": "a@b.com", "password": "password123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_is_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    resp = client.post(
        "/auth/login", data={"username": "a@b.com", "password": "wrongpassword"}
    )
    assert resp.status_code == 401


def test_login_with_unknown_email_is_rejected(client):
    resp = client.post(
        "/auth/login", data={"username": "nobody@nowhere.com", "password": "whatever"}
    )
    assert resp.status_code == 401