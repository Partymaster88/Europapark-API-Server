"""
Seasons Service.
Verarbeitet Saison-Daten aus Cache (nur Europapark).
"""

from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS


class SeasonInfo(BaseModel):
    """Saison-Informationen."""
    id: int
    name: str
    theme: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None


async def get_seasons() -> list[SeasonInfo]:
    """Holt alle Europapark-Saisons."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["seasons"])
    
    if not data or "data" not in data:
        return []
    
    results = []
    for season in data["data"]:
        scopes = season.get("scopes", [])
        
        # Nur Europapark
        if "europapark" not in scopes:
            continue
        
        # Start/End aus excerpt extrahieren oder aus Feldern
        start = season.get("startAt")
        end = season.get("endAt")
        
        results.append(SeasonInfo(
            id=season["id"],
            name=season.get("name", "Unbekannt"),
            theme=season.get("theme"),
            description=season.get("excerpt"),
            start=start[:10] if start else None,
            end=end[:10] if end else None
        ))
    
    return results
