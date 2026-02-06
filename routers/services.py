"""
Services Router.
Service facilities information API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_services, get_service_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/services")
async def services():
    """All service facilities (restrooms, info points, first aid, etc.)."""
    entries = await get_all_services()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="No service data available."
        )
    
    return {
        "count": len(entries),
        "services": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/services/{service_id}")
async def service_info(service_id: int):
    """
    Information for a service facility.
    
    Args:
        service_id: ID of the service
    """
    info = await get_service_by_id(service_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Service with ID {service_id} not found"
        )
    
    return info.model_dump(exclude_none=True)
