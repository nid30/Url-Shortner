from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.models import URL, User
from app.schemas import ShortenRequest, ShortenResponse
from app.services.encoding import encode, decode
from app.services.click_logger import log_click
from app.services.rate_limiter import check_rate_limit
from app.redis_client import redis_client, CACHE_TTL_SECONDS

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(
    payload: ShortenRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    check_rate_limit(current_user.id)

    url_entry = URL(
        short_code="pending",
        long_url=str(payload.long_url),
        user_id=current_user.id,
    )
    session.add(url_entry)
    session.commit()
    session.refresh(url_entry)

    url_entry.short_code = encode(url_entry.id)
    session.add(url_entry)
    session.commit()
    session.refresh(url_entry)

    return ShortenResponse(
        short_code=url_entry.short_code,
        short_url=f"http://localhost:8000/{url_entry.short_code}",
        long_url=url_entry.long_url,
        created_at=url_entry.created_at,
    )


@router.get("/{short_code}")
def redirect_to_long_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    url_id = decode(short_code)

    def queue_click_log():
        background_tasks.add_task(
            log_click,
            url_id=url_id,
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )

    cached_url = redis_client.get(f"url:{short_code}")
    if cached_url:
        queue_click_log()
        return RedirectResponse(url=cached_url, status_code=302)

    url_entry = session.exec(
        select(URL).where(URL.short_code == short_code)
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    redis_client.setex(f"url:{short_code}", CACHE_TTL_SECONDS, url_entry.long_url)

    queue_click_log()
    return RedirectResponse(url=url_entry.long_url, status_code=302)