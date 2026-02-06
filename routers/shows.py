"""
Shows Router.
Show information API.
"""

from fastapi import APIRouter, HTTPException

from services.shows import get_show_info, get_all_shows

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/shows")
async def shows():
    """All shows with basic info."""
    entries = await get_all_shows()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No show data available. Cache not initialized yet."
        )
    
    return {
        "count": len(entries),
        "shows": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/shows/{show_id}")
async def show_info(show_id: int):
    """
    Full information for a show.
    
    Includes:
    - Name, description
    - Location (name and coordinates)
    - Duration
    - Images
    - Current show times
    
    Args:
        show_id: ID of the show
    """
    info = await get_show_info(show_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Show with ID {show_id} not found"
        )
    
    return info.model_dump(exclude_none=True)
