"""
Openingtimes Service.
Verarbeitet Öffnungszeiten aus Cache.
"""

from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS


class OpeningTime(BaseModel):
    """Öffnungszeit für einen Tag."""
    date: str
    start: Optional[str] = None
    end: Optional[str] = None


class OpeningTimesInfo(BaseModel):
    """Öffnungszeiten-Informationen."""
    today: Optional[OpeningTime] = None
    tomorrow: Optional[OpeningTime] = None
    next: Optional[OpeningTime] = None
    message: Optional[str] = None


async def get_opening_times() -> Optional[OpeningTimesInfo]:
    """Holt formatierte Öffnungszeiten."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["openingtimes"])
    
    if not data or "data" not in data:
        return None
    
    raw = data["data"]
    
    # Today
    today = None
    if raw.get("today"):
        today = OpeningTime(
            date=raw["today"].get("date", "")[:10],
            start=raw["today"].get("start"),
            end=raw["today"].get("end")
        )
    
    # Tomorrow
    tomorrow = None
    if raw.get("tomorrow"):
        tomorrow = OpeningTime(
            date=raw["tomorrow"].get("date", "")[:10],
            start=raw["tomorrow"].get("start"),
            end=raw["tomorrow"].get("end")
        )
    
    # Next opening
    next_open = None
    if raw.get("next"):
        next_open = OpeningTime(
            date=raw["next"].get("date", "")[:10],
            start=raw["next"].get("start"),
            end=raw["next"].get("end")
        )
    
    # Message
    message = None
    if raw.get("messages") and raw["messages"]:
        message = raw["messages"][0].get("short")
    
    return OpeningTimesInfo(
        today=today,
        tomorrow=tomorrow,
        next=next_open,
        message=message
    )
