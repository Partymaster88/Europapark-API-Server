"""
Token Storage Service.
Persistiert OAuth2 Tokens in einer JSON-Datei.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TOKEN_FILE = Path(__file__).parent.parent / "data" / "tokens.json"


class TokenData:
    """Repräsentiert gespeicherte Token-Daten."""
    
    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str],
        token_type: str,
        expires_at: datetime,
        created_at: Optional[datetime] = None
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now()
    
    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """Prüft ob der Token abgelaufen ist (mit Sicherheitspuffer)."""
        expiry_with_buffer = self.expires_at - timedelta(seconds=buffer_seconds)
        return datetime.now() >= expiry_with_buffer
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary für JSON-Serialisierung."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TokenData":
        """Erstellt TokenData aus Dictionary."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data["token_type"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )


class TokenStorage:
    """Verwaltet die Persistierung von OAuth2 Tokens."""
    
    def __init__(self, token_file: Optional[Path] = None):
        self.token_file = token_file or TOKEN_FILE
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Stellt sicher, dass das Verzeichnis existiert."""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, token_data: TokenData) -> None:
        """Speichert Token-Daten in die Datei."""
        try:
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(token_data.to_dict(), f, indent=2)
            logger.info(f"Token gespeichert. Gültig bis: {token_data.expires_at}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Tokens: {e}")
            raise
    
    def load(self) -> Optional[TokenData]:
        """Lädt Token-Daten aus der Datei."""
        if not self.token_file.exists():
            logger.debug("Keine gespeicherte Token-Datei gefunden.")
            return None
        
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            token_data = TokenData.from_dict(data)
            logger.debug(f"Token geladen. Gültig bis: {token_data.expires_at}")
            return token_data
        except Exception as e:
            logger.error(f"Fehler beim Laden des Tokens: {e}")
            return None


_token_storage: Optional[TokenStorage] = None


def get_token_storage() -> TokenStorage:
    """Gibt die globale TokenStorage-Instanz zurück."""
    global _token_storage
    if _token_storage is None:
        _token_storage = TokenStorage()
    return _token_storage
