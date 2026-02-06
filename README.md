# Europapark API Server

FastAPI Server für Europapark-Daten mit OAuth2 Authentifizierung.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Starten

```bash
uvicorn main:app --reload --port 8000
```

## Deployment (Dokploy)

1. Repository verbinden
2. Umgebungsvariablen aus `.env.example` setzen
3. Deploy - Nixpacks erkennt `nixpacks.toml` automatisch

## Endpoints

| Endpoint | Beschreibung |
|----------|--------------|
| `/` | Status |
| `/health` | Health-Check |
| `/docs` | Swagger UI |
| `/raw/waittimes` | Rohe Wartezeiten-Daten |
| `/raw/pois` | Rohe POI/Attraktionen-Daten |
| `/raw/seasons` | Rohe Saison/Kalender-Daten |
| `/raw/openingtimes` | Rohe Öffnungszeiten-Daten |
| `/raw/showtimes` | Rohe Showzeiten-Daten |

## Struktur

```
├── main.py              # FastAPI App
├── config.py            # Settings
├── database.py          # SQLAlchemy DB
├── nixpacks.toml        # Deployment
├── requirements.txt     # Dependencies
├── .env                 # Konfiguration
├── routers/
│   └── raw.py           # Raw API Routes
└── services/
    ├── auth.py          # OAuth2
    ├── crypto.py        # Blowfish
    ├── europapark_api.py # API Client
    ├── firebase_*.py    # Firebase
    ├── token_storage.py # Token Persistenz
    └── scheduler.py     # Daily Tasks
```
