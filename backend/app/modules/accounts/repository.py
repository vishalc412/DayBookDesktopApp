"""
Account Repository
Database access layer - NO business logic
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from .models import Account
from app.shared.enums import AccountType


class AccountRepository:
    """Repository for Account database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, account: Account) -> Account:
        """Create a new account"""
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def get_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Account]:
        """Get account by code"""
        result = await self.db.execute(
            select(Account).where(Account.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        account_type: Optional[AccountType] = None,
        is_active: bool = True
    ) -> List[Account]:
        """Get all accounts with optional filters"""
        query = select(Account)

        if account_type:
            query = query.where(Account.account_type == account_type)
        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        query = query.order_by(Account.code)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, account: Account) -> Account:
        """Update an account"""
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def delete(self, account_id: str) -> bool:
        """Soft delete an account"""
        account = await self.get_by_id(account_id)
        if account:
            account.is_active = False
            await self.db.flush()
            return True
        return False

    async def exists_by_code(self, code: str, exclude_id: Optional[str] = None) -> bool:
        """Check if account code already exists"""
        query = select(Account.id).where(Account.code == code.upper())
        if exclude_id:
            query = query.where(Account.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
