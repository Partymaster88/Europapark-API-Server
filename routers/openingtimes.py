"""
Openingtimes Router.
Opening hours API.
"""

from fastapi import APIRouter, HTTPException

from services.openingtimes import get_opening_times

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/openingtimes")
async def openingtimes():
    """
    Current opening hours of Europapark.
    
    Includes today, tomorrow, and next opening.
    """
    info = await get_opening_times()
    
    if not info:
        raise HTTPException(
            status_code=503,
            detail="No opening times available."
        )
    
    return info.model_dump(exclude_none=True)
