from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.category import Category
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummary
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user
from app.services.calculation_service import get_budget_statuses, round_currency

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("", response_model=ApiResponse[BudgetSummary])
def get_budgets(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = date.today()
    target_month = month or now.month
    target_year = year or now.year
    
    statuses = get_budget_statuses(db, current_user.id, target_month, target_year)
    total_budget = sum(b.amount for b in statuses)
    total_spent = sum(b.spent for b in statuses)
    total_remaining = sum(b.remaining for b in statuses)
    overall_percentage = round((total_spent / total_budget * 100), 1) if total_budget > 0 else 0.0
    
    summary = BudgetSummary(
        total_budget=round_currency(total_budget),
        total_spent=round_currency(total_spent),
        total_remaining=round_currency(total_remaining),
        overall_percentage=overall_percentage,
        budgets=statuses
    )
    return ApiResponse(success=True, data=summary)

@router.post("", response_model=ApiResponse[BudgetResponse], status_code=status.HTTP_201_CREATED)
def create_budget(
    req: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify category belongs to user or is default
    category = db.query(Category).filter(
        Category.id == req.category_id,
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    if category.type != "expense":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budgets can only be set for expense categories."
        )

    # Check if budget already exists for this month & year
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == req.category_id,
        Budget.month == req.month,
        Budget.year == req.year
    ).first()
    
    if existing:
        # Upsert: update existing budget amount
        existing.amount = req.amount
        db.commit()
        db.refresh(existing)
        target_budget = existing
    else:
        budget = Budget(
            user_id=current_user.id,
            category_id=req.category_id,
            amount=req.amount,
            month=req.month,
            year=req.year
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        target_budget = budget

    statuses = get_budget_statuses(db, current_user.id, req.month, req.year)
    matched = next((b for b in statuses if b.id == target_budget.id), None)
    return ApiResponse(
        success=True,
        data=matched or BudgetResponse.model_validate(target_budget),
        message="Budget saved successfully"
    )

@router.get("/{budget_id}", response_model=ApiResponse[BudgetResponse])
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    statuses = get_budget_statuses(db, current_user.id, budget.month, budget.year)
    matched = next((b for b in statuses if b.id == budget.id), None)
    return ApiResponse(success=True, data=matched or BudgetResponse.model_validate(budget))

@router.put("/{budget_id}", response_model=ApiResponse[BudgetResponse])
def update_budget(
    budget_id: int,
    req: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    if req.amount is not None:
        budget.amount = req.amount
    if req.category_id is not None:
        budget.category_id = req.category_id
    if req.month is not None:
        budget.month = req.month
    if req.year is not None:
        budget.year = req.year

    db.commit()
    db.refresh(budget)
    
    statuses = get_budget_statuses(db, current_user.id, budget.month, budget.year)
    matched = next((b for b in statuses if b.id == budget.id), None)
    return ApiResponse(
        success=True,
        data=matched or BudgetResponse.model_validate(budget),
        message="Budget updated successfully"
    )

@router.delete("/{budget_id}", response_model=ApiResponse[dict])
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    db.delete(budget)
    db.commit()
    return ApiResponse(success=True, data={"id": budget_id}, message="Budget deleted successfully")
