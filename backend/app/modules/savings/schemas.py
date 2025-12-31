"""
Savings Module - Pydantic Schemas
Request and response models for savings API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from .models import AccountType, AccountStatus, EntryType, CompoundingFrequency


# ==================== Account Schemas ====================

class SavingsAccountBase(BaseModel):
    """Base schema for savings account"""
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: AccountType
    account_number: Optional[str] = Field(None, max_length=100)
    bank_or_institution: str = Field(..., min_length=1, max_length=255)
    branch: Optional[str] = Field(None, max_length=255)
    opening_date: date
    maturity_date: Optional[date] = None
    initial_amount: float = Field(0.0, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    tenure_months: Optional[int] = Field(None, ge=1)
    compounding_frequency: Optional[CompoundingFrequency] = None
    monthly_installment: Optional[float] = Field(None, ge=0)
    nominee_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class SavingsAccountCreate(SavingsAccountBase):
    """Schema for creating savings account"""
    pass


class SavingsAccountUpdate(BaseModel):
    """Schema for updating savings account"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bank_or_institution: Optional[str] = Field(None, min_length=1, max_length=255)
    branch: Optional[str] = Field(None, max_length=255)
    maturity_date: Optional[date] = None
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[AccountStatus] = None
    nominee_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class SavingsAccountResponse(SavingsAccountBase):
    """Schema for savings account response"""
    id: int
    current_balance: float
    expected_maturity_amount: Optional[float]
    actual_maturity_amount: Optional[float]
    total_interest_earned: float
    status: AccountStatus
    closing_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Entry Schemas ====================

class SavingsEntryBase(BaseModel):
    """Base schema for savings entry"""
    entry_type: EntryType
    entry_date: date
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    reference_number: Optional[str] = Field(None, max_length=100)


class SavingsEntryCreate(SavingsEntryBase):
    """Schema for creating savings entry"""
    account_id: int


class SavingsEntryResponse(SavingsEntryBase):
    """Schema for savings entry response"""
    id: int
    account_id: int
    balance_after: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Dashboard Schemas ====================

class SavingsSummary(BaseModel):
    """Summary statistics for savings dashboard"""
    total_accounts: int
    active_accounts: int
    total_savings: float
    total_interest_earned: float
    maturing_soon_count: int  # Next 30 days
    maturing_soon_amount: float


class AccountSummary(BaseModel):
    """Summary for a single account"""
    id: int
    account_name: str
    account_type: AccountType
    bank_or_institution: str
    current_balance: float
    interest_rate: Optional[float]
    maturity_date: Optional[date]
    days_to_maturity: Optional[int]
    expected_maturity_amount: Optional[float]
    status: AccountStatus


class MaturityItem(BaseModel):
    """Maturity schedule item"""
    account_id: int
    account_name: str
    account_type: AccountType
    bank_or_institution: str
    maturity_date: date
    expected_amount: float
    current_balance: float
    days_remaining: int


# ==================== Calculation Request Schemas ====================

class ROICalculationRequest(BaseModel):
    """Request for ROI calculation"""
    principal: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0, le=100)
    tenure_months: int = Field(..., gt=0)
    compounding_frequency: Optional[CompoundingFrequency] = CompoundingFrequency.YEARLY


class RDCalculationRequest(BaseModel):
    """Request for Recurring Deposit calculation"""
    monthly_installment: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0, le=100)
    tenure_months: int = Field(..., gt=0)


class PPFCalculationRequest(BaseModel):
    """Request for PPF calculation"""
    annual_deposit: float = Field(..., gt=0, le=150000)  # Max 1.5 lakh
    interest_rate: float = Field(7.1, gt=0, le=100)  # Current PPF rate
    years: int = Field(15, ge=15)  # Minimum 15 years


# ==================== Goal Schemas ====================

class SavingsGoalCreate(BaseModel):
    """Schema for creating savings goal"""
    goal_name: str = Field(..., min_length=1, max_length=255)
    target_amount: float = Field(..., gt=0)
    target_date: Optional[date] = None
    description: Optional[str] = None


class SavingsGoalResponse(BaseModel):
    """Schema for savings goal response"""
    id: int
    goal_name: str
    target_amount: float
    current_amount: float
    target_date: Optional[date]
    achieved_date: Optional[date]
    is_achieved: bool
    description: Optional[str]
    progress_percentage: float = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
