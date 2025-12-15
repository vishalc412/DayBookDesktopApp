"""
Transaction Pydantic Schemas
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.shared.enums import TransactionStatus, TransactionSource


class TransactionLineCreate(BaseModel):
    """Schema for creating a transaction line"""
    account_id: str
    description: Optional[str] = None
    debit: Decimal = Field(Decimal("0.00"), ge=0)
    credit: Decimal = Field(Decimal("0.00"), ge=0)

    @field_validator('debit', 'credit')
    @classmethod
    def validate_amounts(cls, v):
        """Ensure amounts are positive"""
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    def model_post_init(self, __context):
        """Validate that exactly one of debit or credit is non-zero"""
        if self.debit > 0 and self.credit > 0:
            raise ValueError("A line cannot have both debit and credit")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("A line must have either debit or credit")


class TransactionLineResponse(BaseModel):
    """Schema for transaction line response"""
    id: str
    account_id: str
    line_number: int
    description: Optional[str]
    debit: Decimal
    credit: Decimal

    class Config:
        from_attributes = True


class JournalEntryCreate(BaseModel):
    """Schema for creating a journal entry"""
    date: datetime
    description: str = Field(..., min_length=1, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    lines: List[TransactionLineCreate] = Field(..., min_length=2)

    @field_validator('lines')
    @classmethod
    def validate_lines(cls, v):
        """Validate minimum lines and balance"""
        if len(v) < 2:
            raise ValueError("A transaction must have at least 2 lines (double-entry)")

        total_debit = sum(line.debit for line in v)
        total_credit = sum(line.credit for line in v)

        if total_debit != total_credit:
            raise ValueError(
                f"Debits ({total_debit}) must equal credits ({total_credit})"
            )

        return v


class JournalEntryUpdate(BaseModel):
    """Schema for updating a draft journal entry"""
    date: Optional[datetime] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    lines: Optional[List[TransactionLineCreate]] = None

    @field_validator('lines')
    @classmethod
    def validate_lines(cls, v):
        """Validate lines if provided"""
        if v is not None:
            if len(v) < 2:
                raise ValueError("A transaction must have at least 2 lines")

            total_debit = sum(line.debit for line in v)
            total_credit = sum(line.credit for line in v)

            if total_debit != total_credit:
                raise ValueError(
                    f"Debits ({total_debit}) must equal credits ({total_credit})"
                )

        return v


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response"""
    id: str
    entry_number: str
    date: datetime
    description: str
    reference: Optional[str]
    status: TransactionStatus
    source: TransactionSource
    excel_sync_status: str
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    lines: List[TransactionLineResponse]
    created_at: datetime
    posted_at: Optional[datetime]

    class Config:
        from_attributes = True


class PostTransactionRequest(BaseModel):
    """Schema for posting a transaction"""
    confirm: bool = Field(..., description="Must be true to post")

    @field_validator('confirm')
    @classmethod
    def validate_confirm(cls, v):
        if not v:
            raise ValueError("Must confirm posting")
        return v


class ReverseTransactionRequest(BaseModel):
    """Schema for reversing a transaction"""
    reason: str = Field(..., min_length=1, max_length=500)
    date: Optional[datetime] = None  # Reversal date, defaults to today
