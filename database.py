"""
Datenbank-Modul.
Verwaltet die SQLAlchemy Verbindung und Models.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy Base Class."""
    pass


class TokenModel(Base):
    """Token-Daten in der Datenbank."""
    
    __tablename__ = "tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_type: Mapped[str] = mapped_column(String(50))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


_engine = None
_session_factory = None


def get_database_url() -> str:
    """Konvertiert DATABASE_URL für async SQLAlchemy."""
    url = get_settings().database_url
    
    # SQLite async
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    # PostgreSQL async
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    
    return url


async def init_database() -> None:
    """Initialisiert die Datenbankverbindung und erstellt Tabellen."""
    global _engine, _session_factory
    
    db_url = get_database_url()
    logger.info(f"Initialisiere Datenbank: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    _engine = create_async_engine(db_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Datenbank initialisiert.")


async def close_database() -> None:
    """Schließt die Datenbankverbindung."""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Datenbankverbindung geschlossen.")


def get_session() -> AsyncSession:
    """Gibt eine neue Datenbank-Session zurück."""
    if _session_factory is None:
        raise RuntimeError("Datenbank nicht initialisiert. Rufe init_database() auf.")
    return _session_factory()
