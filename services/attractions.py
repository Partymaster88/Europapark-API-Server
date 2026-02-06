"""
Attractions Service.
Processes and formats attraction information from POI data.
"""

import logging
from typing import Optional

from pydantic import BaseModel

from services.cache import get_cache_service, CACHE_KEYS
from services.waittimes import get_waittime_by_id, WaitTimeEntry

logger = logging.getLogger(__name__)


class Location(BaseModel):
    """Location of an attraction."""
    latitude: float
    longitude: float


class HeightRequirements(BaseModel):
    """Height requirements."""
    min_height: Optional[int] = None
    min_height_with_adult: Optional[int] = None
    max_height: Optional[int] = None


class AgeRequirements(BaseModel):
    """Age requirements."""
    min_age: Optional[int] = None
    min_age_with_adult: Optional[int] = None
    max_age: Optional[int] = None


class StressLevel(BaseModel):
    """Stress levels (0-3 scale)."""
    light: Optional[int] = None
    noise: Optional[int] = None
    smoke: Optional[int] = None
    smell: Optional[int] = None
    darkness: Optional[int] = None
    height: Optional[int] = None
    fear: Optional[int] = None
    narrow_space: Optional[int] = None
    g_force: Optional[int] = None
    splashing_water: Optional[int] = None


class ImageUrls(BaseModel):
    """Image URLs."""
    small: Optional[str] = None
    medium: Optional[str] = None


class AttractionInfo(BaseModel):
    """Full attraction information."""
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
    icon: Optional[str] = None
    wait_time: Optional[WaitTimeEntry] = None


async def get_poi_by_id(attraction_id: int) -> Optional[dict]:
    """Get raw POI data by ID (Europapark only, no Rulantica)."""
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return None
    
    for poi in pois_data["data"].get("pois", []):
        scopes = poi.get("scopes", [])
        if poi.get("id") == attraction_id and "europapark" in scopes:
            return poi
    
    return None


def extract_image_urls(image_data: Optional[dict]) -> Optional[ImageUrls]:
    """Extract image URLs from POI data."""
    if not image_data:
        return None
    
    return ImageUrls(
        small=image_data.get("small"),
        medium=image_data.get("medium")
    )


def extract_stress_levels(stress_data: Optional[dict]) -> Optional[StressLevel]:
    """Extract stress levels from POI data."""
    if not stress_data:
        return None
    
    return StressLevel(
        light=stress_data.get("light"),
        noise=stress_data.get("noise"),
        smoke=stress_data.get("smoke"),
        smell=stress_data.get("smell"),
        darkness=stress_data.get("darkness"),
        height=stress_data.get("height"),
        fear=stress_data.get("fear"),
        narrow_space=stress_data.get("narrowSpace"),
        g_force=stress_data.get("gForce"),
        splashing_water=stress_data.get("splashingWater")
    )


async def get_attraction_info(attraction_id: int) -> Optional[AttractionInfo]:
    """Get formatted attraction information."""
    poi = await get_poi_by_id(attraction_id)
    
    if not poi:
        return None
    
    wait_time = await get_waittime_by_id(attraction_id)
    
    location = None
    if poi.get("latitude") and poi.get("longitude"):
        location = Location(
            latitude=poi["latitude"],
            longitude=poi["longitude"]
        )
    
    height_req = None
    if any([poi.get("minHeight"), poi.get("minHeightAdult"), poi.get("maxHeight")]):
        height_req = HeightRequirements(
            min_height=poi.get("minHeight"),
            min_height_with_adult=poi.get("minHeightAdult"),
            max_height=poi.get("maxHeight")
        )
    
    age_req = None
    if any([poi.get("minAge"), poi.get("minAgeAdult"), poi.get("maxAge")]):
        age_req = AgeRequirements(
            min_age=poi.get("minAge") if poi.get("minAge", 0) > 0 else None,
            min_age_with_adult=poi.get("minAgeAdult"),
            max_age=poi.get("maxAge") if poi.get("maxAge", 0) > 0 else None
        )
    
    stress_levels = extract_stress_levels(poi.get("stressStrainsSensationsLevel"))
    
    image = extract_image_urls(poi.get("image"))
    icon = poi.get("icon", {}).get("small") if poi.get("icon") else None
    
    return AttractionInfo(
        id=poi["id"],
        code=poi.get("code", 0),
        name=poi.get("name", "Unknown"),
        description=poi.get("excerpt"),
        type=poi.get("type", "unknown"),
        area_id=poi.get("areaId"),
        location=location,
        height_requirements=height_req,
        age_requirements=age_req,
        stress_levels=stress_levels,
        image=image,
        icon=icon,
        wait_time=wait_time
    )


async def get_all_attractions() -> list[AttractionInfo]:
    """Get all Europapark attractions (no Rulantica)."""
    cache = get_cache_service()
    pois_data = await cache.load(CACHE_KEYS["pois"])
    
    if not pois_data or "data" not in pois_data:
        return []
    
    results = []
    for poi in pois_data["data"].get("pois", []):
        scopes = poi.get("scopes", [])
        
        # Europapark attractions only (no Rulantica)
        if poi.get("type") != "attraction" or "europapark" not in scopes:
            continue
        
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
            name=poi.get("name", "Unknown"),
            description=poi.get("excerpt"),
            type=poi.get("type", "unknown"),
            area_id=poi.get("areaId"),
            location=location,
            height_requirements=None,
            age_requirements=None,
            stress_levels=None,
            image=extract_image_urls(poi.get("image")),
            icon=poi.get("icon", {}).get("small") if poi.get("icon") else None,
            wait_time=wait_time
        ))
    
    return results
