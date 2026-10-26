"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, examples=["Lunch with client"])
    amount: float = Field(..., gt=0, examples=[12.5])
    category: Optional[str] = Field(default=None, examples=["Food"])


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
