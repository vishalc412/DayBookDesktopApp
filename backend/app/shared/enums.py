"""
Shared Enumerations
"""

from enum import Enum


class TransactionStatus(str, Enum):
    """Transaction lifecycle states"""
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"


class TransactionSource(str, Enum):
    """Source of transaction entry"""
    APP = "APP"
    EXCEL_IMPORT = "EXCEL_IMPORT"
    RECOVERY = "RECOVERY"


class AccountType(str, Enum):
    """Chart of accounts types"""
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class ExcelSyncStatus(str, Enum):
    """Excel synchronization status"""
    PENDING = "PENDING"
    SYNCED = "SYNCED"
    FAILED = "FAILED"
