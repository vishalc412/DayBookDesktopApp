"""
Account Pydantic Schemas
Request/Response validation models
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.shared.enums import AccountType


class AccountCreate(BaseModel):
    """Schema for creating an account"""
    code: str = Field(..., min_length=1, max_length=20, description="Account code")
    name: str = Field(..., min_length=1, max_length=200, description="Account name")
    account_type: AccountType
    parent_id: Optional[str] = None

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        """Validate account code format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Account code must be alphanumeric')
        return v.upper()


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None


class AccountResponse(BaseModel):
    """Schema for account response"""
    id: str
    code: str
    name: str
    account_type: AccountType
    parent_id: Optional[str]
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountBalanceUpdate(BaseModel):
    """Schema for balance updates (internal use)"""
    account_id: str
    amount: Decimal
    reason: str
