"""
Expenses Module - Database Models
Expense tracking and categorization
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum as SQLEnum, Text, Boolean
from app.core.database import Base
import enum


class ExpenseCategory(str, enum.Enum):
    """Expense categories"""
    GROCERIES = "Groceries"
    UTILITIES = "Utilities"  # Electricity, water, gas
    RENT = "Rent"
    TRANSPORTATION = "Transportation"  # Fuel, public transport
    HEALTHCARE = "Healthcare"  # Medical, medicines
    EDUCATION = "Education"  # School, courses, books
    ENTERTAINMENT = "Entertainment"  # Movies, dining, subscriptions
    SHOPPING = "Shopping"  # Clothing, electronics, etc.
    INSURANCE = "Insurance"  # Life, health, vehicle
    INVESTMENTS = "Investments"  # Money moved to savings/investments
    LOAN_EMI = "Loan EMI"
    CHARITY = "Charity"
    HOUSEHOLD = "Household"  # Furniture, appliances, maintenance
    PERSONAL_CARE = "Personal Care"  # Salon, gym
    TRAVEL = "Travel"  # Vacations, trips
    GIFTS = "Gifts"
    TAXES = "Taxes"
    OTHER = "Other"


class PaymentMethod(str, enum.Enum):
    """Payment methods"""
    CASH = "Cash"
    DEBIT_CARD = "Debit Card"
    CREDIT_CARD = "Credit Card"
    UPI = "UPI"
    NET_BANKING = "Net Banking"
    CHEQUE = "Cheque"
    WALLET = "Mobile Wallet"
    EMI = "EMI"
    OTHER = "Other"


class RecurringFrequency(str, enum.Enum):
    """Recurring expense frequency"""
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    HALF_YEARLY = "Half-Yearly"
    YEARLY = "Yearly"


class Expense(Base):
    """
    Expense Model

    Tracks all expenses with categorization
    """
    __tablename__ = "expenses"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Basic Details
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)

    # Category and Payment
    category = Column(SQLEnum(ExpenseCategory), nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)

    # Date
    expense_date = Column(Date, nullable=False, index=True)

    # Vendor/Merchant
    vendor = Column(String(255), nullable=True)

    # Location (optional - for tracking where money was spent)
    location = Column(String(255), nullable=True)

    # Receipt
    receipt_number = Column(String(100), nullable=True)
    receipt_image_path = Column(String(500), nullable=True)  # Path to scanned receipt

    # Tags (comma-separated for flexible categorization)
    tags = Column(String(500), nullable=True)  # "essential, monthly, family"

    # Recurring Expense Tracking
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(SQLEnum(RecurringFrequency), nullable=True)
    recurring_group_id = Column(String(50), nullable=True)  # Group related recurring expenses

    # Linked Account (if expense is from a specific savings account withdrawal)
    linked_savings_account_id = Column(Integer, nullable=True)  # Foreign key reference (soft)

    # Budget Tracking
    is_budgeted = Column(Boolean, default=False)
    budget_exceeded = Column(Boolean, default=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Expense(id={self.id}, description='{self.description}', amount={self.amount}, category='{self.category}', date={self.expense_date})>"


class ExpenseBudget(Base):
    """
    Expense Budget Model

    Set monthly/yearly budgets for expense categories
    """
    __tablename__ = "expense_budgets"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Category
    category = Column(SQLEnum(ExpenseCategory), nullable=False, index=True)

    # Budget Amount
    budget_amount = Column(Float, nullable=False)

    # Period
    period_type = Column(String(20), nullable=False)  # "monthly", "yearly"
    period_year = Column(Integer, nullable=True)
    period_month = Column(Integer, nullable=True)  # 1-12 for monthly budgets

    # Tracking
    spent_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, nullable=True)
    percentage_used = Column(Float, default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    is_exceeded = Column(Boolean, default=False)

    # Alert Settings
    alert_at_percentage = Column(Integer, default=80)  # Alert when 80% spent
    alert_triggered = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ExpenseBudget(id={self.id}, category='{self.category}', budget={self.budget_amount}, spent={self.spent_amount})>"


class ExpenseCategory_Custom(Base):
    """
    Custom Expense Categories

    Allow users to create custom categories beyond the predefined ones
    """
    __tablename__ = "expense_categories_custom"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Category Details
    category_name = Column(String(100), nullable=False, unique=True)
    category_icon = Column(String(50), nullable=True)  # Icon name/emoji
    category_color = Column(String(20), nullable=True)  # Hex color code

    # Parent category (optional - for subcategories)
    parent_category = Column(SQLEnum(ExpenseCategory), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ExpenseCategory_Custom(id={self.id}, name='{self.category_name}')>"
