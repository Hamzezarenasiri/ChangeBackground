from sqlalchemy.orm import DeclarativeBase
from Background_changer.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta

