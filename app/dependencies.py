from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.auth import decode_access_token
from app.database import get_session
from app.models import User

# tokenUrl just tells FastAPI's auto-docs (/docs) where to send a
# "try it out" login request — it doesn't affect actual token
# validation, which happens below in decode_access_token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error

    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_error

    return user