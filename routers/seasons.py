"""
Seasons Router.
Saison-Daten API.
"""

from fastapi import APIRouter, HTTPException

from services.seasons import get_seasons

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/seasons")
async def seasons():
    """
    Alle Europapark-Saisons.
    """
    entries = await get_seasons()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Saisondaten verfügbar."
        )
    
    return {
        "count": len(entries),
        "seasons": [e.model_dump(exclude_none=True) for e in entries]
    }
