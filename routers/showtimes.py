"""
Showtimes Router.
Showzeiten-API mit verarbeiteten Daten.
"""

from fastapi import APIRouter, HTTPException

from services.showtimes import get_processed_showtimes, get_showtime_by_id

router = APIRouter(tags=["Showtimes"])


@router.get("/showtimes")
async def showtimes():
    """
    Alle Showzeiten mit Namen und Location.
    
    Times sind im ISO 8601 Format (z.B. "2026-02-06T15:15:00+01:00").
    """
    entries = await get_processed_showtimes()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Showzeiten verfügbar. Cache noch nicht initialisiert."
        )
    
    return {
        "count": len(entries),
        "showtimes": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/showtimes/{show_id}")
async def showtime_by_id(show_id: int):
    """
    Showzeiten für eine bestimmte Show.
    
    Args:
        show_id: ID der Show
    """
    entry = await get_showtime_by_id(show_id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Show mit ID {show_id} nicht gefunden"
        )
    
    return entry.model_dump(exclude_none=True)
