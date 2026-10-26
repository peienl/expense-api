"""SQLAlchemy ORM models."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from .database import Base


def _utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
