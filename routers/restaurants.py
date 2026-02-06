"""
Restaurants Router.
Restaurant information API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_restaurants, get_restaurant_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/restaurants")
async def restaurants():
    """All restaurants and gastronomy."""
    entries = await get_all_restaurants()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No restaurant data available."
        )
    
    return {
        "count": len(entries),
        "restaurants": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/restaurants/{restaurant_id}")
async def restaurant_info(restaurant_id: int):
    """
    Information for a restaurant.
    
    Args:
        restaurant_id: ID of the restaurant
    """
    info = await get_restaurant_by_id(restaurant_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    return info.model_dump(exclude_none=True)
