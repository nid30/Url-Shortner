from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import URL
from app.schemas import AnalyticsResponse
from app.services import analytics

router = APIRouter()


@router.get("/analytics/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str, session: Session = Depends(get_session)):
    url_entry = session.exec(select(URL).where(URL.short_code == short_code)).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return AnalyticsResponse(
        short_code=url_entry.short_code,
        long_url=url_entry.long_url,
        total_clicks=analytics.get_total_clicks(session, url_entry.id),
        clicks_by_day=analytics.get_clicks_by_day(session, url_entry.id),
        top_referrers=analytics.get_top_referrers(session, url_entry.id),
        device_breakdown=analytics.get_device_breakdown(session, url_entry.id),
        browser_breakdown=analytics.get_browser_breakdown(session, url_entry.id),
    )