from datetime import date
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.dashboard import (
    DashboardSummary,
    CategorySpendingSummary,
    MonthlyTrendPoint,
)
from app.schemas.transaction import TransactionResponse
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user
from app.services.calculation_service import (
    build_dashboard_summary,
    get_top_spending_categories,
    get_monthly_trends,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    summary = build_dashboard_summary(db, current_user.id)
    return ApiResponse(success=True, data=summary)

@router.get("/recent-transactions", response_model=ApiResponse[List[TransactionResponse]])
def get_recent_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recent = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(5)
        .all()
    )
    return ApiResponse(
        success=True,
        data=[TransactionResponse.model_validate(t) for t in recent]
    )

@router.get("/category-summary", response_model=ApiResponse[List[CategorySpendingSummary]])
def get_category_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = date.today()
    top = get_top_spending_categories(db, current_user.id, now.month, now.year, limit=5)
    return ApiResponse(success=True, data=top)

@router.get("/monthly-summary", response_model=ApiResponse[List[MonthlyTrendPoint]])
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trends = get_monthly_trends(db, current_user.id, num_months=6)
    return ApiResponse(success=True, data=trends)
