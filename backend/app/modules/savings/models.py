"""
Savings Module - Database Models
Accounts and entries for savings & investments tracking
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AccountType(str, enum.Enum):
    """Savings account types"""
    FIXED_DEPOSIT = "Fixed Deposit"
    RECURRING_DEPOSIT = "Recurring Deposit"
    PPF = "PPF"
    NSC = "NSC"
    MUTUAL_FUND_SIP = "Mutual Fund SIP"
    BONDS = "Bonds"
    SAVINGS_ACCOUNT = "Savings Account"
    PRECIOUS_METALS = "Precious Metals"
    DIGITAL_GOLD = "Digital Gold"
    STOCKS = "Stocks"
    OTHER = "Other"


class AccountStatus(str, enum.Enum):
    """Account status"""
    ACTIVE = "Active"
    MATURED = "Matured"
    CLOSED = "Closed"
    PREMATURE_WITHDRAWAL = "Premature Withdrawal"


class EntryType(str, enum.Enum):
    """Transaction entry types"""
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    INTEREST_CREDIT = "Interest Credit"
    DIVIDEND = "Dividend"
    MATURITY = "Maturity"
    FEE = "Fee"


class CompoundingFrequency(str, enum.Enum):
    """Compounding frequency"""
    YEARLY = "Yearly"
    HALF_YEARLY = "Half-Yearly"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    DAILY = "Daily"


class SavingsAccount(Base):
    """
    Savings Account Model

    Represents various savings and investment accounts:
    - Fixed Deposits, Recurring Deposits
    - PPF, NSC, Bonds
    - Mutual Fund SIP
    - Savings accounts
    - Precious metals accounts
    """
    __tablename__ = "savings_accounts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Basic Information
    account_name = Column(String(255), nullable=False, index=True)
    account_type = Column(SQLEnum(AccountType), nullable=False, index=True)
    account_number = Column(String(100), nullable=True)  # Optional account number

    # Institution Details
    bank_or_institution = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=True)

    # Account Dates
    opening_date = Column(Date, nullable=False, index=True)
    maturity_date = Column(Date, nullable=True, index=True)
    closing_date = Column(Date, nullable=True)

    # Financial Details
    initial_amount = Column(Float, default=0.0, nullable=False)  # Opening balance or lump sum
    current_balance = Column(Float, default=0.0, nullable=False)  # Current balance
    interest_rate = Column(Float, nullable=True)  # Annual interest rate (%)

    # Term Details
    tenure_months = Column(Integer, nullable=True)  # Tenure in months
    compounding_frequency = Column(SQLEnum(CompoundingFrequency), nullable=True)

    # Recurring Deposit Details
    monthly_installment = Column(Float, nullable=True)  # For RD/SIP

    # Maturity Details
    expected_maturity_amount = Column(Float, nullable=True)
    actual_maturity_amount = Column(Float, nullable=True)
    total_interest_earned = Column(Float, default=0.0)

    # Status
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False, index=True)

    # Additional Info
    nominee_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    entries = relationship("SavingsEntry", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SavingsAccount(id={self.id}, name='{self.account_name}', type='{self.account_type}', balance={self.current_balance})>"


class SavingsEntry(Base):
    """
    Savings Entry Model

    Represents individual transactions for savings accounts:
    - Deposits, withdrawals
    - Interest credits
    - Fees, dividends
    - Maturity payments
    """
    __tablename__ = "savings_entries"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key
    account_id = Column(Integer, ForeignKey("savings_accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Entry Details
    entry_type = Column(SQLEnum(EntryType), nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)

    # Amount
    amount = Column(Float, nullable=False)  # Positive for credits, can be positive/negative

    # Balance after this entry
    balance_after = Column(Float, nullable=False)

    # Description
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("SavingsAccount", back_populates="entries")

    def __repr__(self):
        return f"<SavingsEntry(id={self.id}, account_id={self.account_id}, type='{self.entry_type}', amount={self.amount}, date={self.entry_date})>"


class SavingsGoal(Base):
    """
    Savings Goal Model

    Optional: Track savings goals and targets
    """
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Goal Details
    goal_name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)

    # Dates
    target_date = Column(Date, nullable=True)
    achieved_date = Column(Date, nullable=True)

    # Status
    is_achieved = Column(Boolean, default=False)

    # Linked accounts (optional - could be JSON array of account IDs)
    linked_accounts = Column(Text, nullable=True)  # JSON array: [1, 2, 3]

    # Notes
    description = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SavingsGoal(id={self.id}, name='{self.goal_name}', target={self.target_amount}, current={self.current_amount})>"
