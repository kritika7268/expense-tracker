from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.dashboard import (
    MonthlyTrendPoint,
    CategorySpendingSummary,
    MonthlyReport,
)
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user
from app.services.calculation_service import (
    get_monthly_trends,
    get_top_spending_categories,
    get_monthly_metrics,
    get_budget_statuses,
    round_currency,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/monthly", response_model=ApiResponse[List[MonthlyTrendPoint]])
def get_monthly_analytics(
    months: int = Query(12, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trends = get_monthly_trends(db, current_user.id, num_months=months)
    return ApiResponse(success=True, data=trends)

@router.get("/categories", response_model=ApiResponse[List[CategorySpendingSummary]])
def get_category_analytics(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year
    # All spending categories for the selected period
    categories = get_top_spending_categories(db, current_user.id, target_month, target_year, limit=50)
    return ApiResponse(success=True, data=categories)

@router.get("/income-expense", response_model=ApiResponse[List[MonthlyTrendPoint]])
def get_income_expense_analytics(
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trends = get_monthly_trends(db, current_user.id, num_months=months)
    return ApiResponse(success=True, data=trends)

@router.get("/savings", response_model=ApiResponse[List[dict]])
def get_savings_analytics(
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trends = get_monthly_trends(db, current_user.id, num_months=months)
    data = [
        {
            "month": t.month,
            "savings": t.savings,
            "savings_rate": t.savings_rate,
            "income": t.income,
            "expense": t.expense,
        }
        for t in trends
    ]
    return ApiResponse(success=True, data=data)

@router.get("/report", response_model=ApiResponse[MonthlyReport])
def get_monthly_report(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year
    
    metrics = get_monthly_metrics(db, current_user.id, target_month, target_year)
    category_breakdown = get_top_spending_categories(db, current_user.id, target_month, target_year, limit=50)
    highest_cat = category_breakdown[0] if category_breakdown else None
    
    tx_count = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            extract("month", Transaction.transaction_date) == target_month,
            extract("year", Transaction.transaction_date) == target_year,
        )
        .count()
    )
    
    budget_status = get_budget_statuses(db, current_user.id, target_month, target_year)
    
    report = MonthlyReport(
        month=target_month,
        year=target_year,
        total_income=metrics["income"],
        total_expense=metrics["expense"],
        total_savings=metrics["savings"],
        savings_rate=metrics["savings_rate"],
        highest_spending_category=highest_cat,
        transaction_count=tx_count,
        budget_status=budget_status,
        category_breakdown=category_breakdown,
    )
    return ApiResponse(success=True, data=report)
