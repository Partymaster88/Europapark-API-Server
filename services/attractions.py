"""
Attractions Service.
Verarbeitet und formatiert Attraktionsinformationen aus POI-Daten.
"""

import logging
from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS
from services.waittimes import get_waittime_by_id, WaitTimeEntry

logger = logging.getLogger(__name__)


class Location(BaseModel):
    """Standort einer Attraktion."""
    latitude: float
    longitude: float


class HeightRequirements(BaseModel):
    """Größenanforderungen."""
    min_height: Optional[int] = None
    min_height_with_adult: Optional[int] = None
    max_height: Optional[int] = None


class AgeRequirements(BaseModel):
    """Altersanforderungen."""
    min_age: Optional[int] = None
    min_age_with_adult: Optional[int] = None
    max_age: Optional[int] = None


class StressLevel(BaseModel):
    """Belastungslevel."""
    speed: Optional[int] = None
    spin: Optional[int] = None
    swing: Optional[int] = None
    height: Optional[int] = None
    water: Optional[int] = None
    darkness: Optional[int] = None


class ImageUrls(BaseModel):
    """Bild-URLs in verschiedenen Größen."""
    small: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None
    original: Optional[str] = None


class AttractionInfo(BaseModel):
    """Vollständige Attraktionsinformationen."""
    id: int
    code: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: str
    area_id: Optional[int] = None
    location: Optional[Location] = None
    height_requirements: Optional[HeightRequirements] = None
    age_requirements: Optional[AgeRequirements] = None
    stress_levels: Optional[StressLevel] = None
    image: Optional[ImageUrls] = None
    wait_time: Optional[WaitTimeEntry] = None


async def get_poi_by_id(attraction_id: int) -> Optional[dict]:
    """Holt POI-Rohdaten anhand der ID."""
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return None
    
    for poi in pois_data["data"].get("pois", []):
        if poi.get("id") == attraction_id:
            return poi
    
    return None


def extract_image_urls(image_data: Optional[dict]) -> Optional[ImageUrls]:
    """Extrahiert Bild-URLs aus den POI-Daten."""
    if not image_data:
        return None
    
    return ImageUrls(
        small=image_data.get("small"),
        medium=image_data.get("medium"),
        large=image_data.get("large"),
        original=image_data.get("reference")
    )


def extract_stress_levels(stress_data: Optional[dict]) -> Optional[StressLevel]:
    """Extrahiert Belastungslevel aus den POI-Daten."""
    if not stress_data:
        return None
    
    return StressLevel(
        speed=stress_data.get("speed"),
        spin=stress_data.get("spin"),
        swing=stress_data.get("swing"),
        height=stress_data.get("height"),
        water=stress_data.get("water"),
        darkness=stress_data.get("darkness")
    )


async def get_attraction_info(attraction_id: int) -> Optional[AttractionInfo]:
    """
    Holt formatierte Attraktionsinformationen.
    """
    poi = await get_poi_by_id(attraction_id)
    
    if not poi:
        return None
    
    # Wartezeit aus Cache holen
    wait_time = await get_waittime_by_id(attraction_id)
    
    # Location extrahieren
    location = None
    if poi.get("latitude") and poi.get("longitude"):
        location = Location(
            latitude=poi["latitude"],
            longitude=poi["longitude"]
        )
    
    # Größenanforderungen
    height_req = None
    if any([poi.get("minHeight"), poi.get("minHeightAdult"), poi.get("maxHeight")]):
        height_req = HeightRequirements(
            min_height=poi.get("minHeight"),
            min_height_with_adult=poi.get("minHeightAdult"),
            max_height=poi.get("maxHeight")
        )
    
    # Altersanforderungen
    age_req = None
    if any([poi.get("minAge"), poi.get("minAgeAdult"), poi.get("maxAge")]):
        age_req = AgeRequirements(
            min_age=poi.get("minAge") if poi.get("minAge", 0) > 0 else None,
            min_age_with_adult=poi.get("minAgeAdult"),
            max_age=poi.get("maxAge") if poi.get("maxAge", 0) > 0 else None
        )
    
    # Stress-Level
    stress_levels = extract_stress_levels(poi.get("stressStrainsSensationsLevel"))
    
    # Bild
    image = extract_image_urls(poi.get("image"))
    
    return AttractionInfo(
        id=poi["id"],
        code=poi.get("code", 0),
        name=poi.get("name", "Unbekannt"),
        description=poi.get("excerpt"),
        type=poi.get("type", "unknown"),
        area_id=poi.get("areaId"),
        location=location,
        height_requirements=height_req,
        age_requirements=age_req,
        stress_levels=stress_levels,
        image=image,
        wait_time=wait_time
    )


async def get_all_attractions() -> list[AttractionInfo]:
    """Holt alle Attraktionen mit Basisinfos."""
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return []
    
    results = []
    for poi in pois_data["data"].get("pois", []):
        # Nur Attraktionen
        if poi.get("type") != "attraction":
            continue
        
        # Wartezeit holen
        wait_time = await get_waittime_by_id(poi["id"])
        
        location = None
        if poi.get("latitude") and poi.get("longitude"):
            location = Location(
                latitude=poi["latitude"],
                longitude=poi["longitude"]
            )
        
        results.append(AttractionInfo(
            id=poi["id"],
            code=poi.get("code", 0),
            name=poi.get("name", "Unbekannt"),
            description=poi.get("excerpt"),
            type=poi.get("type", "unknown"),
            area_id=poi.get("areaId"),
            location=location,
            height_requirements=None,  # Kurzform ohne Details
            age_requirements=None,
            stress_levels=None,
            image=extract_image_urls(poi.get("image")),
            wait_time=wait_time
        ))
    
    return results
