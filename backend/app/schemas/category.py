from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["income", "expense"]
    icon: Optional[str] = Field("Tag", max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[Literal["income", "expense"]] = None
    icon: Optional[str] = Field(None, max_length=50)

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    created_at: datetime
    is_default: bool = False
