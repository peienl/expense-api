"""FastAPI application exposing an Expenses API backed by SQLite."""
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas, services
from .database import SessionLocal, engine

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense API",
    description="A simple FastAPI starter for tracking expenses, backed by SQLite.",
    version="1.0.0",
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["health"])
def read_root() -> dict:
    return {"message": "Expense API is running"}


@app.post("/expenses", response_model=schemas.ExpenseOut, status_code=201, tags=["expenses"])
def create_expense(
    expense: schemas.ExpenseCreate, db: Session = Depends(get_db)
) -> models.Expense:
    """Create a new expense record."""
    return crud.create_expense(db=db, expense=expense)


@app.get("/expenses", response_model=List[schemas.ExpenseOut], tags=["expenses"])
def read_expenses(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[models.Expense]:
    """Retrieve a list of expenses."""
    return crud.get_expenses(db=db, skip=skip, limit=limit)


@app.post("/budgets", response_model=schemas.BudgetOut, status_code=201, tags=["budgets"])
def create_budget(
    budget: schemas.BudgetCreate, db: Session = Depends(get_db)
) -> schemas.BudgetOut:
    """Set a monthly spending limit for a category."""
    try:
        return services.create_budget(db=db, budget=budget)
    except services.DuplicateBudgetError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get(
    "/budgets/{month}",
    response_model=List[schemas.BudgetStatus],
    tags=["budgets"],
)
def read_budget_status(month: str, db: Session = Depends(get_db)) -> List[schemas.BudgetStatus]:
    """Budget vs. actual spend per category for a given month ('YYYY-MM')."""
    try:
        year, month_number = services.parse_year_month(month)
    except services.InvalidMonthFormatError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return services.get_budget_statuses_for_month(db, year=year, month=month_number)


@app.get(
    "/alerts/{month}",
    response_model=List[schemas.BudgetAlert],
    tags=["budgets"],
)
def read_alerts(month: str, db: Session = Depends(get_db)) -> List[schemas.BudgetAlert]:
    """Categories at or above 80% (warning) or 100% (exceeded) of their budget for a given month ('YYYY-MM')."""
    try:
        year, month_number = services.parse_year_month(month)
    except services.InvalidMonthFormatError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return services.get_alerts_for_month(db, year=year, month=month_number)
