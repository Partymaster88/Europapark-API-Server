# Europapark API Server

Ein FastAPI-basierter Server für Europapark-Daten.

## Installation

1. **Virtuelle Umgebung erstellen:**
   ```bash
   python -m venv venv
   ```

2. **Virtuelle Umgebung aktivieren:**
   ```bash
   # Linux/macOS
   source venv/bin/activate
   
   # Windows
   .\venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren:**
   ```bash
   # .env.example kopieren und anpassen
   cp .env.example .env
   # Dann die .env Datei mit den korrekten Werten befüllen
   ```

## Konfiguration

Die Anwendung wird über Umgebungsvariablen in der `.env` Datei konfiguriert:

| Variable | Beschreibung |
|----------|--------------|
| `FB_APP_ID` | Firebase App ID |
| `FB_API_KEY` | Firebase API Key |
| `FB_PROJECT_ID` | Firebase Project ID |
| `API_BASE` | Basis-URL der Ticket-API |
| `AUTH_URL` | URL für die Authentifizierung |
| `ENC_KEY` | Encryption Key |
| `ENC_IV` | Encryption IV |
| `API_USERNAME` | API Benutzername |
| `API_PASSWORD` | API Passwort |
| `APP_VERSION` | App Version |

## Server starten

```bash
# Entwicklungsmodus mit Auto-Reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Oder direkt mit Python
python main.py
```

## Firebase Health-Check

Der Server führt automatisch Firebase Health-Checks durch:

- **Bei Startup:** Initialer Health-Check beim Serverstart
- **Täglich um 03:00 Uhr:** Automatischer Health-Check mit Secret-Aktualisierung

Falls sich die Secrets in der `.env` Datei geändert haben, werden diese beim täglichen Check automatisch neu geladen.

## API Dokumentation

Nach dem Start des Servers ist die interaktive API-Dokumentation verfügbar unter:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

| Methode | Endpoint  | Beschreibung                    |
|---------|-----------|--------------------------------|
| GET     | /         | Willkommensnachricht + Firebase Status |
| GET     | /health   | Health-Check Status (inkl. Firebase) |
| GET     | /docs     | Swagger API Dokumentation      |
| GET     | /redoc    | ReDoc API Dokumentation        |

## Projektstruktur

```
Europapark-API-Server/
├── main.py              # Hauptanwendung mit Lifespan-Management
├── config.py            # Konfigurationsverwaltung
├── requirements.txt     # Python-Abhängigkeiten
├── .env                 # Umgebungsvariablen (nicht im Git)
├── .env.example         # Beispiel-Konfiguration
├── .gitignore           # Git-Ignores
├── README.md            # Diese Datei
└── services/
    ├── __init__.py
    ├── firebase_health.py  # Firebase Health-Check Service
    └── scheduler.py        # Täglicher Scheduler
```
