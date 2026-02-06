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
    
    def extract_time(dt_str: str | None) -> str | None:
        """Extrahiert nur die Uhrzeit aus ISO-String."""
        if not dt_str:
            return None
        try:
            return dt_str[11:16]  # HH:MM
        except (IndexError, TypeError):
            return None
    
    # Today
    today = None
    if raw.get("today"):
        today = OpeningTime(
            date=raw["today"].get("date", "")[:10],
            start=extract_time(raw["today"].get("start")),
            end=extract_time(raw["today"].get("end"))
        )
    
    # Tomorrow
    tomorrow = None
    if raw.get("tomorrow"):
        tomorrow = OpeningTime(
            date=raw["tomorrow"].get("date", "")[:10],
            start=extract_time(raw["tomorrow"].get("start")),
            end=extract_time(raw["tomorrow"].get("end"))
        )
    
    # Next opening
    next_open = None
    if raw.get("next"):
        next_open = OpeningTime(
            date=raw["next"].get("date", "")[:10],
            start=extract_time(raw["next"].get("start")),
            end=extract_time(raw["next"].get("end"))
        )
    
    # Message (long)
    message = None
    if raw.get("messages") and raw["messages"]:
        message = raw["messages"][0].get("long")
    
    return OpeningTimesInfo(
        today=today,
        tomorrow=tomorrow,
        next=next_open,
        message=message
    )
