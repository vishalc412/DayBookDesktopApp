"""
Transaction Repository
Database access layer for journal entries and lines
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from .models import JournalEntry, TransactionLine
from app.shared.enums import TransactionStatus


class TransactionRepository:
    """Repository for transaction database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, entry: JournalEntry) -> JournalEntry:
        """Create a new journal entry"""
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry, ['lines'])
        return entry

    async def get_by_id(self, entry_id: str) -> Optional[JournalEntry]:
        """Get journal entry by ID with lines"""
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(JournalEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_by_entry_number(self, entry_number: str) -> Optional[JournalEntry]:
        """Get journal entry by entry number"""
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(JournalEntry.entry_number == entry_number)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[TransactionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntry]:
        """Get all journal entries with filters"""
        query = select(JournalEntry).options(selectinload(JournalEntry.lines))

        if status:
            query = query.where(JournalEntry.status == status)

        if start_date:
            query = query.where(JournalEntry.date >= start_date)

        if end_date:
            query = query.where(JournalEntry.date <= end_date)

        query = query.order_by(JournalEntry.date.desc(), JournalEntry.entry_number.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, entry: JournalEntry) -> JournalEntry:
        """Update a journal entry"""
        await self.db.flush()
        await self.db.refresh(entry, ['lines'])
        return entry

    async def delete(self, entry_id: str) -> bool:
        """Delete a journal entry (only DRAFT entries)"""
        entry = await self.get_by_id(entry_id)
        if entry and entry.status == TransactionStatus.DRAFT:
            await self.db.delete(entry)
            await self.db.flush()
            return True
        return False

    async def get_next_entry_number(self, prefix: str = "JE") -> str:
        """Generate next entry number"""
        result = await self.db.execute(
            select(func.count(JournalEntry.id))
        )
        count = result.scalar() or 0
        return f"{prefix}{count + 1:06d}"

    async def mark_posted(self, entry: JournalEntry) -> JournalEntry:
        """Mark entry as posted"""
        entry.status = TransactionStatus.POSTED
        entry.posted_at = datetime.utcnow()
        entry.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def mark_reversed(
        self,
        entry: JournalEntry,
        reversal_entry_id: str
    ) -> JournalEntry:
        """Mark entry as reversed"""
        entry.status = TransactionStatus.REVERSED
        entry.reversed_by_id = reversal_entry_id
        entry.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(entry)
        return entry
