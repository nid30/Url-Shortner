"""
Runs as a FastAPI BackgroundTask, which executes *after* the redirect
response has already been sent to the browser. That's the whole point:
the user isn't kept waiting on an analytics write.

Important detail: the request's own DB session (from the `get_session`
dependency) is already closed by the time this runs, since dependency
cleanup happens before the response finishes sending. So this function
opens its own short-lived session rather than reusing the request's.
"""

from sqlmodel import Session

from app.database import engine
from app.models import ClickEvent
from app.services.user_agent import parse_device_and_browser


def log_click(
    url_id: int,
    referrer: str | None,
    user_agent: str | None,
    ip_address: str | None,
) -> None:
    device_type, browser = parse_device_and_browser(user_agent)

    click = ClickEvent(
        url_id=url_id,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address,
        device_type=device_type,
        browser=browser,
    )

    with Session(engine) as session:
        session.add(click)
        session.commit()