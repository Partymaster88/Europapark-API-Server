"""
Shops Router.
Shop information API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_shops, get_shop_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/shops")
async def shops():
    """All shops."""
    entries = await get_all_shops()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No shop data available."
        )
    
    return {
        "count": len(entries),
        "shops": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/shops/{shop_id}")
async def shop_info(shop_id: int):
    """
    Information for a shop.
    
    Args:
        shop_id: ID of the shop
    """
    info = await get_shop_by_id(shop_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Shop with ID {shop_id} not found"
        )
    
    return info.model_dump(exclude_none=True)
