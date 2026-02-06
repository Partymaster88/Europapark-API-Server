"""
Seasons Router.
Season data API.
"""

from fastapi import APIRouter, HTTPException

from services.seasons import get_seasons

router = APIRouter(prefix="/times", tags=["Times"])


@router.get("/seasons")
async def seasons():
    """All Europapark seasons."""
    entries = await get_seasons()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No season data available."
        )
    
    return {
        "count": len(entries),
        "seasons": [e.model_dump(exclude_none=True) for e in entries]
    }
