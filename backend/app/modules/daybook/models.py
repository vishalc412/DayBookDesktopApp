"""
DayBook Models - Daily accounting pages with balance carry-forward
"""

from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Column, String, Numeric, Date, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class DayBookPage(Base):
    """
    A single day's accounting page.

    Key Concept:
    - Each day has its own "page" in the daybook
    - Opening balance carries forward from previous day's closing
    - Closing balance becomes next day's opening balance

    Example Timeline:

    Dec 14:
        Opening: $0
        Transactions: +$1,000
        Closing: $1,000

    Dec 15:
        Opening: $1,000 (← from Dec 14)
        Transactions: -$200
        Closing: $800

    Dec 16:
        Opening: $800 (← from Dec 15)
        Transactions: +$500
        Closing: $1,300
    """
    __tablename__ = "daybook_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_date = Column(Date, nullable=False, unique=True, index=True)
    """The date this page represents"""

    opening_balance = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Balance at start of day (from previous day's closing)"""

    closing_balance = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Balance at end of day (becomes next day's opening)"""

    total_debit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Sum of all debits for this day"""

    total_credit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Sum of all credits for this day"""

    entry_count = Column(Integer, default=0, nullable=False)
    """Number of entries on this page"""

    is_closed = Column(Boolean, default=False, nullable=False)
    """Is this day closed for editing? (for period close)"""

    notes = Column(Text, nullable=True)
    """Optional day notes"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entries = relationship(
        "DayBookEntry",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="DayBookEntry.entry_time"
    )

    # Index for fast date lookups
    __table_args__ = (
        Index('idx_daybook_date', 'book_date'),
    )

    @property
    def opening_balance_decimal(self) -> Decimal:
        return Decimal(str(self.opening_balance))

    @property
    def closing_balance_decimal(self) -> Decimal:
        return Decimal(str(self.closing_balance))

    @property
    def net_movement(self) -> Decimal:
        """Net change for the day"""
        return Decimal(str(self.total_debit)) - Decimal(str(self.total_credit))

    def __repr__(self):
        return f"<DayBookPage {self.book_date} - Balance: {self.closing_balance}>"


class DayBookEntry(Base):
    """
    Individual entry in the daybook.

    This is simpler than JournalEntry - focused on daily bookkeeping.
    For full double-entry, use the Transactions module.
    """
    __tablename__ = "daybook_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = Column(String(36), ForeignKey('daybook_pages.id'), nullable=False, index=True)

    entry_number = Column(Integer, nullable=False)
    """Entry number within the day (1, 2, 3...)"""

    entry_time = Column(DateTime, nullable=False, index=True)
    """Exact time of entry"""

    particulars = Column(Text, nullable=False)
    """Description of the transaction"""

    receipt_no = Column(String(50), nullable=True)
    """Receipt/voucher number if any"""

    debit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Debit amount (money received)"""

    credit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """Credit amount (money paid)"""

    balance = Column(Numeric(15, 2), nullable=False)
    """Running balance after this entry"""

    category = Column(String(50), nullable=True)
    """Optional category (Sales, Purchase, Expense, etc.)"""

    party_name = Column(String(200), nullable=True)
    """Customer/Supplier name if applicable"""

    linked_transaction_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=True)
    """Optional link to full double-entry transaction"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), default="system")

    # Relationships
    page = relationship("DayBookPage", back_populates="entries")

    # Indexes
    __table_args__ = (
        Index('idx_daybook_entry_date', 'page_id', 'entry_number'),
    )

    @property
    def amount(self) -> Decimal:
        """Net amount (debit - credit)"""
        return Decimal(str(self.debit)) - Decimal(str(self.credit))

    def __repr__(self):
        return f"<DayBookEntry {self.entry_number} - {self.particulars[:30]}>"
