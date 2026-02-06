"""
Services Router.
Service-Informationen API.
"""

from fastapi import APIRouter, HTTPException

from services.pois import get_all_services, get_service_by_id

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/services")
async def services():
    """Alle Services (WC, Info, Erste Hilfe, etc.)."""
    entries = await get_all_services()
    
    if not entries:
        raise HTTPException(
            status_code=503,
            detail="Keine Servicedaten verfügbar."
        )
    
    return {
        "count": len(entries),
        "services": [e.model_dump(exclude_none=True) for e in entries]
    }


@router.get("/services/{service_id}")
async def service_info(service_id: int):
    """
    Informationen zu einem Service.
    
    Args:
        service_id: ID des Services
    """
    info = await get_service_by_id(service_id)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Service mit ID {service_id} nicht gefunden"
        )
    
    return info.model_dump(exclude_none=True)
