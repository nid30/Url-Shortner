"""
Password hashing (bcrypt via passlib) and JWT creation/verification
(python-jose). Kept together since both are "auth primitives" with no
DB or request dependencies of their own — pure functions, easy to unit
test in isolation.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# In a real deployment this MUST come from an env var / secrets
# manager, never hardcoded. The fallback here exists only so the app
# doesn't crash on a fresh local clone before you've set up .env.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours — fine for a portfolio project

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """`subject` is typically the user's id (as a string) — this is
    what ends up in the token's `sub` claim and what we'll pull back
    out to identify the user on every authenticated request."""
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Returns the user id (as a string) if the token is valid, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None