# Europapark API Server

Unofficial API server providing Europapark data including wait times, show times, opening hours, and POI information.

## Disclaimer

**This project is not affiliated with, endorsed by, or connected to Europa-Park GmbH & Co Mack KG in any way.**

This is an unofficial, community-driven project that accesses publicly available data. Use at your own risk. The developers are not responsible for any misuse or any consequences arising from the use of this software.

All trademarks, service marks, and company names are the property of their respective owners.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure the `.env` file with the required credentials.

## Development

```bash
uvicorn main:app --reload --port 8000
```

## Deployment

### Docker

```bash
docker build -t europapark-api .
docker run -p 8000:8000 --env-file .env europapark-api
```

### Nixpacks

The project includes `nixpacks.toml` for automatic builds:

```bash
nixpacks build . -o out
```

### Manual

1. Set up Python environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
