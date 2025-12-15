"""
Transaction Service
Core business logic for double-entry accounting
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from .models import JournalEntry, TransactionLine
from .schemas import JournalEntryCreate, JournalEntryUpdate
from .repository import TransactionRepository
from .validators import TransactionValidator
from app.modules.accounts.service import AccountService
from app.shared.enums import TransactionStatus, TransactionSource, ExcelSyncStatus
from app.core.events import event_bus, EventType, DomainEvent


class TransactionService:
    """Service for transaction business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TransactionRepository(db)
        self.validator = TransactionValidator()
        self.account_service = AccountService(db)

    async def create_transaction(
        self,
        data: JournalEntryCreate,
        source: TransactionSource = TransactionSource.APP
    ) -> JournalEntry:
        """
        Create a new transaction in DRAFT status
        """
        # Validate date
        self.validator.validate_date(data.date)

        # Validate accounts exist
        account_ids = [line.account_id for line in data.lines]
        await self.validator.validate_accounts_exist(account_ids, self.account_service)

        # Generate entry number
        entry_number = await self.repository.get_next_entry_number()

        # Create journal entry
        entry = JournalEntry(
            entry_number=entry_number,
            date=data.date,
            description=data.description,
            reference=data.reference,
            status=TransactionStatus.DRAFT,
            source=source,
            excel_sync_status=ExcelSyncStatus.PENDING
        )

        # Create lines
        for idx, line_data in enumerate(data.lines, start=1):
            self.validator.validate_line_amounts(line_data.debit, line_data.credit)

            line = TransactionLine(
                account_id=line_data.account_id,
                line_number=idx,
                description=line_data.description,
                debit=line_data.debit,
                credit=line_data.credit
            )
            entry.lines.append(line)

        # Final validation
        self.validator.validate_minimum_lines(entry.lines)
        self.validator.validate_balanced(entry)

        # Save
        entry = await self.repository.create(entry)

        # Publish event
        await event_bus.publish(DomainEvent(
            event_type=EventType.TRANSACTION_CREATED,
            data={"entry_id": entry.id, "entry_number": entry.entry_number},
            timestamp=datetime.utcnow()
        ))

        return entry

    async def update_draft_transaction(
        self,
        entry_id: str,
        data: JournalEntryUpdate
    ) -> JournalEntry:
        """
        Update a DRAFT transaction
        POSTED transactions are IMMUTABLE
        """
        entry = await self.repository.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Transaction {entry_id} not found")

        # Validate can modify
        self.validator.validate_can_modify(entry)

        # Update fields
        if data.date:
            self.validator.validate_date(data.date)
            entry.date = data.date

        if data.description:
            entry.description = data.description

        if data.reference is not None:
            entry.reference = data.reference

        if data.lines:
            # Validate accounts exist
            account_ids = [line.account_id for line in data.lines]
            await self.validator.validate_accounts_exist(account_ids, self.account_service)

            # Replace lines
            entry.lines.clear()
            for idx, line_data in enumerate(data.lines, start=1):
                self.validator.validate_line_amounts(line_data.debit, line_data.credit)

                line = TransactionLine(
                    account_id=line_data.account_id,
                    line_number=idx,
                    description=line_data.description,
                    debit=line_data.debit,
                    credit=line_data.credit
                )
                entry.lines.append(line)

            # Validate new lines
            self.validator.validate_minimum_lines(entry.lines)
            self.validator.validate_balanced(entry)

        return await self.repository.update(entry)

    async def post_transaction(self, entry_id: str) -> JournalEntry:
        """
        Post a transaction
        This makes it IMMUTABLE and updates account balances
        """
        entry = await self.repository.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Transaction {entry_id} not found")

        # Validate can post
        self.validator.validate_can_post(entry)

        # Apply to account balances
        for line in entry.lines:
            # Calculate amount to apply to account
            # Debit increases assets/expenses, decreases liabilities/equity/revenue
            # Credit increases liabilities/equity/revenue, decreases assets/expenses
            amount = line.debit_decimal - line.credit_decimal

            await self.account_service.apply_transaction_line(
                account_id=line.account_id,
                amount=amount,
                reason=f"Transaction {entry.entry_number}"
            )

        # Mark as posted
        entry = await self.repository.mark_posted(entry)

        # Publish event (triggers Excel sync)
        await event_bus.publish(DomainEvent(
            event_type=EventType.TRANSACTION_POSTED,
            data={
                "entry_id": entry.id,
                "entry_number": entry.entry_number,
                "total_debit": str(entry.total_debit),
                "total_credit": str(entry.total_credit)
            },
            timestamp=datetime.utcnow()
        ))

        return entry

    async def reverse_transaction(
        self,
        entry_id: str,
        reason: str,
        reversal_date: Optional[datetime] = None
    ) -> JournalEntry:
        """
        Reverse a POSTED transaction
        Creates a new transaction with opposite entries
        """
        original_entry = await self.repository.get_by_id(entry_id)
        if not original_entry:
            raise ValueError(f"Transaction {entry_id} not found")

        # Validate can reverse
        self.validator.validate_can_reverse(original_entry)

        # Create reversal entry
        reversal_date = reversal_date or datetime.utcnow()

        reversal_number = await self.repository.get_next_entry_number("REV")

        reversal_entry = JournalEntry(
            entry_number=reversal_number,
            date=reversal_date,
            description=f"REVERSAL: {reason} (Original: {original_entry.entry_number})",
            reference=original_entry.reference,
            status=TransactionStatus.DRAFT,
            source=TransactionSource.APP,
            reverses_entry_id=original_entry.id
        )

        # Create opposite lines
        for line in original_entry.lines:
            reversal_line = TransactionLine(
                account_id=line.account_id,
                line_number=line.line_number,
                description=f"Reversal of {line.description or ''}",
                debit=line.credit,  # Swap debit and credit
                credit=line.debit
            )
            reversal_entry.lines.append(reversal_line)

        # Save reversal entry
        reversal_entry = await self.repository.create(reversal_entry)

        # Post reversal entry immediately
        reversal_entry = await self.post_transaction(reversal_entry.id)

        # Mark original as reversed
        await self.repository.mark_reversed(original_entry, reversal_entry.id)

        # Publish event
        await event_bus.publish(DomainEvent(
            event_type=EventType.TRANSACTION_REVERSED,
            data={
                "original_entry_id": original_entry.id,
                "reversal_entry_id": reversal_entry.id,
                "reason": reason
            },
            timestamp=datetime.utcnow()
        ))

        return reversal_entry

    async def get_transaction(self, entry_id: str) -> Optional[JournalEntry]:
        """Get transaction by ID"""
        return await self.repository.get_by_id(entry_id)

    async def get_all_transactions(
        self,
        status: Optional[TransactionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntry]:
        """Get all transactions with filters"""
        return await self.repository.get_all(status, start_date, end_date, limit, offset)

    async def delete_draft_transaction(self, entry_id: str) -> bool:
        """Delete a DRAFT transaction (only drafts can be deleted)"""
        entry = await self.repository.get_by_id(entry_id)
        if not entry:
            return False

        self.validator.validate_can_modify(entry)
        return await self.repository.delete(entry_id)
