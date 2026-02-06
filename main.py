"""
Europapark API Server
Ein FastAPI-basierter Server für Europapark-Daten.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from services.firebase_health import check_firebase_health, get_firebase_status
from services.scheduler import start_scheduler, stop_scheduler

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-Manager für die FastAPI-Anwendung.
    
    Startup:
    - Lädt die Konfiguration
    - Führt initialen Firebase Health-Check durch
    - Startet den täglichen Scheduler
    
    Shutdown:
    - Stoppt den Scheduler
    """
    # Startup
    logger.info("Starte Europapark API Server...")
    
    # Konfiguration laden und validieren
    try:
        settings = get_settings()
        logger.info(f"Konfiguration geladen. Firebase Project: {settings.fb_project_id}")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {e}")
        raise
    
    # Initialer Firebase Health-Check
    logger.info("Führe initialen Firebase Health-Check durch...")
    status = await check_firebase_health()
    
    if status.is_healthy:
        logger.info(
            f"Firebase Health-Check erfolgreich. "
            f"Response Time: {status.response_time_ms:.2f}ms"
        )
    else:
        logger.warning(
            f"Firebase Health-Check fehlgeschlagen: {status.last_error}. "
            f"Server wird trotzdem gestartet."
        )
    
    # Täglichen Scheduler starten
    start_scheduler()
    
    logger.info("Europapark API Server erfolgreich gestartet.")
    
    yield
    
    # Shutdown
    logger.info("Fahre Europapark API Server herunter...")
    stop_scheduler()
    logger.info("Server heruntergefahren.")


# FastAPI App initialisieren
app = FastAPI(
    title="Europapark API",
    description="API Server für Europapark-Daten",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root-Endpoint - gibt eine Willkommensnachricht zurück."""
    firebase_status = get_firebase_status()
    
    return {
        "message": "Willkommen zur Europapark API",
        "version": "1.0.0",
        "docs": "/docs",
        "firebase_status": firebase_status.to_dict(),
    }


@app.get("/health")
async def health_check():
    """Health-Check Endpoint mit Firebase-Status."""
    firebase_status = get_firebase_status()
    
    return {
        "status": "healthy" if firebase_status.is_healthy else "degraded",
        "firebase": firebase_status.to_dict(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
