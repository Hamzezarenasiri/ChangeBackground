import os

from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from Background_changer.settings import settings


async def create_database() -> None:
    """Create a database."""

async def drop_database() -> None:
    """Drop current database."""
    if settings.db_file.exists():
        os.remove(settings.db_file)
