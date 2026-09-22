from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.schemas.common import ApiResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.deps import get_current_user
from app.services.auth_service import initialize_user_defaults

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    # Hash password & create user
    user = User(
        name=req.name.strip(),
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        currency=req.currency or "INR"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default categories and user settings
    initialize_user_defaults(db, user)

    # Generate JWT
    token = create_access_token({"sub": str(user.id)})
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        ),
        message="User registered successfully"
    )

@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token({"sub": str(user.id)})
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        ),
        message="Login successful"
    )

@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Current user profile fetched successfully"
    )
