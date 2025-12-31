"""
Models Registry
Import all models here to ensure they're registered with SQLAlchemy Base
This file should be imported during application startup
"""

# Existing models
from app.modules.accounts.models import Account
from app.modules.transactions.models import JournalEntry, TransactionLine
from app.modules.daybook.models import DayBookPage, DayBookEntry
from app.modules.audit.models import AuditLog

# New modules - Savings
from app.modules.savings.models import (
    SavingsAccount,
    SavingsEntry,
    SavingsGoal
)

# New modules - Precious Metals
from app.modules.precious_metals.models import (
    PreciousMetalsAccount,
    PreciousMetalsTransaction,
    PreciousMetalsRate
)

# New modules - Expenses
from app.modules.expenses.models import (
    Expense,
    ExpenseBudget,
    ExpenseCategory_Custom
)

# Export all for easy access
__all__ = [
    # Existing
    'Account',
    'JournalEntry',
    'TransactionLine',
    'DayBookPage',
    'DayBookEntry',
    'AuditLog',
    # Savings
    'SavingsAccount',
    'SavingsEntry',
    'SavingsGoal',
    # Precious Metals
    'PreciousMetalsAccount',
    'PreciousMetalsTransaction',
    'PreciousMetalsRate',
    # Expenses
    'Expense',
    'ExpenseBudget',
    'ExpenseCategory_Custom',
]
