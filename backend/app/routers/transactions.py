import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    PaginationMeta,
)
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user
from app.services.export_service import generate_transactions_csv

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def build_transaction_query(
    db: Session,
    user_id: int,
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
):
    query = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.user_id == user_id)
    )
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if search:
        query = query.filter(Transaction.title.ilike(f"%{search.strip()}%"))
        
    return query

@router.get("", response_model=ApiResponse[TransactionListResponse])
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    sort_by: str = Query("newest", pattern="^(newest|oldest|highest|lowest)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = build_transaction_query(
        db=db,
        user_id=current_user.id,
        type=type,
        category_id=category_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )
    
    total = query.count()
    total_pages = math.ceil(total / limit) if total > 0 else 1

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
    elif sort_by == "highest":
        query = query.order_by(Transaction.amount.desc(), Transaction.id.desc())
    elif sort_by == "lowest":
        query = query.order_by(Transaction.amount.asc(), Transaction.id.asc())
    else: # newest
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    offset = (page - 1) * limit
    transactions = query.offset(offset).limit(limit).all()

    response_data = TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        pagination=PaginationMeta(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
    )
    return ApiResponse(success=True, data=response_data)

@router.get("/export")
def export_transactions(
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = build_transaction_query(
        db=db,
        user_id=current_user.id,
        type=type,
        category_id=category_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
        search=search,
    ).order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
    
    transactions = query.all()
    csv_content = generate_transactions_csv(transactions)
    
    filename = f"expensely_transactions_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )

@router.post("", response_model=ApiResponse[TransactionResponse], status_code=status.HTTP_201_CREATED)
def create_transaction(
    req: TransactionCreate,
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
            detail="Specified category does not exist or is not accessible"
        )
    
    if category.type != req.type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category.name}' is of type '{category.type}', cannot create a '{req.type}' transaction under it."
        )

    transaction = Transaction(
        user_id=current_user.id,
        category_id=req.category_id,
        type=req.type,
        amount=req.amount,
        title=req.title.strip(),
        description=req.description.strip() if req.description else None,
        transaction_date=req.transaction_date,
        payment_method=req.payment_method
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return ApiResponse(
        success=True,
        data=TransactionResponse.model_validate(transaction),
        message="Transaction recorded successfully"
    )

@router.get("/{transaction_id}", response_model=ApiResponse[TransactionResponse])
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return ApiResponse(
        success=True,
        data=TransactionResponse.model_validate(transaction)
    )

@router.put("/{transaction_id}", response_model=ApiResponse[TransactionResponse])
def update_transaction(
    transaction_id: int,
    req: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or access denied"
        )

    if req.category_id is not None:
        cat = db.query(Category).filter(
            Category.id == req.category_id,
            (Category.user_id == current_user.id) | (Category.user_id.is_(None))
        ).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")
        transaction.category_id = req.category_id

    if req.title is not None:
        transaction.title = req.title.strip()
    if req.amount is not None:
        transaction.amount = req.amount
    if req.type is not None:
        transaction.type = req.type
    if req.transaction_date is not None:
        transaction.transaction_date = req.transaction_date
    if req.payment_method is not None:
        transaction.payment_method = req.payment_method
    if req.description is not None:
        transaction.description = req.description.strip() if req.description else None

    db.commit()
    db.refresh(transaction)
    return ApiResponse(
        success=True,
        data=TransactionResponse.model_validate(transaction),
        message="Transaction updated successfully"
    )

@router.delete("/{transaction_id}", response_model=ApiResponse[dict])
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or access denied"
        )
    
    db.delete(transaction)
    db.commit()
    return ApiResponse(
        success=True,
        data={"id": transaction_id},
        message="Transaction deleted successfully"
    )
