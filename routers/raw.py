"""
Raw API Router.
Returns raw data from the Europapark API.
"""

from fastapi import APIRouter, HTTPException

from services.europapark_api import (
    get_waiting_times,
    get_pois,
    get_seasons,
    get_opening_times,
    get_show_times
)

router = APIRouter(prefix="/raw", tags=["Raw API"])


@router.get("/waittimes")
async def raw_waittimes():
    """Raw wait times data from Europapark API."""
    try:
        return await get_waiting_times()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pois")
async def raw_pois():
    """Raw POI data (attractions, shows, etc.) from Europapark API."""
    try:
        return await get_pois()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasons")
async def raw_seasons():
    """Raw season/calendar data from Europapark API."""
    try:
        return await get_seasons()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/openingtimes")
async def raw_opening_times():
    """Raw opening times data from Europapark API."""
    try:
        return await get_opening_times()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/showtimes")
async def raw_show_times():
    """Raw show times data from Europapark API."""
    try:
        return await get_show_times()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
