from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Literal

CurrencyType = Literal["INR", "USD", "EUR", "GBP"]

class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    currency: Optional[CurrencyType] = "INR"

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_new_password: str = Field(..., min_length=8, max_length=100)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("New password and confirmation do not match")
        return self

class SettingsUpdate(BaseModel):
    currency: Optional[CurrencyType] = "INR"
    monthly_income_target: Optional[float] = Field(0.0, ge=0)

class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    currency: str
    monthly_income_target: float
