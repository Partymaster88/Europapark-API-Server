"""
Attractions Router.
Attraktionsinformationen API.
"""

from fastapi import APIRouter, HTTPException

from services.attractions import get_attraction_info, get_all_attractions

router = APIRouter(tags=["Attractions"])


@router.get("/attractions")
async def attractions():
    """
    Alle Attraktionen mit Basisinfos.
    """
    entries = await get_all_attractions()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Attraktionsdaten verfügbar. Cache noch nicht initialisiert."
        )
    
    return {
        "count": len(entries),
        "attractions": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/attractions/{attraction_id}")
async def attraction_info(attraction_id: int):
    """
    Vollständige Informationen zu einer Attraktion.
    
    Enthält:
    - Basis-Infos (Name, Beschreibung, Typ)
    - Standort (Koordinaten)
    - Größen-/Altersanforderungen
    - Belastungslevel (Geschwindigkeit, Höhe, etc.)
    - Bilder
    - Aktuelle Wartezeit
    
    Args:
        attraction_id: ID der Attraktion (gleiche ID wie in /waittimes)
    """
    info = await get_attraction_info(attraction_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Attraktion mit ID {attraction_id} nicht gefunden"
        )
    
    return info.model_dump(exclude_none=True)
