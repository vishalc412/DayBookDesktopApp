"""
DayBook Pydantic Schemas
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List


class DayBookEntryCreate(BaseModel):
    """Schema for creating a DayBook entry"""

    description: str = Field(..., min_length=1, max_length=500)
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    reference: Optional[str] = Field(None, max_length=100)


class DayBookEntryUpdate(BaseModel):
    """Schema for updating a DayBook entry"""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    debit_amount: Optional[Decimal] = Field(None, ge=0)
    credit_amount: Optional[Decimal] = Field(None, ge=0)
    reference: Optional[str] = Field(None, max_length=100)


class DayBookEntryResponse(BaseModel):
    """Schema for DayBook entry response"""

    id: str
    entry_number: str
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance: Decimal
    reference: Optional[str]
    created_at: datetime
    date: date

    model_config = {"from_attributes": True}


class DayBookPageResponse(BaseModel):
    """Schema for DayBook page response"""

    id: str
    book_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    is_locked: bool
    entries: List[DayBookEntryResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DayBookSearchRequest(BaseModel):
    """Schema for searching DayBook entries"""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    entry_number: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class ReportRequest(BaseModel):
    """Schema for requesting a report"""

    start_date: date
    end_date: date


class DayBookReportSummary(BaseModel):
    """Summary statistics for the report"""

    opening_balance: Decimal
    closing_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    net_change: Decimal
    entry_count: int


class DayBookReportResponse(BaseModel):
    """Full report response"""

    period_start: date
    period_end: date
    summary: DayBookReportSummary
    entries: List[DayBookEntryResponse]

    model_config = {"from_attributes": True}
