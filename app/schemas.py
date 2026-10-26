"""Pydantic schemas for request/response validation."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    """Fixed set of known expense/budget categories."""

    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HOUSING = "Housing"
    HEALTHCARE = "Healthcare"
    SHOPPING = "Shopping"
    OTHER = "Other"


class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, examples=["Lunch with client"])
    amount: float = Field(..., gt=0, examples=[12.5])
    category: Optional[Category] = Field(default=None, examples=["Food"])


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetBase(BaseModel):
    category: Category = Field(..., examples=["Food"])
    year: int = Field(..., ge=2000, le=3000, examples=[2025])
    month: int = Field(..., ge=1, le=12, examples=[6])
    monthly_limit: float = Field(..., gt=0, examples=[300.0])


class BudgetCreate(BudgetBase):
    pass


class BudgetOut(BudgetBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetStatus(BaseModel):
    """Current spend vs. limit for a single category/month, with overspend info."""

    category: str
    year: int
    month: int
    monthly_limit: float
    total_spent: float
    remaining: float
    percent_used: float = Field(
        description="total_spent / monthly_limit, expressed as a percentage (e.g. 85.0 = 85%)."
    )
    is_overspent: bool
    overspend_amount: float = Field(
        default=0.0,
        description="Amount spent beyond the monthly_limit; 0 if not overspent.",
    )


class AlertLevel(str, Enum):
    """Severity of a budget alert, based on percent of budget used."""

    WARNING = "warning"  # >= 80% and < 100% of budget used
    EXCEEDED = "exceeded"  # >= 100% of budget used


class BudgetAlert(BaseModel):
    """An alert for a category that has reached a warning or exceeded threshold."""

    category: str
    year: int
    month: int
    monthly_limit: float
    total_spent: float
    percent_used: float
    level: AlertLevel
