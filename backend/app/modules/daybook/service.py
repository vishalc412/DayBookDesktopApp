"""
DayBook Service - Day-by-day accounting with balance carry-forward
"""

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

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
            select(DayBookPage).where(DayBookPage.book_date == book_date)
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
            entry_count=0
        )

        self.db.add(page)
        await self.db.flush()
        await self.db.refresh(page)

        return page

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
        particulars: str,
        debit: Decimal = Decimal("0.00"),
        credit: Decimal = Decimal("0.00"),
        receipt_no: Optional[str] = None,
        category: Optional[str] = None,
        party_name: Optional[str] = None
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
        if debit < 0 or credit < 0:
            raise ValueError("Amounts cannot be negative")
        if debit > 0 and credit > 0:
            raise ValueError("Entry cannot have both debit and credit")
        if debit == 0 and credit == 0:
            raise ValueError("Entry must have either debit or credit")

        # Get or create page
        page = await self.get_or_create_page(book_date)

        # Calculate new entry number
        next_entry_number = page.entry_count + 1

        # Calculate running balance
        amount = debit - credit
        new_balance = page.opening_balance_decimal + page.net_movement + amount

        # Create entry
        entry = DayBookEntry(
            page_id=page.id,
            entry_number=next_entry_number,
            entry_time=datetime.now(),
            particulars=particulars,
            receipt_no=receipt_no,
            debit=debit,
            credit=credit,
            balance=new_balance,
            category=category,
            party_name=party_name
        )

        self.db.add(entry)

        # Update page totals
        page.total_debit += debit
        page.total_credit += credit
        page.closing_balance = new_balance
        page.entry_count = next_entry_number
        page.updated_at = datetime.utcnow()

        await self.db.flush()

        # Carry forward to subsequent days
        await self._carry_forward_from_date(book_date)

        # Publish event
        await event_bus.publish(DomainEvent(
            event_type=EventType.TRANSACTION_CREATED,
            data={
                "entry_id": entry.id,
                "date": str(book_date),
                "amount": str(amount)
            },
            timestamp=datetime.utcnow()
        ))

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
            .where(DayBookPage.book_date == book_date)
        )
        return result.scalar_one_or_none()

    async def get_page_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[DayBookPage]:
        """Get multiple days' pages"""
        result = await self.db.execute(
            select(DayBookPage)
            .where(and_(
                DayBookPage.book_date >= start_date,
                DayBookPage.book_date <= end_date
            ))
            .order_by(DayBookPage.book_date)
        )
        return list(result.scalars().all())

    async def get_today_page(self) -> DayBookPage:
        """Get today's page"""
        return await self.get_or_create_page(date.today())

    async def search_entries(
        self,
        query: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
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
            .where(and_(*filters) if filters else True)
        )

        if query:
            query_stmt = query_stmt.where(
                DayBookEntry.particulars.contains(query) |
                DayBookEntry.party_name.contains(query) |
                DayBookEntry.receipt_no.contains(query)
            )

        if category:
            query_stmt = query_stmt.where(DayBookEntry.category == category)

        result = await self.db.execute(query_stmt.order_by(DayBookEntry.entry_time.desc()))
        return list(result.scalars().all())
