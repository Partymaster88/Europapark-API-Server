"""
Shops Router.
Shop-Informationen API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_shops, get_shop_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/shops")
async def shops():
    """Alle Shops."""
    entries = await get_all_shops()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Shopdaten verfügbar."
        )
    
    return {
        "count": len(entries),
        "shops": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/shops/{shop_id}")
async def shop_info(shop_id: int):
    """
    Informationen zu einem Shop.
    
    Args:
        shop_id: ID des Shops
    """
    info = await get_shop_by_id(shop_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Shop mit ID {shop_id} nicht gefunden"
        )
    
    return info.model_dump(exclude_none=True)
