"""
Openingtimes Router.
Öffnungszeiten API.
"""

from fastapi import APIRouter, HTTPException

from services.openingtimes import get_opening_times

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/openingtimes")
async def openingtimes():
    """
    Aktuelle Öffnungszeiten des Europaparks.
    
    Enthält heute, morgen und nächste Öffnung.
    """
    info = await get_opening_times()
    
    if not info:
        raise HTTPException(
            status_code=503,
            detail="Keine Öffnungszeiten verfügbar."
        )
    
    return info.model_dump(exclude_none=True)
