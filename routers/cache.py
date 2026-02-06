"""
Cache API Router.
Gibt gecachte Daten aus der Datenbank zurück.
"""

from fastapi import APIRouter, HTTPException

from services.cache import get_cache_service, CACHE_KEYS

router = APIRouter(prefix="/cache", tags=["Cache API"])


@router.get("/waittimes")
async def cached_waittimes():
    """Gecachte Wartezeiten (aktualisiert alle 5 Min)."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["waittimes"])
    if not data:
        raise HTTPException(status_code=404, detail="Keine gecachten Daten verfügbar")
    return data


@router.get("/showtimes")
async def cached_showtimes():
    """Gecachte Showzeiten (aktualisiert alle 5 Min)."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["showtimes"])
    if not data:
        raise HTTPException(status_code=404, detail="Keine gecachten Daten verfügbar")
    return data


@router.get("/pois")
async def cached_pois():
    """Gecachte POIs (aktualisiert täglich)."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["pois"])
    if not data:
        raise HTTPException(status_code=404, detail="Keine gecachten Daten verfügbar")
    return data


@router.get("/seasons")
async def cached_seasons():
    """Gecachte Seasons (aktualisiert täglich)."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["seasons"])
    if not data:
        raise HTTPException(status_code=404, detail="Keine gecachten Daten verfügbar")
    return data


@router.get("/openingtimes")
async def cached_openingtimes():
    """Gecachte Öffnungszeiten (aktualisiert täglich)."""
    cache = get_cache_service()
    data = await cache.load(CACHE_KEYS["openingtimes"])
    if not data:
        raise HTTPException(status_code=404, detail="Keine gecachten Daten verfügbar")
    return data
