"""
Aggregation queries for the analytics endpoint.

Deliberately doing all aggregation in SQL (GROUP BY, COUNT, date
truncation) rather than pulling every ClickEvent row into Python and
summing there. For a table that could have millions of rows, the
difference is: the DB does one efficient pass with an index vs. your
app server pulling gigabytes over the wire to count them. This is a
detail worth explicitly mentioning in an interview.
"""

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import ClickEvent


def get_total_clicks(session: Session, url_id: int) -> int:
    statement = select(func.count(ClickEvent.id)).where(ClickEvent.url_id == url_id)
    return session.exec(statement).one()


def get_clicks_by_day(session: Session, url_id: int) -> list[dict]:
    day = func.date(ClickEvent.clicked_at)
    statement = (
        select(day.label("day"), func.count(ClickEvent.id).label("clicks"))
        .where(ClickEvent.url_id == url_id)
        .group_by(day)
        .order_by(day)
    )
    rows = session.exec(statement).all()
    return [{"day": str(row.day), "clicks": row.clicks} for row in rows]


def get_top_referrers(session: Session, url_id: int, limit: int = 5) -> list[dict]:
    statement = (
        select(
            ClickEvent.referrer,
            func.count(ClickEvent.id).label("clicks"),
        )
        .where(ClickEvent.url_id == url_id)
        .group_by(ClickEvent.referrer)
        .order_by(func.count(ClickEvent.id).desc())
        .limit(limit)
    )
    rows = session.exec(statement).all()
    return [
        {"referrer": row.referrer or "direct", "clicks": row.clicks} for row in rows
    ]


def get_device_breakdown(session: Session, url_id: int) -> list[dict]:
    statement = (
        select(ClickEvent.device_type, func.count(ClickEvent.id).label("clicks"))
        .where(ClickEvent.url_id == url_id)
        .group_by(ClickEvent.device_type)
        .order_by(func.count(ClickEvent.id).desc())
    )
    rows = session.exec(statement).all()
    return [{"device_type": row.device_type, "clicks": row.clicks} for row in rows]


def get_browser_breakdown(session: Session, url_id: int) -> list[dict]:
    statement = (
        select(ClickEvent.browser, func.count(ClickEvent.id).label("clicks"))
        .where(ClickEvent.url_id == url_id)
        .group_by(ClickEvent.browser)
        .order_by(func.count(ClickEvent.id).desc())
    )
    rows = session.exec(statement).all()
    return [{"browser": row.browser, "clicks": row.clicks} for row in rows]