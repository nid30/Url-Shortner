def test_shorten_requires_authentication(client):
    resp = client.post("/shorten", json={"long_url": "https://example.com"})
    assert resp.status_code == 401


def test_shorten_returns_a_short_code(client, auth_headers):
    resp = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["short_code"]
    assert body["short_url"].endswith(body["short_code"])


def test_redirect_sends_visitor_to_the_long_url(client, auth_headers):
    shorten_resp = client.post(
        "/shorten",
        json={"long_url": "https://example.com/some/page"},
        headers=auth_headers,
    )
    short_code = shorten_resp.json()["short_code"]

    redirect_resp = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://example.com/some/page"


def test_redirect_404s_for_a_code_that_was_never_issued(client):
    resp = client.get("/zzzzzz")
    assert resp.status_code == 404


def test_second_visit_is_served_from_cache(client, auth_headers):
    shorten_resp = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
    )
    short_code = shorten_resp.json()["short_code"]

    first = client.get(f"/{short_code}", follow_redirects=False)
    second = client.get(f"/{short_code}", follow_redirects=False)

    assert first.status_code == second.status_code == 302
    assert first.headers["location"] == second.headers["location"]


def test_rate_limit_blocks_after_max_requests_per_window(client, auth_headers):
    for _ in range(10):
        resp = client.post(
            "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
        )
        assert resp.status_code == 200

    eleventh = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
    )
    assert eleventh.status_code == 429
    assert "Retry-After" in eleventh.headers


def test_rate_limit_is_scoped_per_user(client):
    def register_and_login(email):
        client.post("/auth/register", json={"email": email, "password": "password123"})
        resp = client.post(
            "/auth/login", data={"username": email, "password": "password123"}
        )
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    user_a_headers = register_and_login("user_a@example.com")
    user_b_headers = register_and_login("user_b@example.com")

    for _ in range(10):
        resp = client.post(
            "/shorten", json={"long_url": "https://example.com"}, headers=user_a_headers
        )
        assert resp.status_code == 200

    blocked = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=user_a_headers
    )
    assert blocked.status_code == 429

    still_ok = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=user_b_headers
    )
    assert still_ok.status_code == 200