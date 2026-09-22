from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from app.schemas.category import CategoryResponse

class BudgetBase(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000, le=2100)

class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    spent: float = 0.0
    remaining: float = 0.0
    percentage: float = 0.0
    status: Literal["Under Budget", "Near Limit", "Over Budget"] = "Under Budget"
    warning_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

class BudgetSummary(BaseModel):
    total_budget: float
    total_spent: float
    total_remaining: float
    overall_percentage: float
    budgets: list[BudgetResponse]
