from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=ApiResponse[List[CategoryResponse]])
def get_categories(
    type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    )
    if type:
        query = query.filter(Category.type == type)
    categories = query.order_by(Category.name.asc()).all()
    
    result = []
    for c in categories:
        res = CategoryResponse.model_validate(c)
        res.is_default = (c.user_id is None)
        result.append(res)
        
    return ApiResponse(success=True, data=result)

@router.post("", response_model=ApiResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_category(
    req: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if duplicate name under same type for this user
    existing = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
        Category.name.ilike(req.name.strip()),
        Category.type == req.type
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A category named '{req.name.strip()}' already exists for {req.type}."
        )
    
    category = Category(
        user_id=current_user.id,
        name=req.name.strip(),
        type=req.type,
        icon=req.icon or "Tag"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return ApiResponse(
        success=True,
        data=CategoryResponse.model_validate(category),
        message="Category created successfully"
    )

@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
def update_category(
    category_id: int,
    req: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or cannot be modified"
        )
    
    if req.name is not None:
        category.name = req.name.strip()
    if req.type is not None:
        category.type = req.type
    if req.icon is not None:
        category.icon = req.icon
        
    db.commit()
    db.refresh(category)
    return ApiResponse(
        success=True,
        data=CategoryResponse.model_validate(category),
        message="Category updated successfully"
    )

@router.delete("/{category_id}", response_model=ApiResponse[dict])
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or cannot be deleted"
        )
    
    # Requirement 16: Prevent deleting a category if transactions depend on it
    tx_count = db.query(Transaction).filter(
        Transaction.category_id == category_id,
        Transaction.user_id == current_user.id
    ).count()
    if tx_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category '{category.name}' because {tx_count} transaction(s) depend on it. Please reassign or delete those transactions first."
        )
    
    db.delete(category)
    db.commit()
    return ApiResponse(
        success=True,
        data={"id": category_id},
        message="Category deleted successfully"
    )
