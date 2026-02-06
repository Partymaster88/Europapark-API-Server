"""
Waittimes Router.
Wait times API with processed data.
"""

from fastapi import APIRouter, HTTPException

from services.waittimes import get_processed_waittimes, get_waittime_by_id

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/waittimes")
async def waittimes():
    """
    All wait times with names and status.
    
    Status values:
    - operational: Attraction in operation
    - closed: Closed
    - refurbishment: Under maintenance
    - weather: Closed due to weather
    - ice: Closed due to ice
    - down: Technical issues
    - vqueue_temporarily_full: Virtual queue temporarily full
    - vqueue_full: Virtual queue completely full
    """
    entries = await get_processed_waittimes()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No wait times available. Cache not initialized yet."
        )
    
    return {
        "count": len(entries),
        "waittimes": [e.model_dump() for e in entries]
    }


@router.get("/waittimes/{attraction_id}")
async def waittime_by_id(attraction_id: int):
    """
    Wait time for a specific attraction.
    
    Args:
        attraction_id: ID of the attraction (from POI data)
    """
    entry = await get_waittime_by_id(attraction_id)
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Attraction with ID {attraction_id} not found"
        )
    
    return entry.model_dump()
