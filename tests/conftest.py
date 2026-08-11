"""
Fixtures shared across all test files.

Design choice: tests hit REAL Postgres and Redis (not mocks), pointed
at a separate test database (`shortener_test`) and a separate Redis
logical DB (index 1), configured via env vars in the `test` service in
docker-compose.yml. This is closer to production behavior than mocking
the DB layer, at the cost of needing real infra to run tests — which
is exactly why we run them through docker-compose rather than bare
`pytest` on a laptop with nothing else running.
"""

import psycopg2
from psycopg2 import errors as pg_errors
from sqlalchemy import text
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.database import engine, DATABASE_URL
from app.redis_client import redis_client
from app.main import app  # noqa: F401 — importing registers all models on SQLModel.metadata


def _ensure_test_database_exists() -> None:
    """
    The Postgres container only auto-creates the `shortener` database
    (via POSTGRES_DB). `shortener_test` doesn't exist until we create
    it — so connect to the default `postgres` maintenance DB and create
    it if missing. Safe to run every time: catches the "already exists"
    error and moves on.
    """
    base_url, _, dbname = DATABASE_URL.rpartition("/")
    maintenance_url = f"{base_url}/postgres"

    conn = psycopg2.connect(maintenance_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(f'CREATE DATABASE "{dbname}"')
    except pg_errors.DuplicateDatabase:
        pass
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    _ensure_test_database_exists()
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture(autouse=True)
def clean_state():
    """Runs before EVERY test: wipes all tables and flushes the test
    Redis DB, so each test starts from a known-empty state."""
    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE TABLE click_events, urls, users RESTART IDENTITY CASCADE")
        )
    redis_client.flushdb()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Registers and logs in a fresh test user, returns ready-to-use auth headers."""
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}