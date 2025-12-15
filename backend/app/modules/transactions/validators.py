"""
Transaction Validators
Enforces double-entry accounting rules
"""

from decimal import Decimal
from datetime import datetime
from typing import List

from .models import JournalEntry, TransactionLine
from app.shared.enums import TransactionStatus


class TransactionValidator:
    """Validates transaction operations according to accounting principles"""

    @staticmethod
    def validate_minimum_lines(lines: List[TransactionLine]) -> None:
        """Validate minimum number of lines (double-entry requires at least 2)"""
        if len(lines) < 2:
            raise ValueError(
                "A transaction must have at least 2 lines for double-entry accounting"
            )

    @staticmethod
    def validate_balanced(entry: JournalEntry) -> None:
        """Validate that debits equal credits"""
        total_debit = entry.total_debit
        total_credit = entry.total_credit

        if total_debit != total_credit:
            raise ValueError(
                f"Transaction is not balanced: "
                f"Debits={total_debit}, Credits={total_credit}. "
                f"Difference={total_debit - total_credit}"
            )

    @staticmethod
    def validate_date(entry_date: datetime) -> None:
        """Validate transaction date"""
        if entry_date > datetime.utcnow():
            raise ValueError("Transaction date cannot be in the future")

        # Optional: Add fiscal period validation
        # if entry_date < fiscal_period_start:
        #     raise ValueError("Transaction date is before current fiscal period")

    @staticmethod
    async def validate_accounts_exist(account_ids: List[str], account_service) -> None:
        """Validate that all accounts exist"""
        for account_id in account_ids:
            account = await account_service.get_account(account_id)
            if not account:
                raise ValueError(f"Account {account_id} does not exist")
            if not account.is_active:
                raise ValueError(f"Account {account_id} is not active")

    @staticmethod
    def validate_can_modify(entry: JournalEntry) -> None:
        """Validate that entry can be modified"""
        if entry.status != TransactionStatus.DRAFT:
            raise ValueError(
                f"Cannot modify transaction in status {entry.status}. "
                f"Only DRAFT transactions can be modified."
            )

    @staticmethod
    def validate_can_post(entry: JournalEntry) -> None:
        """Validate that entry can be posted"""
        if entry.status != TransactionStatus.DRAFT:
            raise ValueError(
                f"Cannot post transaction in status {entry.status}. "
                f"Only DRAFT transactions can be posted."
            )

        if not entry.is_balanced:
            raise ValueError("Cannot post unbalanced transaction")

        if not entry.lines or len(entry.lines) < 2:
            raise ValueError("Cannot post transaction with less than 2 lines")

    @staticmethod
    def validate_can_reverse(entry: JournalEntry) -> None:
        """Validate that entry can be reversed"""
        if entry.status != TransactionStatus.POSTED:
            raise ValueError(
                f"Cannot reverse transaction in status {entry.status}. "
                f"Only POSTED transactions can be reversed."
            )

        if entry.reversed_by_id:
            raise ValueError("Transaction has already been reversed")

    @staticmethod
    def validate_line_amounts(debit: Decimal, credit: Decimal) -> None:
        """Validate transaction line amounts"""
        if debit < 0 or credit < 0:
            raise ValueError("Debit and credit amounts must be non-negative")

        if debit > 0 and credit > 0:
            raise ValueError("A line cannot have both debit and credit")

        if debit == 0 and credit == 0:
            raise ValueError("A line must have either debit or credit")
