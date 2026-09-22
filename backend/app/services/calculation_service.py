from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.category import Category
from app.schemas.dashboard import (
    CategorySpendingSummary,
    MonthlyTrendPoint,
    DashboardSummary,
    MonthlyReport,
)
from app.schemas.budget import BudgetResponse
from app.schemas.transaction import TransactionResponse

def round_currency(val: float | Decimal) -> float:
    if val is None:
        return 0.0
    d = Decimal(str(val))
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def get_total_balance(db: Session, user_id: int) -> float:
    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == user_id, Transaction.type == "income")
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == user_id, Transaction.type == "expense")
        .scalar()
    )
    return round_currency(Decimal(str(income)) - Decimal(str(expense)))

def get_monthly_metrics(db: Session, user_id: int, month: int, year: int) -> Dict[str, float]:
    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .scalar()
    )
    
    d_income = Decimal(str(income))
    d_expense = Decimal(str(expense))
    d_savings = d_income - d_expense
    
    if d_income > 0:
        d_savings_rate = (d_savings / d_income) * Decimal("100")
    else:
        d_savings_rate = Decimal("0.0")
        
    return {
        "income": round_currency(d_income),
        "expense": round_currency(d_expense),
        "savings": round_currency(d_savings),
        "savings_rate": round(float(d_savings_rate), 1),
    }

def get_budget_statuses(db: Session, user_id: int, month: int, year: int) -> List[BudgetResponse]:
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
        .all()
    )
    results = []
    
    for b in budgets:
        # Sum expenses for this category in this month/year
        spent_amount = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == user_id,
                Transaction.category_id == b.category_id,
                Transaction.type == "expense",
                extract("month", Transaction.transaction_date) == month,
                extract("year", Transaction.transaction_date) == year,
            )
            .scalar()
        )
        d_budget = Decimal(str(b.amount))
        d_spent = Decimal(str(spent_amount))
        d_remaining = max(Decimal("0.0"), d_budget - d_spent)
        
        pct = 0.0
        if d_budget > 0:
            pct = float((d_spent / d_budget) * Decimal("100"))
            
        pct_rounded = round(pct, 1)
        cat_name = b.category.name if b.category else "Category"
        
        if pct_rounded >= 100.0:
            status = "Over Budget"
            warning_msg = f"Your {cat_name} budget has been exceeded."
        elif pct_rounded >= 80.0:
            status = "Near Limit"
            warning_msg = f"{int(pct_rounded)}% of your {cat_name} budget has been used."
        else:
            status = "Under Budget"
            warning_msg = None
            
        res = BudgetResponse(
            id=b.id,
            user_id=b.user_id,
            category_id=b.category_id,
            amount=round_currency(d_budget),
            month=b.month,
            year=b.year,
            spent=round_currency(d_spent),
            remaining=round_currency(d_remaining),
            percentage=pct_rounded,
            status=status,
            warning_message=warning_msg,
            created_at=b.created_at,
            updated_at=b.updated_at,
            category=b.category,
        )
        results.append(res)
        
    return results

def get_top_spending_categories(db: Session, user_id: int, month: int, year: int, limit: int = 5) -> List[CategorySpendingSummary]:
    # Total monthly expense for calculating percentages
    monthly_expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .scalar()
    )
    d_total = Decimal(str(monthly_expense))
    
    rows = (
        db.query(
            Category.id,
            Category.name,
            Category.icon,
            func.coalesce(func.sum(Transaction.amount), 0).label("total_amount")
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .group_by(Category.id, Category.name, Category.icon)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
        .all()
    )
    
    result = []
    for r in rows:
        amount_dec = Decimal(str(r.total_amount))
        pct = 0.0
        if d_total > 0:
            pct = round(float((amount_dec / d_total) * Decimal("100")), 1)
        result.append(
            CategorySpendingSummary(
                category_id=r.id,
                category_name=r.name,
                category_icon=r.icon or "Tag",
                amount=round_currency(amount_dec),
                percentage=pct,
            )
        )
    return result

def get_monthly_trends(db: Session, user_id: int, num_months: int = 6) -> List[MonthlyTrendPoint]:
    """Computes income, expense, and savings trends for the past N months."""
    current_date = date.today()
    month_list = []
    
    for i in range(num_months - 1, -1, -1):
        # calculate month and year going backwards
        m = current_date.month - i
        y = current_date.year
        while m <= 0:
            m += 12
            y -= 1
        month_list.append((m, y))
        
    trends = []
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for m, y in month_list:
        metrics = get_monthly_metrics(db, user_id, m, y)
        label = f"{month_names[m]} {y}"
        trends.append(
            MonthlyTrendPoint(
                month=label,
                month_num=m,
                year=y,
                income=metrics["income"],
                expense=metrics["expense"],
                savings=metrics["savings"],
                savings_rate=metrics["savings_rate"],
            )
        )
    return trends

def build_dashboard_summary(db: Session, user_id: int) -> DashboardSummary:
    now = date.today()
    current_month = now.month
    current_year = now.year
    
    total_balance = get_total_balance(db, user_id)
    monthly_metrics = get_monthly_metrics(db, user_id, current_month, current_year)
    budget_statuses = get_budget_statuses(db, user_id, current_month, current_year)
    
    total_budget = sum(b.amount for b in budget_statuses)
    budget_spent = sum(b.spent for b in budget_statuses)
    budget_remaining = sum(b.remaining for b in budget_statuses)
    budget_used_pct = round((budget_spent / total_budget * 100), 1) if total_budget > 0 else 0.0
    
    warnings = [b.warning_message for b in budget_statuses if b.warning_message is not None]
    
    recent_txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(5)
        .all()
    )
    
    top_categories = get_top_spending_categories(db, user_id, current_month, current_year, limit=5)
    monthly_trends = get_monthly_trends(db, user_id, num_months=6)
    
    return DashboardSummary(
        total_balance=total_balance,
        current_month_income=monthly_metrics["income"],
        current_month_expense=monthly_metrics["expense"],
        current_month_savings=monthly_metrics["savings"],
        savings_rate=monthly_metrics["savings_rate"],
        total_budget=round_currency(total_budget),
        budget_spent=round_currency(budget_spent),
        budget_remaining=round_currency(budget_remaining),
        budget_used_percentage=budget_used_pct,
        budget_warnings=warnings,
        recent_transactions=recent_txs,
        top_spending_categories=top_categories,
        monthly_trends=monthly_trends,
    )
