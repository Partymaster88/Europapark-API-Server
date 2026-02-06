"""
Attractions Router.
Attraction information API.
"""

from fastapi import APIRouter, HTTPException

from services.attractions import get_attraction_info, get_all_attractions

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/attractions")
async def attractions():
    """All attractions with basic info."""
    entries = await get_all_attractions()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No attraction data available. Cache not initialized yet."
        )
    
    return {
        "count": len(entries),
        "attractions": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/attractions/{attraction_id}")
async def attraction_info(attraction_id: int):
    """
    Full information for an attraction.
    
    Includes:
    - Basic info (name, description, type)
    - Location (coordinates)
    - Height/age requirements
    - Stress levels (speed, height, etc.)
    - Images
    - Current wait time
    
    Args:
        attraction_id: ID of the attraction (same ID as in /waittimes)
    """
    info = await get_attraction_info(attraction_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Attraction with ID {attraction_id} not found"
        )
    
    return info.model_dump(exclude_none=True)
