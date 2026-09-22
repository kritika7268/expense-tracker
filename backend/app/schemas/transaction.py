from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List, Literal
from app.schemas.category import CategoryResponse

PaymentMethodType = Literal["Cash", "UPI", "Debit Card", "Credit Card", "Bank Transfer", "Other"]

class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    type: Literal["income", "expense"]
    category_id: int
    transaction_date: date
    payment_method: PaymentMethodType
    description: Optional[str] = Field(None, max_length=1000)

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None
    payment_method: Optional[PaymentMethodType] = None
    description: Optional[str] = Field(None, max_length=1000)

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    pagination: PaginationMeta
