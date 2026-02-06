"""
Europapark API Server
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_database, close_database
from routers.attractions import router as attractions_router
from routers.cache import router as cache_router
from routers.raw import router as raw_router
from routers.shows import router as shows_router
from routers.showtimes import router as showtimes_router
from routers.waittimes import router as waittimes_router
from services.auth import get_auth_service, initialize_auth, shutdown_auth
from services.cache import get_cache_service
from services.firebase_health import check_firebase_health, get_firebase_status
from services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle-Manager für die FastAPI-Anwendung."""
    logger.info("Starte Europapark API Server...")
    
    # Konfiguration laden
    settings = get_settings()
    logger.info(f"Konfiguration geladen. Firebase Project: {settings.fb_project_id}")
    
    # Datenbank initialisieren
    await init_database()
    
    # Firebase Health-Check
    status = await check_firebase_health()
    if status.is_healthy:
        logger.info(f"Firebase Health-Check erfolgreich. Response Time: {status.response_time_ms:.2f}ms")
    else:
        logger.warning(f"Firebase Health-Check fehlgeschlagen: {status.last_error}")
    
    # OAuth2 Authentifizierung
    auth_success = await initialize_auth()
    if auth_success:
        auth_service = get_auth_service()
        logger.info(f"Authentifizierung erfolgreich. Token gültig bis: {auth_service.get_status().get('expires_at')}")
        
        # Cache-Service starten (nur wenn authentifiziert)
        cache_service = get_cache_service()
        cache_service.start()
        logger.info("Cache-Service gestartet.")
    else:
        logger.warning("Authentifizierung fehlgeschlagen.")
    
    start_scheduler()
    logger.info("Server erfolgreich gestartet.")
    
    yield
    
    # Shutdown
    logger.info("Fahre Server herunter...")
    get_cache_service().stop()
    await shutdown_auth()
    stop_scheduler()
    await close_database()
    logger.info("Server heruntergefahren.")


app = FastAPI(
    title="Europapark API",
    description="API Server für Europapark-Daten",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registrieren
app.include_router(raw_router)
app.include_router(cache_router)
app.include_router(waittimes_router)
app.include_router(showtimes_router)
app.include_router(attractions_router)
app.include_router(shows_router)


@app.get("/")
async def root():
    firebase_status = get_firebase_status()
    auth_service = get_auth_service()
    
    return {
        "message": "Willkommen zur Europapark API",
        "version": "1.0.0",
        "docs": "/docs",
        "firebase_status": firebase_status.to_dict(),
        "auth_status": auth_service.get_status(),
    }


@app.get("/health")
async def health_check():
    firebase_status = get_firebase_status()
    auth_service = get_auth_service()
    auth_status = auth_service.get_status()
    
    is_healthy = firebase_status.is_healthy and auth_status.get("authenticated", False)
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "firebase": firebase_status.to_dict(),
        "auth": auth_status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
