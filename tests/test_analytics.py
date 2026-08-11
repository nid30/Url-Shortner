def test_analytics_reflects_click_count(client, auth_headers):
    shorten_resp = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
    )
    short_code = shorten_resp.json()["short_code"]

    client.get(f"/{short_code}")
    client.get(f"/{short_code}")
    client.get(f"/{short_code}")

    resp = client.get(f"/analytics/{short_code}")
    assert resp.status_code == 200
    assert resp.json()["total_clicks"] == 3


def test_analytics_404s_for_unknown_short_code(client):
    resp = client.get("/analytics/zzzzzz")
    assert resp.status_code == 404


def test_analytics_device_breakdown_reflects_user_agent(client, auth_headers):
    shorten_resp = client.post(
        "/shorten", json={"long_url": "https://example.com"}, headers=auth_headers
    )
    short_code = shorten_resp.json()["short_code"]

    client.get(
        f"/{short_code}",
        headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
        },
    )

    resp = client.get(f"/analytics/{short_code}")
    device_types = [row["device_type"] for row in resp.json()["device_breakdown"]]
    assert "mobile" in device_types