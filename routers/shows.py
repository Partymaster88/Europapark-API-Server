"""
Shows Router.
Show-Informationen API.
"""

from fastapi import APIRouter, HTTPException

from services.shows import get_show_info, get_all_shows

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/shows")
async def shows():
    """
    Alle Shows mit Basisinfos.
    """
    entries = await get_all_shows()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Showdaten verfügbar. Cache noch nicht initialisiert."
        )
    
    return {
        "count": len(entries),
        "shows": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/shows/{show_id}")
async def show_info(show_id: int):
    """
    Vollständige Informationen zu einer Show.
    
    Enthält:
    - Name, Beschreibung
    - Location (Name und Koordinaten)
    - Dauer
    - Bilder
    - Aktuelle Showzeiten
    
    Args:
        show_id: ID der Show
    """
    info = await get_show_info(show_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Show mit ID {show_id} nicht gefunden"
        )
    
    return info.model_dump(exclude_none=True)
