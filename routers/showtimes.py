"""
Showtimes Router.
Show times API with processed data.
"""

from fastapi import APIRouter, HTTPException

from services.showtimes import get_processed_showtimes, get_showtime_by_id

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/showtimes")
async def showtimes():
    """
    All show times with names and locations.
    
    Times are in ISO 8601 format (e.g. "2026-02-06T15:15:00+01:00").
    """
    entries = await get_processed_showtimes()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No show times available. Cache not initialized yet."
        )
    
    return {
        "count": len(entries),
        "showtimes": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/showtimes/{show_id}")
async def showtime_by_id(show_id: int):
    """
    Show times for a specific show.
    
    Args:
        show_id: ID of the show
    """
    entry = await get_showtime_by_id(show_id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Show with ID {show_id} not found"
        )
    
    return entry.model_dump(exclude_none=True)
