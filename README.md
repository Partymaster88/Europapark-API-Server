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

## Struktur

```
├── main.py              # FastAPI App
├── config.py            # Settings
├── nixpacks.toml        # Deployment
├── requirements.txt     # Dependencies
├── .env                 # Konfiguration
└── services/
    ├── auth.py          # OAuth2
    ├── crypto.py        # Blowfish
    ├── firebase_*.py    # Firebase
    ├── token_storage.py # Token Persistenz
    └── scheduler.py     # Daily Tasks
```
