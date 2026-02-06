"""
Konfigurationsmodul für die Europapark API.
Lädt Umgebungsvariablen und stellt sie als Pydantic Settings bereit.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Anwendungskonfiguration aus Umgebungsvariablen."""

    # Firebase Konfiguration
    fb_app_id: str
    fb_api_key: str
    fb_project_id: str

    # API Konfiguration
    api_base: str
    auth_url: str

    # Encryption Keys
    enc_key: str
    enc_iv: str

    # API Credentials
    user_key: str
    pass_key: str
    api_username: str
    api_password: str

    # App Version
    app_version: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Gibt die gecachte Settings-Instanz zurück.
    Verwendet lru_cache für Performance.
    """
    return get_settings_uncached()


def get_settings_uncached() -> Settings:
    """
    Lädt die Settings neu ohne Cache.
    Verwendet für Secret-Aktualisierungen.
    """
    return Settings()


def refresh_settings() -> Settings:
    """
    Aktualisiert die Settings durch Neuladen der .env Datei.
    Löscht den Cache und lädt neu.
    """
    get_settings.cache_clear()
    return get_settings()
