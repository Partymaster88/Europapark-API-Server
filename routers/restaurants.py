"""
Restaurants Router.
Restaurant-Informationen API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_restaurants, get_restaurant_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/restaurants")
async def restaurants():
    """Alle Restaurants und Gastronomie."""
    entries = await get_all_restaurants()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Restaurantdaten verfügbar."
        )
    
    return {
        "count": len(entries),
        "restaurants": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/restaurants/{restaurant_id}")
async def restaurant_info(restaurant_id: int):
    """
    Informationen zu einem Restaurant.
    
    Args:
        restaurant_id: ID des Restaurants
    """
    info = await get_restaurant_by_id(restaurant_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Restaurant mit ID {restaurant_id} nicht gefunden"
        )
    
    return info.model_dump(exclude_none=True)
