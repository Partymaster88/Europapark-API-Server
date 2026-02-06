"""
Shows Service.
Verarbeitet und formatiert Show-Informationen aus POI-Daten.
"""

import logging
from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS
from services.showtimes import get_showtime_by_id, ShowTimeEntry

logger = logging.getLogger(__name__)


class Location(BaseModel):
    """Standort."""
    latitude: float
    longitude: float


class ImageUrls(BaseModel):
    """Bild-URLs."""
    small: Optional[str] = None
    medium: Optional[str] = None


class ShowInfo(BaseModel):
    """Vollständige Show-Informationen."""
    id: int
    name: str
    description: Optional[str] = None
    location_name: Optional[str] = None
    location: Optional[Location] = None
    duration: Optional[int] = None
    image: Optional[ImageUrls] = None
    icon: Optional[str] = None
    showtimes: Optional[ShowTimeEntry] = None


def extract_image_urls(image_data: Optional[dict]) -> Optional[ImageUrls]:
    """Extrahiert Bild-URLs aus den POI-Daten."""
    if not image_data:
        return None
    
    return ImageUrls(
        small=image_data.get("small"),
        medium=image_data.get("medium")
    )


async def get_all_shows_from_pois() -> list[dict]:
    """
    Holt alle Shows aus den POI-Daten (showlocation -> shows).
    Gibt Liste von (show, location_poi) Tupeln zurück.
    """
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return []
    
    shows = []
    for poi in pois_data["data"].get("pois", []):
        scopes = poi.get("scopes", [])
        
        # Nur Europapark (keine Rulantica)
        if "europapark" not in scopes:
            continue
        
        # Shows aus showlocation extrahieren
        for show in poi.get("shows", []):
            shows.append({
                "show": show,
                "location_poi": poi
            })
    
    return shows


async def get_show_by_id(show_id: int) -> Optional[dict]:
    """Holt Show-Rohdaten anhand der ID."""
    all_shows = await get_all_shows_from_pois()
    
    for item in all_shows:
        if item["show"].get("id") == show_id:
            return item
    
    return None


async def get_show_info(show_id: int) -> Optional[ShowInfo]:
    """
    Holt formatierte Show-Informationen.
    """
    item = await get_show_by_id(show_id)
    
    if not item:
        return None
    
    show = item["show"]
    location_poi = item["location_poi"]
    
    # Showzeiten holen
    showtimes = await get_showtime_by_id(show_id)
    
    # Location
    location = None
    if location_poi.get("latitude") and location_poi.get("longitude"):
        location = Location(
            latitude=location_poi["latitude"],
            longitude=location_poi["longitude"]
        )
    
    # Bild und Icon
    image = extract_image_urls(show.get("image"))
    icon = show.get("icon", {}).get("small") if show.get("icon") else None
    
    return ShowInfo(
        id=show["id"],
        name=show.get("name", "Unbekannt"),
        description=show.get("excerpt"),
        location_name=location_poi.get("name"),
        location=location,
        duration=show.get("duration"),
        image=image,
        icon=icon,
        showtimes=showtimes
    )


async def get_all_shows() -> list[ShowInfo]:
    """Holt alle Shows mit Basisinfos."""
    all_shows = await get_all_shows_from_pois()
    
    results = []
    for item in all_shows:
        show = item["show"]
        location_poi = item["location_poi"]
        
        # Showzeiten holen
        showtimes = await get_showtime_by_id(show["id"])
        
        # Location
        location = None
        if location_poi.get("latitude") and location_poi.get("longitude"):
            location = Location(
                latitude=location_poi["latitude"],
                longitude=location_poi["longitude"]
            )
        
        results.append(ShowInfo(
            id=show["id"],
            name=show.get("name", "Unbekannt"),
            description=show.get("excerpt"),
            location_name=location_poi.get("name"),
            location=location,
            duration=show.get("duration"),
            image=extract_image_urls(show.get("image")),
            icon=show.get("icon", {}).get("small") if show.get("icon") else None,
            showtimes=showtimes
        ))
    
    return results
