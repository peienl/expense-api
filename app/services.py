"""Service layer: business logic for budgets and overspend detection.

This module sits between the routers (`app/main.py`) and the repository
layer (`app/crud.py`). All domain rules — such as preventing duplicate
budgets, computing percent-of-budget-used, and classifying alert
severity — live here.

Routers must only call into this module; they must never compute these
values themselves.
"""
import re
from typing import List, Tuple

from sqlalchemy.orm import Session

from . import crud, schemas

# Thresholds (as a percentage of monthly_limit) used to classify alerts.
WARNING_THRESHOLD_PERCENT = 80.0
EXCEEDED_THRESHOLD_PERCENT = 100.0

_YEAR_MONTH_PATTERN = re.compile(r"^(\d{4})-(\d{2})$")


class DuplicateBudgetError(Exception):
    """Raised when a budget already exists for the given category/year/month."""

    def __init__(self, category: str, year: int, month: int) -> None:
        self.category = category
        self.year = year
        self.month = month
        super().__init__(
            f"A budget for category={category!r}, year={year}, month={month} already exists."
        )


class InvalidMonthFormatError(Exception):
    """Raised when a month path parameter is not in 'YYYY-MM' format."""

    def __init__(self, raw_value: str) -> None:
        self.raw_value = raw_value
        super().__init__(
            f"Invalid month format {raw_value!r}; expected 'YYYY-MM' (e.g. '2025-06')."
        )


def parse_year_month(raw_value: str) -> Tuple[int, int]:
    """Parse a 'YYYY-MM' string into (year, month).

    Raises:
        InvalidMonthFormatError: if the value does not match 'YYYY-MM',
            or if the month is not between 1 and 12.
    """
    match = _YEAR_MONTH_PATTERN.match(raw_value)
    if match is None:
        raise InvalidMonthFormatError(raw_value)

    year, month = int(match.group(1)), int(match.group(2))
    if not (1 <= month <= 12):
        raise InvalidMonthFormatError(raw_value)

    return year, month


def create_budget(db: Session, budget: schemas.BudgetCreate) -> schemas.BudgetOut:
    """Create a new monthly budget limit for a category.

    Enforces that only one budget can exist per category/year/month.

    Raises:
        DuplicateBudgetError: if a budget already exists for this
            category/year/month combination.
    """
    existing = crud.get_budget_by_category_month(
        db, category=budget.category, year=budget.year, month=budget.month
    )
    if existing is not None:
        raise DuplicateBudgetError(
            category=budget.category, year=budget.year, month=budget.month
        )

    db_budget = crud.create_budget(db, budget)
    return schemas.BudgetOut.model_validate(db_budget)


def _build_budget_status(
    db: Session, db_budget: "crud.models.Budget"
) -> schemas.BudgetStatus:
    """Compute a single BudgetStatus from a Budget row, by looking up actual spend."""
    total_spent = crud.get_total_spent_for_category_month(
        db, category=db_budget.category, year=db_budget.year, month=db_budget.month
    )

    remaining = db_budget.monthly_limit - total_spent
    percent_used = (
        (total_spent / db_budget.monthly_limit) * 100.0
        if db_budget.monthly_limit > 0
        else 0.0
    )
    is_overspent = total_spent > db_budget.monthly_limit
    overspend_amount = max(total_spent - db_budget.monthly_limit, 0.0)

    return schemas.BudgetStatus(
        category=db_budget.category,
        year=db_budget.year,
        month=db_budget.month,
        monthly_limit=db_budget.monthly_limit,
        total_spent=total_spent,
        remaining=remaining,
        percent_used=percent_used,
        is_overspent=is_overspent,
        overspend_amount=overspend_amount,
    )


def get_budget_statuses_for_month(
    db: Session, year: int, month: int
) -> List[schemas.BudgetStatus]:
    """Return budget-vs-actual-spend status for every category budgeted in a given month."""
    db_budgets = crud.get_budgets_by_month(db, year=year, month=month)
    return [_build_budget_status(db, b) for b in db_budgets]


def get_alerts_for_month(db: Session, year: int, month: int) -> List[schemas.BudgetAlert]:
    """Return alerts for categories at/above the warning or exceeded thresholds.

    A category is included only if its spend has reached at least
    WARNING_THRESHOLD_PERCENT (80%) of its monthly_limit. Categories at or
    above EXCEEDED_THRESHOLD_PERCENT (100%) are classified as "exceeded";
    the rest are classified as "warning".
    """
    statuses = get_budget_statuses_for_month(db, year=year, month=month)
    alerts: List[schemas.BudgetAlert] = []

    for status in statuses:
        if status.percent_used >= EXCEEDED_THRESHOLD_PERCENT:
            level = schemas.AlertLevel.EXCEEDED
        elif status.percent_used >= WARNING_THRESHOLD_PERCENT:
            level = schemas.AlertLevel.WARNING
        else:
            continue

        alerts.append(
            schemas.BudgetAlert(
                category=status.category,
                year=status.year,
                month=status.month,
                monthly_limit=status.monthly_limit,
                total_spent=status.total_spent,
                percent_used=status.percent_used,
                level=level,
            )
        )

    return alerts
