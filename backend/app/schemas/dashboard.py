from pydantic import BaseModel
from typing import List, Optional
from app.schemas.transaction import TransactionResponse
from app.schemas.budget import BudgetResponse

class CategorySpendingSummary(BaseModel):
    category_id: int
    category_name: str
    category_icon: Optional[str] = "Tag"
    amount: float
    percentage: float

class MonthlyTrendPoint(BaseModel):
    month: str # e.g., "Jan 2026"
    month_num: int
    year: int
    income: float
    expense: float
    savings: float
    savings_rate: float

class DashboardSummary(BaseModel):
    total_balance: float
    current_month_income: float
    current_month_expense: float
    current_month_savings: float
    savings_rate: float
    total_budget: float
    budget_spent: float
    budget_remaining: float
    budget_used_percentage: float
    budget_warnings: List[str]
    recent_transactions: List[TransactionResponse]
    top_spending_categories: List[CategorySpendingSummary]
    monthly_trends: List[MonthlyTrendPoint]

class MonthlyReport(BaseModel):
    month: int
    year: int
    total_income: float
    total_expense: float
    total_savings: float
    savings_rate: float
    highest_spending_category: Optional[CategorySpendingSummary] = None
    transaction_count: int
    budget_status: List[BudgetResponse]
    category_breakdown: List[CategorySpendingSummary]
