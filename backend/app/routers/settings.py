from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.settings import SettingsResponse, SettingsUpdate
from app.schemas.common import ApiResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=ApiResponse[SettingsResponse])
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = current_user.settings
    if not settings:
        settings = UserSettings(
            user_id=current_user.id,
            currency=current_user.currency or "INR",
            monthly_income_target=0.0
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    return ApiResponse(
        success=True,
        data=SettingsResponse.model_validate(settings)
    )

@router.put("", response_model=ApiResponse[SettingsResponse])
def update_settings(
    req: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = current_user.settings
    if not settings:
        settings = UserSettings(
            user_id=current_user.id,
            currency=req.currency or current_user.currency or "INR",
            monthly_income_target=req.monthly_income_target or 0.0
        )
        db.add(settings)
    else:
        if req.currency is not None:
            settings.currency = req.currency
            current_user.currency = req.currency
        if req.monthly_income_target is not None:
            settings.monthly_income_target = req.monthly_income_target
            
    db.commit()
    db.refresh(settings)
    return ApiResponse(
        success=True,
        data=SettingsResponse.model_validate(settings),
        message="Settings updated successfully"
    )
