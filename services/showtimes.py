"""
Showtimes Service.
Verarbeitet Showzeiten und verknüpft sie mit POI-Daten.
"""

import logging
from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS

logger = logging.getLogger(__name__)


class Location(BaseModel):
    """Standort."""
    latitude: float
    longitude: float


class ShowTimeEntry(BaseModel):
    """Showzeit-Eintrag."""
    id: int
    name: str
    location: Optional[Location] = None
    times_today: list[str]
    times_tomorrow: list[str]


async def get_show_info_map() -> dict[int, dict]:
    """
    Erstellt ein Mapping von Show-ID zu Show-Informationen aus POI-Daten.
    Shows sind unter showlocation POIs verschachtelt.
    """
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return {}
    
    show_map = {}
    for poi in pois_data["data"].get("pois", []):
        scopes = poi.get("scopes", [])
        
        # Nur Europapark (keine Rulantica)
        if "europapark" not in scopes:
            continue
        
        # Shows aus showlocation extrahieren
        shows = poi.get("shows", [])
        for show in shows:
            show_id = show.get("id")
            if show_id:
                show_map[show_id] = {
                    "name": show.get("name", "Unbekannt"),
                    "latitude": poi.get("latitude"),
                    "longitude": poi.get("longitude"),
                }
    
    return show_map


async def get_processed_showtimes() -> list[ShowTimeEntry]:
    """
    Holt verarbeitete Showzeiten mit Namen und Location.
    """
    cache = get_cache_service()
    
    # Showzeiten laden
    showtimes_data = await cache.load(CACHE_KEYS["showtimes"])
    if not showtimes_data or "data" not in showtimes_data:
        return []
    
    # Show-Info-Mapping laden
    show_map = await get_show_info_map()
    
    results = []
    for entry in showtimes_data["data"]:
        show_id = entry.get("showId")
        
        # Show-Info holen
        show_info = show_map.get(show_id)
        if not show_info:
            continue
        
        # Location
        location = None
        if show_info.get("latitude") and show_info.get("longitude"):
            location = Location(
                latitude=show_info["latitude"],
                longitude=show_info["longitude"]
            )
        
        results.append(ShowTimeEntry(
            id=show_id,
            name=show_info["name"],
            location=location,
            times_today=entry.get("today", []),
            times_tomorrow=entry.get("tomorrow", [])
        ))
    
    return results


async def get_showtime_by_id(show_id: int) -> Optional[ShowTimeEntry]:
    """
    Holt Showzeiten für eine bestimmte Show.
    """
    showtimes = await get_processed_showtimes()
    
    for entry in showtimes:
        if entry.id == show_id:
            return entry
    
    return None
