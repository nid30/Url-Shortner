from fastapi import FastAPI

from app.database import init_db
from app.routers import shorten, analytics, auth

app = FastAPI(title="URL Shortener", version="0.1.0")

app.include_router(auth.router)
app.include_router(shorten.router)
app.include_router(analytics.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}