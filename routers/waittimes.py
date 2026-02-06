"""
Waittimes Router.
Eigene Wartezeiten-API mit verarbeiteten Daten.
"""

from fastapi import APIRouter, HTTPException

from services.waittimes import get_processed_waittimes, get_waittime_by_id

router = APIRouter(tags=["Waittimes"])


@router.get("/waittimes")
async def waittimes():
    """
    Alle Wartezeiten mit Namen und Status.
    
    Status-Werte:
    - operational: Attraktion in Betrieb
    - closed: Geschlossen
    - refurbishment: Wartung
    - weather: Wetter-bedingt geschlossen
    - ice: Eis-bedingt geschlossen
    - down: Störung
    - vqueue_temporarily_full: Virtual Queue temporär voll
    - vqueue_full: Virtual Queue komplett voll
    """
    entries = await get_processed_waittimes()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Wartezeiten verfügbar. Cache noch nicht initialisiert."
        )
    
    return {
        "count": len(entries),
        "waittimes": [e.model_dump() for e in entries]
    }


@router.get("/waittimes/{attraction_id}")
async def waittime_by_id(attraction_id: int):
    """
    Wartezeit für eine bestimmte Attraktion.
    
    Args:
        attraction_id: ID der Attraktion (aus POI-Daten)
    """
    entry = await get_waittime_by_id(attraction_id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Attraktion mit ID {attraction_id} nicht gefunden"
        )
    
    return entry.model_dump()
