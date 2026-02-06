# Europapark API Server

FastAPI server for Europapark data with OAuth2 authentication.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

## Deployment (Dokploy)

1. Connect repository
2. Set environment variables from `.env.example`
3. Deploy - Nixpacks detects `nixpacks.toml` automatically

## Endpoints

### Times
| Endpoint | Description |
|----------|-------------|
| `/times/waittimes` | Wait times for attractions |
| `/times/showtimes` | Show times |
| `/times/openingtimes` | Opening hours |
| `/times/seasons` | Season information |

### Info
| Endpoint | Description |
|----------|-------------|
| `/info/attractions` | Attraction details |
| `/info/shows` | Show details |
| `/info/shops` | Shop information |
| `/info/restaurants` | Restaurant information |
| `/info/services` | Service facilities |

### Raw
| Endpoint | Description |
|----------|-------------|
| `/raw/waittimes` | Raw wait times data |
| `/raw/pois` | Raw POI data |
| `/raw/seasons` | Raw season data |
| `/raw/openingtimes` | Raw opening times data |
| `/raw/showtimes` | Raw show times data |

### System
| Endpoint | Description |
|----------|-------------|
| `/` | API info |
| `/health` | Health check |
| `/docs` | Swagger UI |

## Structure

```
├── main.py              # FastAPI App
├── config.py            # Settings
├── database.py          # SQLAlchemy DB
├── nixpacks.toml        # Deployment
├── requirements.txt     # Dependencies
├── .env                 # Configuration
├── routers/
│   ├── raw.py           # Raw API routes
│   ├── waittimes.py     # Wait times routes
│   ├── showtimes.py     # Show times routes
│   ├── openingtimes.py  # Opening times routes
│   ├── seasons.py       # Seasons routes
│   ├── attractions.py   # Attractions routes
│   ├── shows.py         # Shows routes
│   ├── shops.py         # Shops routes
│   ├── restaurants.py   # Restaurants routes
│   └── services.py      # Services routes
└── services/
    ├── auth.py          # OAuth2
    ├── cache.py         # Data caching
    ├── crypto.py        # Blowfish decryption
    ├── europapark_api.py # API client
    ├── firebase_*.py    # Firebase services
    ├── token_storage.py # Token persistence
    └── scheduler.py     # Scheduled tasks
```
