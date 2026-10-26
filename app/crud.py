"""CRUD operations for expenses."""
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


def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).offset(skip).limit(limit).all()
