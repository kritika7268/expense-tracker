from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.settings import ProfileUpdateRequest, PasswordChangeRequest
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user
from app.utils.security import verify_password, hash_password

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ApiResponse[UserResponse])
def get_profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Profile retrieved successfully"
    )

@router.put("", response_model=ApiResponse[UserResponse])
def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = req.name.strip()
    if req.currency:
        current_user.currency = req.currency
        if current_user.settings:
            current_user.settings.currency = req.currency
            
    db.commit()
    db.refresh(current_user)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Profile updated successfully"
    )

@router.put("/password", response_model=ApiResponse[dict])
def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
        
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return ApiResponse(
        success=True,
        data={"message": "Password updated successfully"},
        message="Password changed successfully"
    )
