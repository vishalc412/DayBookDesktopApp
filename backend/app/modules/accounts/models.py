"""
Account Database Models
SQLAlchemy ORM models for chart of accounts
"""

from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Boolean, Integer
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base
from app.shared.enums import AccountType


class Account(Base):
    """
    Chart of Accounts
    Represents ledger accounts (Assets, Liabilities, Revenue, Expenses, Equity)
    """
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    parent_id = Column(String(36), nullable=True)  # For account hierarchy
    balance = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # transaction_lines defined in transactions module

    def __repr__(self):
        return f"<Account {self.code} - {self.name}>"

    @property
    def balance_decimal(self) -> Decimal:
        """Get balance as Decimal"""
        return Decimal(str(self.balance))

    def update_balance(self, amount: Decimal):
        """Update account balance (accounting rules apply)"""
        current = self.balance_decimal
        self.balance = current + amount
        self.updated_at = datetime.utcnow()
