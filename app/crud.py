"""Repository layer: direct database access for expenses and budgets.

Functions here perform raw CRUD/query operations only. Any domain logic
(e.g. computing overspend, enforcing business rules) belongs in
`app/services.py`, not here.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


def create_expense(db: Session, expense: schemas.ExpenseCreate) -> models.Expense:
    db_expense = models.Expense(
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Expense]:
    return db.query(models.Expense).offset(skip).limit(limit).all()


def get_total_spent_for_category_month(
    db: Session, category: str, year: int, month: int
) -> float:
    """Sum the amount of all expenses for a category within a given year/month."""
    total: Optional[float] = (
        db.query(func.sum(models.Expense.amount))
        .filter(
            models.Expense.category == category,
            func.extract("year", models.Expense.created_at) == year,
            func.extract("month", models.Expense.created_at) == month,
        )
        .scalar()
    )
    return total or 0.0


def create_budget(db: Session, budget: schemas.BudgetCreate) -> models.Budget:
    db_budget = models.Budget(
        category=budget.category,
        year=budget.year,
        month=budget.month,
        monthly_limit=budget.monthly_limit,
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_budget_by_category_month(
    db: Session, category: str, year: int, month: int
) -> Optional[models.Budget]:
    return (
        db.query(models.Budget)
        .filter(
            models.Budget.category == category,
            models.Budget.year == year,
            models.Budget.month == month,
        )
        .first()
    )


def get_budgets(db: Session, skip: int = 0, limit: int = 100) -> List[models.Budget]:
    return db.query(models.Budget).offset(skip).limit(limit).all()


def get_budgets_by_month(db: Session, year: int, month: int) -> List[models.Budget]:
    """Return all category budgets configured for a given year/month."""
    return (
        db.query(models.Budget)
        .filter(models.Budget.year == year, models.Budget.month == month)
        .all()
    )
