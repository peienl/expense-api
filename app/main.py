"""FastAPI application exposing an Expenses API backed by SQLite."""
from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense API",
    description="A simple FastAPI starter for tracking expenses, backed by SQLite.",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["health"])
def read_root():
    return {"message": "Expense API is running"}


@app.post("/expenses", response_model=schemas.ExpenseOut, status_code=201, tags=["expenses"])
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense record."""
    return crud.create_expense(db=db, expense=expense)


@app.get("/expenses", response_model=List[schemas.ExpenseOut], tags=["expenses"])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of expenses."""
    return crud.get_expenses(db=db, skip=skip, limit=limit)
