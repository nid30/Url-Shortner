from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class URL(SQLModel, table=True):
    __tablename__ = "urls"

    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, unique=True)
    long_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)


class ClickEvent(SQLModel, table=True):
    __tablename__ = "click_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    url_id: int = Field(foreign_key="urls.id", index=True)
    clicked_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None