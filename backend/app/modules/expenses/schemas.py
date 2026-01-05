"""
Expenses Module - Pydantic Schemas
Request and response models for expenses API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import date, datetime
from .models import ExpenseCategory, PaymentMethod, RecurringFrequency


# ==================== Expense Schemas ====================

class ExpenseBase(BaseModel):
    """Base schema for expense"""
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    category: ExpenseCategory
    payment_method: PaymentMethod
    expense_date: date
    vendor: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    receipt_number: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    is_recurring: bool = False
    recurring_frequency: Optional[RecurringFrequency] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Schema for creating expense"""
    linked_savings_account_id: Optional[int] = None


class ExpenseUpdate(BaseModel):
    """Schema for updating expense"""
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    payment_method: Optional[PaymentMethod] = None
    expense_date: Optional[date] = None
    vendor: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    receipt_number: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    """Schema for expense response"""
    id: int
    receipt_image_path: Optional[str]
    recurring_group_id: Optional[str]
    linked_savings_account_id: Optional[int]
    is_budgeted: bool
    budget_exceeded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseBulkCreate(BaseModel):
    """Schema for bulk creating expenses"""
    expenses: List[ExpenseCreate]


# ==================== Budget Schemas ====================

class ExpenseBudgetBase(BaseModel):
    """Base schema for expense budget"""
    category: ExpenseCategory
    budget_amount: float = Field(..., gt=0)
    period_type: str = Field(..., pattern="^(monthly|yearly)$")
    period_year: Optional[int] = Field(None, ge=2020, le=2100)
    period_month: Optional[int] = Field(None, ge=1, le=12)
    alert_at_percentage: int = Field(80, ge=0, le=100)


class ExpenseBudgetCreate(ExpenseBudgetBase):
    """Schema for creating expense budget"""
    pass


class ExpenseBudgetUpdate(BaseModel):
    """Schema for updating expense budget"""
    budget_amount: Optional[float] = Field(None, gt=0)
    alert_at_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class ExpenseBudgetResponse(ExpenseBudgetBase):
    """Schema for expense budget response"""
    id: int
    spent_amount: float
    remaining_amount: Optional[float]
    percentage_used: float
    is_active: bool
    is_exceeded: bool
    alert_triggered: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class ExpenseSummary(BaseModel):
    """Summary statistics for expenses dashboard"""
    total_expenses: float
    total_count: int
    transaction_count: int  # Alias for total_count for frontend compatibility
    this_month_expenses: float
    this_month_count: int
    average_expense: float
    top_category: str
    top_category_amount: float


class CategorySummary(BaseModel):
    """Expense summary by category"""
    category: str
    total_amount: float
    amount: float  # Alias for total_amount for frontend compatibility
    count: int
    percentage: float
    average: float


class MonthlySummary(BaseModel):
    """Monthly expense summary"""
    month: str  # "2025-01"
    year: int
    month_num: int
    total_expenses: float
    count: int
    categories: Dict[str, float]  # category -> amount


class PaymentMethodSummary(BaseModel):
    """Summary by payment method"""
    payment_method: str
    total_amount: float
    count: int
    percentage: float


class ExpenseTrend(BaseModel):
    """Expense trend data"""
    date: date
    amount: float
    category: str


class BudgetStatus(BaseModel):
    """Budget status for a category"""
    category: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float
    is_exceeded: bool
    is_alert: bool  # True if alert threshold is reached (e.g., 80% budget used)
    days_remaining: int  # In period


class TopExpense(BaseModel):
    """Top expense item"""
    id: int
    description: str
    amount: float
    category: str
    expense_date: date
    vendor: Optional[str]


# ==================== Report Schemas ====================

class ExpenseReportRequest(BaseModel):
    """Request for expense report"""
    start_date: date
    end_date: date
    categories: Optional[List[ExpenseCategory]] = None
    payment_methods: Optional[List[PaymentMethod]] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = None


class MonthlyReportRequest(BaseModel):
    """Request for monthly report"""
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)


class YearlyReportRequest(BaseModel):
    """Request for yearly report"""
    year: int = Field(..., ge=2020, le=2100)


class SavingsVsExpensesRequest(BaseModel):
    """Request for savings vs expenses comparison"""
    months: int = Field(12, ge=1, le=36)


# ==================== Custom Category Schemas ====================

class CustomCategoryCreate(BaseModel):
    """Schema for creating custom category"""
    category_name: str = Field(..., min_length=1, max_length=100)
    category_icon: Optional[str] = Field(None, max_length=50)
    category_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    parent_category: Optional[ExpenseCategory] = None


class CustomCategoryResponse(BaseModel):
    """Schema for custom category response"""
    id: int
    category_name: str
    category_icon: Optional[str]
    category_color: Optional[str]
    parent_category: Optional[ExpenseCategory]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
