"""
DayBook Service - Day-by-day accounting with balance carry-forward
"""

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from .models import DayBookPage, DayBookEntry
from app.core.events import event_bus, EventType, DomainEvent


class DayBookService:
    """Service for day-by-day daybook operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_page(self, book_date: date) -> DayBookPage:
        """
        Get the daybook page for a specific date.
        If it doesn't exist, create it with carry-forward balance.

        Logic:
        1. Check if page exists for this date
        2. If not, create new page
        3. Get previous day's closing balance
        4. Set as today's opening balance
        """
        # Try to get existing page
        result = await self.db.execute(
            select(DayBookPage)
            .options(selectinload(DayBookPage.entries))
            .where(DayBookPage.book_date == book_date)
        )
        page = result.scalar_one_or_none()

        if page:
            return page

        # Create new page
        # Get previous day's closing balance
        previous_balance = await self._get_previous_closing_balance(book_date)

        page = DayBookPage(
            book_date=book_date,
            opening_balance=previous_balance,
            closing_balance=previous_balance,  # Initial closing = opening
            total_debit=Decimal("0.00"),
            total_credit=Decimal("0.00"),
            entry_count=0,
        )

        self.db.add(page)
        await self.db.flush()
        await self.db.refresh(page)

        # Re-fetch the page to ensure all relationships (entries) are loaded
        # This prevents MissingGreenlet error when accessing page.entries in async context
        return await self.get_page(book_date)

    async def _get_previous_closing_balance(self, current_date: date) -> Decimal:
        """Get the closing balance from the previous day"""
        # Get the most recent page before current_date
        result = await self.db.execute(
            select(DayBookPage)
            .where(DayBookPage.book_date < current_date)
            .order_by(DayBookPage.book_date.desc())
            .limit(1)
        )
        previous_page = result.scalar_one_or_none()

        if previous_page:
            return Decimal(str(previous_page.closing_balance))

        # No previous page, starting balance is zero
        return Decimal("0.00")

    async def add_entry(
        self,
        book_date: date,
        description: str,
        debit_amount: Decimal = Decimal("0.00"),
        credit_amount: Decimal = Decimal("0.00"),
        reference: Optional[str] = None,
        category: Optional[str] = None,
        party_name: Optional[str] = None,
    ) -> DayBookEntry:
        """
        Add an entry to a specific day's page.

        This automatically:
        1. Gets or creates the page for that date
        2. Calculates the new balance
        3. Updates the page totals
        4. Carries forward to next days if they exist
        """
        # Validate
        if debit_amount < 0 or credit_amount < 0:
            raise ValueError("Amounts cannot be negative")
        if debit_amount > 0 and credit_amount > 0:
            raise ValueError("Entry cannot have both debit and credit")
        if debit_amount == 0 and credit_amount == 0:
            raise ValueError("Entry must have either debit or credit")

        # Get or create page
        page = await self.get_or_create_page(book_date)

        # Check if page is locked
        if page.is_locked:
            raise ValueError("Cannot add entry to a locked page")

        # Calculate new entry number
        next_entry_number = page.entry_count + 1

        # Calculate running balance
        amount = debit_amount - credit_amount
        new_balance = page.opening_balance_decimal + page.net_movement + amount

        # Generate entry number string
        entry_number_str = f"{book_date.strftime('%Y%m%d')}-{next_entry_number:04d}"

        # Create entry
        entry = DayBookEntry(
            page_id=page.id,
            entry_number=entry_number_str,
            entry_time=datetime.now(),
            particulars=description,
            receipt_no=reference,
            debit=debit_amount,
            credit=credit_amount,
            balance=new_balance,
            category=category,
            party_name=party_name,
        )

        self.db.add(entry)

        # Update page totals
        page.total_debit += debit_amount
        page.total_credit += credit_amount
        page.closing_balance = new_balance
        page.entry_count = next_entry_number
        page.updated_at = datetime.utcnow()

        await self.db.flush()

        # Carry forward to subsequent days
        await self._carry_forward_from_date(book_date)

        # Publish event
        await event_bus.publish(
            DomainEvent(
                event_type=EventType.TRANSACTION_CREATED,
                data={
                    "entry_id": entry.id,
                    "date": str(book_date),
                    "amount": str(amount),
                },
                timestamp=datetime.utcnow(),
            )
        )

        await self.db.refresh(entry)
        return entry

    async def _carry_forward_from_date(self, start_date: date):
        """
        Recalculate balances for all days after the given date.

        When you add/modify an entry on a past date, all future
        days need their opening balances updated.
        """
        # Get all pages after start_date
        result = await self.db.execute(
            select(DayBookPage)
            .where(DayBookPage.book_date > start_date)
            .options(selectinload(DayBookPage.entries))
            .order_by(DayBookPage.book_date)
        )
        future_pages = result.scalars().all()

        if not future_pages:
            return  # No future pages to update

        # Get the closing balance of start_date
        start_page_result = await self.db.execute(
            select(DayBookPage).where(DayBookPage.book_date == start_date)
        )
        start_page = start_page_result.scalar_one_or_none()

        if not start_page:
            return

        # Carry forward through each subsequent day
        previous_closing = start_page.closing_balance_decimal

        for page in future_pages:
            # Update opening balance
            page.opening_balance = previous_closing

            # Recalculate closing balance
            page.closing_balance = previous_closing + page.net_movement

            # Update entries' balances
            await self._recalculate_page_balances(page)

            previous_closing = page.closing_balance_decimal

        await self.db.flush()

    async def _recalculate_page_balances(self, page: DayBookPage):
        """Recalculate running balances for all entries on a page"""
        # Get all entries for this page in order
        result = await self.db.execute(
            select(DayBookEntry)
            .where(DayBookEntry.page_id == page.id)
            .order_by(DayBookEntry.entry_number)
        )
        entries = result.scalars().all()

        running_balance = page.opening_balance_decimal

        for entry in entries:
            amount = Decimal(str(entry.debit)) - Decimal(str(entry.credit))
            running_balance += amount
            entry.balance = running_balance

    async def get_page(self, book_date: date) -> Optional[DayBookPage]:
        """Get a specific day's page with all entries"""
        result = await self.db.execute(
            select(DayBookPage)
            .options(selectinload(DayBookPage.entries))
            .where(DayBookPage.book_date == book_date)
        )
        return result.scalar_one_or_none()

    async def get_page_range(
        self, start_date: date, end_date: date
    ) -> List[DayBookPage]:
        """Get multiple days' pages"""
        result = await self.db.execute(
            select(DayBookPage)
            .options(selectinload(DayBookPage.entries))
            .where(
                and_(
                    DayBookPage.book_date >= start_date,
                    DayBookPage.book_date <= end_date,
                )
            )
            .order_by(DayBookPage.book_date)
        )
        return list(result.scalars().all())

    async def get_today_page(self) -> DayBookPage:
        """Get today's page"""
        return await self.get_or_create_page(date.today())

    async def search_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        description: Optional[str] = None,
        entry_number: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DayBookEntry]:
        """Search entries by text, date range, or category"""
        filters = []

        if start_date:
            filters.append(DayBookPage.book_date >= start_date)
        if end_date:
            filters.append(DayBookPage.book_date <= end_date)

        query_stmt = (
            select(DayBookEntry)
            .join(DayBookPage)
            .options(selectinload(DayBookEntry.page))
            .where(and_(*filters) if filters else True)
        )

        if description:
            query_stmt = query_stmt.where(
                DayBookEntry.particulars.contains(description)
                | (
                    DayBookEntry.party_name.isnot(None)
                    & DayBookEntry.party_name.contains(description)
                )
                | (
                    DayBookEntry.receipt_no.isnot(None)
                    & DayBookEntry.receipt_no.contains(description)
                )
            )

        if entry_number:
            query_stmt = query_stmt.where(
                DayBookEntry.entry_number.contains(entry_number)
            )

        if category:
            query_stmt = query_stmt.where(DayBookEntry.category == category)

        result = await self.db.execute(
            query_stmt.order_by(DayBookEntry.entry_time.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_entry(self, entry_id: str, data) -> DayBookEntry:
        """Update a daybook entry (only if page is not locked)"""
        # Get entry
        result = await self.db.execute(
            select(DayBookEntry).where(DayBookEntry.id == entry_id)
        )
        entry = result.scalar_one_or_none()

        if not entry:
            raise ValueError("Entry not found")

        # Get page
        page_result = await self.db.execute(
            select(DayBookPage).where(DayBookPage.id == entry.page_id)
        )
        page = page_result.scalar_one_or_none()

        if not page:
            raise ValueError("Page not found")

        if page.is_locked:
            raise ValueError("Cannot update entry on a locked page")

        # Store old amounts for recalculation
        old_debit = Decimal(str(entry.debit))
        old_credit = Decimal(str(entry.credit))

        # Update fields
        if data.description is not None:
            entry.particulars = data.description
        if data.debit_amount is not None:
            entry.debit = data.debit_amount
        if data.credit_amount is not None:
            entry.credit = data.credit_amount
        if data.reference is not None:
            entry.receipt_no = data.reference

        # Recalculate page totals
        page.total_debit = page.total_debit - old_debit + Decimal(str(entry.debit))
        page.total_credit = page.total_credit - old_credit + Decimal(str(entry.credit))
        page.updated_at = datetime.utcnow()

        # Recalculate closing balance
        page.closing_balance = page.opening_balance + page.net_movement

        # Recalculate all entries on this page
        await self._recalculate_page_balances(page)

        # Carry forward to subsequent days
        await self._carry_forward_from_date(page.book_date)

        await self.db.flush()
        await self.db.refresh(entry)

        return entry

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a daybook entry (only if page is not locked)"""
        # Get entry
        result = await self.db.execute(
            select(DayBookEntry).where(DayBookEntry.id == entry_id)
        )
        entry = result.scalar_one_or_none()

        if not entry:
            return False

        # Get page
        page_result = await self.db.execute(
            select(DayBookPage).where(DayBookPage.id == entry.page_id)
        )
        page = page_result.scalar_one_or_none()

        if not page:
            return False

        if page.is_locked:
            raise ValueError("Cannot delete entry from a locked page")

        # Update page totals
        page.total_debit -= Decimal(str(entry.debit))
        page.total_credit -= Decimal(str(entry.credit))
        page.entry_count -= 1
        page.updated_at = datetime.utcnow()

        # Delete entry
        await self.db.delete(entry)

        # Recalculate closing balance
        page.closing_balance = page.opening_balance + page.net_movement

        # Recalculate remaining entries on this page
        await self._recalculate_page_balances(page)

        # Carry forward to subsequent days
        await self._carry_forward_from_date(page.book_date)

        await self.db.flush()

        return True

    async def lock_page(self, book_date: date) -> DayBookPage:
        """Lock a page to prevent further edits"""
        page = await self.get_or_create_page(book_date)
        page.is_locked = True
        page.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(page)

        return page

    async def get_pages(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
        offset: int = 0,
    ) -> List[DayBookPage]:
        """Get list of daybook pages"""
        filters = []

        if start_date:
            filters.append(DayBookPage.book_date >= start_date)
        if end_date:
            filters.append(DayBookPage.book_date <= end_date)

        query_stmt = select(DayBookPage)

        if filters:
            query_stmt = query_stmt.where(and_(*filters))

        query_stmt = (
            query_stmt.options(selectinload(DayBookPage.entries))
            .order_by(DayBookPage.book_date.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query_stmt)
        return list(result.scalars().all())

    async def generate_report(self, start_date: date, end_date: date) -> dict:
        """
        Generate a report for a specific date range.
        Returns summary statistics and all entries.
        """
        # Get all pages in the range, ordered chronologically
        pages = await self.get_page_range(start_date, end_date)

        # Initialize summary
        summary = {
            "opening_balance": Decimal("0.00"),
            "closing_balance": Decimal("0.00"),
            "total_debit": Decimal("0.00"),
            "total_credit": Decimal("0.00"),
            "net_change": Decimal("0.00"),
            "entry_count": 0,
        }

        all_entries = []

        if pages:
            # We have activity in this range
            first_page = pages[0]
            last_page = pages[-1]

            summary["opening_balance"] = first_page.opening_balance_decimal
            summary["closing_balance"] = last_page.closing_balance_decimal

            for page in pages:
                summary["total_debit"] += Decimal(str(page.total_debit))
                summary["total_credit"] += Decimal(str(page.total_credit))
                summary["entry_count"] += page.entry_count

                # Collect entries
                # Ensure entries are sorted by time/number
                sorted_entries = sorted(page.entries, key=lambda x: x.entry_number)
                # Store tuple of (book_date, entry)
                for entry in sorted_entries:
                    all_entries.append((page.book_date, entry))

        else:
            # No activity in this range, find opening balance from previous days
            previous_balance = await self._get_previous_closing_balance(start_date)
            summary["opening_balance"] = previous_balance
            summary["closing_balance"] = previous_balance

        summary["net_change"] = summary["total_debit"] - summary["total_credit"]

        return {
            "period_start": start_date,
            "period_end": end_date,
            "summary": summary,
            "entries": all_entries,
        }
