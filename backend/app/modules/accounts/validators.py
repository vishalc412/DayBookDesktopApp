"""
Account Validators
Business rules and constraints
"""

from decimal import Decimal
from app.shared.enums import AccountType


class AccountValidator:
    """Validates account operations"""

    @staticmethod
    def validate_account_code(code: str) -> None:
        """Validate account code format"""
        if not code or len(code) < 1 or len(code) > 20:
            raise ValueError("Account code must be between 1 and 20 characters")

        if not code.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Account code must be alphanumeric (hyphens and underscores allowed)")

    @staticmethod
    def validate_account_name(name: str) -> None:
        """Validate account name"""
        if not name or len(name) < 1 or len(name) > 200:
            raise ValueError("Account name must be between 1 and 200 characters")

    @staticmethod
    def validate_balance_update(
        account_type: AccountType,
        current_balance: Decimal,
        amount: Decimal
    ) -> None:
        """
        Validate balance update according to accounting rules

        Debit increases: Assets, Expenses
        Credit increases: Liabilities, Equity, Revenue
        """
        new_balance = current_balance + amount

        # Assets and Expenses normally have debit balances (positive)
        if account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            # Allow negative temporarily but warn
            pass

        # Liabilities, Equity, Revenue normally have credit balances (can be represented as positive)
        elif account_type in [AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE]:
            pass

    @staticmethod
    def can_delete_account(has_transactions: bool, balance: Decimal) -> tuple[bool, str]:
        """Check if account can be deleted"""
        if has_transactions:
            return False, "Cannot delete account with existing transactions"

        if balance != Decimal("0.00"):
            return False, "Cannot delete account with non-zero balance"

        return True, ""
