"""
Account Service
Business logic layer
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Account
from .schemas import AccountCreate, AccountUpdate
from .repository import AccountRepository
from .validators import AccountValidator
from app.shared.enums import AccountType
from app.core.events import event_bus, EventType, DomainEvent


class AccountService:
    """Service for account business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AccountRepository(db)
        self.validator = AccountValidator()

    async def create_account(self, data: AccountCreate) -> Account:
        """Create a new account"""
        # Validate
        self.validator.validate_account_code(data.code)
        self.validator.validate_account_name(data.name)

        # Check if code already exists
        if await self.repository.exists_by_code(data.code):
            raise ValueError(f"Account code '{data.code}' already exists")

        # Create account
        account = Account(
            code=data.code.upper(),
            name=data.name,
            account_type=data.account_type,
            parent_id=data.parent_id,
            balance=Decimal("0.00"),
            is_active=True
        )

        account = await self.repository.create(account)

        # Publish event
        await event_bus.publish(DomainEvent(
            event_type=EventType.ACCOUNT_CREATED,
            data={"account_id": account.id, "code": account.code},
            timestamp=datetime.utcnow()
        ))

        return account

    async def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return await self.repository.get_by_id(account_id)

    async def get_account_by_code(self, code: str) -> Optional[Account]:
        """Get account by code"""
        return await self.repository.get_by_code(code)

    async def get_all_accounts(
        self,
        account_type: Optional[AccountType] = None,
        is_active: bool = True
    ) -> List[Account]:
        """Get all accounts with filters"""
        return await self.repository.get_all(account_type, is_active)

    async def update_account(self, account_id: str, data: AccountUpdate) -> Account:
        """Update account details"""
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if data.name:
            self.validator.validate_account_name(data.name)
            account.name = data.name

        if data.is_active is not None:
            account.is_active = data.is_active

        return await self.repository.update(account)

    async def apply_transaction_line(
        self,
        account_id: str,
        amount: Decimal,
        reason: str = "Transaction"
    ) -> Account:
        """
        Apply a transaction line to an account
        Called ONLY when transaction is POSTED
        """
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Validate balance update
        self.validator.validate_balance_update(
            account.account_type,
            account.balance_decimal,
            amount
        )

        # Update balance
        account.update_balance(amount)
        await self.repository.update(account)

        # Publish event
        await event_bus.publish(DomainEvent(
            event_type=EventType.ACCOUNT_BALANCE_UPDATED,
            data={
                "account_id": account.id,
                "amount": str(amount),
                "new_balance": str(account.balance),
                "reason": reason
            },
            timestamp=datetime.utcnow()
        ))

        return account

    async def calculate_balance_as_of(
        self,
        account_id: str,
        as_of_date: datetime
    ) -> Decimal:
        """
        Calculate account balance as of a specific date
        This would query transaction_lines table (not implemented in basic version)
        """
        # TODO: Implement historical balance calculation
        account = await self.repository.get_by_id(account_id)
        return account.balance_decimal if account else Decimal("0.00")

    async def initialize_default_accounts(self):
        """Initialize default chart of accounts"""
        default_accounts = [
            # Assets
            AccountCreate(code="1000", name="Cash", account_type=AccountType.ASSET),
            AccountCreate(code="1100", name="Bank Account", account_type=AccountType.ASSET),
            AccountCreate(code="1200", name="Accounts Receivable", account_type=AccountType.ASSET),

            # Liabilities
            AccountCreate(code="2000", name="Accounts Payable", account_type=AccountType.LIABILITY),
            AccountCreate(code="2100", name="Loans Payable", account_type=AccountType.LIABILITY),

            # Equity
            AccountCreate(code="3000", name="Owner's Equity", account_type=AccountType.EQUITY),
            AccountCreate(code="3100", name="Retained Earnings", account_type=AccountType.EQUITY),

            # Revenue
            AccountCreate(code="4000", name="Sales Revenue", account_type=AccountType.REVENUE),
            AccountCreate(code="4100", name="Service Revenue", account_type=AccountType.REVENUE),

            # Expenses
            AccountCreate(code="5000", name="Cost of Goods Sold", account_type=AccountType.EXPENSE),
            AccountCreate(code="5100", name="Rent Expense", account_type=AccountType.EXPENSE),
            AccountCreate(code="5200", name="Utilities Expense", account_type=AccountType.EXPENSE),
            AccountCreate(code="5300", name="Salaries Expense", account_type=AccountType.EXPENSE),
        ]

        created = []
        for acc_data in default_accounts:
            try:
                if not await self.repository.exists_by_code(acc_data.code):
                    account = await self.create_account(acc_data)
                    created.append(account)
            except Exception as e:
                print(f"Error creating account {acc_data.code}: {e}")

        return created
