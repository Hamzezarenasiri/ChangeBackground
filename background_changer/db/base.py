from sqlalchemy.orm import DeclarativeBase

from background_changer.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
