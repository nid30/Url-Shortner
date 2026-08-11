from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    long_url: HttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime


class AnalyticsResponse(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int
    clicks_by_day: list[dict]
    top_referrers: list[dict]
    device_breakdown: list[dict]
    browser_breakdown: list[dict]


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"