"""
Authentifizierungs-Service für OAuth2 Token Management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from config import Settings, get_settings
from services.firebase_config import get_firebase_config_service
from services.token_storage import TokenData, TokenStorage, get_token_storage

logger = logging.getLogger(__name__)


class AuthService:
    """Verwaltet die OAuth2-Authentifizierung."""
    
    REFRESH_BUFFER_SECONDS = 600
    MIN_REFRESH_INTERVAL_SECONDS = 60
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        token_storage: Optional[TokenStorage] = None
    ):
        self.settings = settings or get_settings()
        self.token_storage = token_storage or get_token_storage()
        self.firebase_config = get_firebase_config_service()
        
        self._current_token: Optional[TokenData] = None
        self._refresh_task: Optional[asyncio.Task] = None
    
    @property
    def is_authenticated(self) -> bool:
        if self._current_token is None:
            return False
        return not self._current_token.is_expired(self.REFRESH_BUFFER_SECONDS)
    
    @property
    def access_token(self) -> Optional[str]:
        if self._current_token and not self._current_token.is_expired():
            return self._current_token.access_token
        return None
    
    def get_auth_header(self) -> dict:
        if not self.access_token:
            raise RuntimeError("Nicht authentifiziert.")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def initialize(self) -> bool:
        """Initialisiert den Auth-Service."""
        logger.info("Initialisiere Authentifizierung...")
        
        saved_token = await self.token_storage.load()
        
        if saved_token and not saved_token.is_expired(self.REFRESH_BUFFER_SECONDS):
            logger.info("Gültiger gespeicherter Token gefunden.")
            self._current_token = saved_token
            self._start_refresh_scheduler()
            return True
        
        if saved_token and saved_token.refresh_token:
            logger.info("Token abgelaufen. Versuche Refresh...")
            try:
                await self._refresh_token(saved_token.refresh_token)
                self._start_refresh_scheduler()
                return True
            except Exception as e:
                logger.warning(f"Token Refresh fehlgeschlagen: {e}")
        
        try:
            await self._request_new_token()
            self._start_refresh_scheduler()
            return True
        except Exception as e:
            logger.error(f"Token-Anforderung fehlgeschlagen: {e}")
            return False
    
    async def _request_new_token(self) -> None:
        logger.info("Fordere neuen OAuth2 Token an...")
        
        credentials = await self.firebase_config.get_decrypted_credentials()
        logger.info(f"Verwende client_id: {credentials['username'][:8]}...")
        
        token_data = await self._oauth2_token_request(
            grant_type="client_credentials",
            client_id=credentials["username"],
            client_secret=credentials["password"]
        )
        
        self._current_token = token_data
        await self.token_storage.save(token_data)
        logger.info(f"Neuer Token erhalten. Gültig bis: {token_data.expires_at}")
    
    async def _refresh_token(self, refresh_token: str) -> None:
        logger.info("Erneuere Access Token...")
        
        credentials = await self.firebase_config.get_decrypted_credentials()
        
        token_data = await self._oauth2_token_request(
            grant_type="refresh_token",
            client_id=credentials["username"],
            refresh_token=refresh_token
        )
        
        self._current_token = token_data
        await self.token_storage.save(token_data)
        logger.info(f"Token erneuert. Gültig bis: {token_data.expires_at}")
    
    async def _oauth2_token_request(
        self,
        grant_type: str,
        client_id: str,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None
    ) -> TokenData:
        payload = {"grant_type": grant_type, "client_id": client_id}
        
        if client_secret:
            payload["client_secret"] = client_secret
        if refresh_token:
            payload["refresh_token"] = refresh_token
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"EuropaParkApp/{self.settings.app_version} (Android)"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.settings.auth_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                error_msg = f"Token Request fehlgeschlagen: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error_description', error_data)}"
                except Exception:
                    error_msg += f" - {response.text}"
                raise RuntimeError(error_msg)
            
            data = response.json()
        
        expires_in = data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        return TokenData(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            expires_at=expires_at
        )
    
    def _start_refresh_scheduler(self) -> None:
        if self._refresh_task and not self._refresh_task.done():
            return
        self._refresh_task = asyncio.create_task(self._refresh_loop())
        logger.info("Token Refresh Scheduler gestartet.")
    
    def _stop_refresh_scheduler(self) -> None:
        if self._refresh_task:
            self._refresh_task.cancel()
            self._refresh_task = None
            logger.info("Token Refresh Scheduler gestoppt.")
    
    async def _refresh_loop(self) -> None:
        while True:
            try:
                if self._current_token is None:
                    await asyncio.sleep(60)
                    continue
                
                time_until_expiry = (
                    self._current_token.expires_at - datetime.now()
                ).total_seconds()
                
                sleep_time = max(
                    time_until_expiry - self.REFRESH_BUFFER_SECONDS,
                    self.MIN_REFRESH_INTERVAL_SECONDS
                )
                
                await asyncio.sleep(sleep_time)
                
                if self._current_token.refresh_token:
                    try:
                        await self._refresh_token(self._current_token.refresh_token)
                    except Exception as e:
                        logger.warning(f"Refresh fehlgeschlagen: {e}")
                        await self._request_new_token()
                else:
                    await self._request_new_token()
                    
            except asyncio.CancelledError:
                logger.info("Token Refresh Loop beendet.")
                break
            except Exception as e:
                logger.error(f"Fehler im Token Refresh Loop: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self) -> None:
        self._stop_refresh_scheduler()
        logger.info("Auth-Service heruntergefahren.")
    
    def get_status(self) -> dict:
        if self._current_token is None:
            return {"authenticated": False, "token_present": False, "expires_at": None, "is_expired": True}
        
        return {
            "authenticated": self.is_authenticated,
            "token_present": True,
            "expires_at": self._current_token.expires_at.isoformat(),
            "is_expired": self._current_token.is_expired(),
            "created_at": self._current_token.created_at.isoformat()
        }


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


async def initialize_auth() -> bool:
    return await get_auth_service().initialize()


async def shutdown_auth() -> None:
    global _auth_service
    if _auth_service:
        await _auth_service.shutdown()
