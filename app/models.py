"""SQLAlchemy ORM models."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint

from .database import Base


def _utcnow() -> datetime:
    """Return the current UTC time as a naive datetime.

    We compute the time using the timezone-aware API (avoiding the
    deprecated `datetime.utcnow()`), then strip the tzinfo before
    returning. SQLite has no native timezone-aware datetime type, and
    storing a tz-aware value causes a "+00:00" suffix to be persisted
    that breaks SQLite's strftime/extract-based date filtering. Since
    this app only ever works in UTC, storing naive UTC values keeps
    date filtering (e.g. "all expenses in a given year/month") correct.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)


class Budget(Base):
    """A monthly spending limit for a single expense category."""

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("category", "year", "month", name="uq_budget_category_year_month"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    monthly_limit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
