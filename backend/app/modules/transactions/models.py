"""
Transaction Database Models
Implements double-entry accounting with Journal Entries and Transaction Lines
"""

from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base
from app.shared.enums import TransactionStatus, TransactionSource, ExcelSyncStatus


class JournalEntry(Base):
    """
    Journal Entry (Transaction Header)
    Represents a complete accounting transaction
    """
    __tablename__ = "journal_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True)

    # Transaction state
    status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.DRAFT,
        nullable=False,
        index=True
    )
    source = Column(
        Enum(TransactionSource),
        default=TransactionSource.APP,
        nullable=False
    )

    # Excel sync
    excel_sync_status = Column(
        Enum(ExcelSyncStatus),
        default=ExcelSyncStatus.PENDING,
        nullable=False
    )

    # Reversal tracking
    reversed_by_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=True)
    reverses_entry_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    created_by = Column(String(50), default="system")

    # Relationships
    lines = relationship(
        "TransactionLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        lazy="selectinload"
    )

    def __repr__(self):
        return f"<JournalEntry {self.entry_number} - {self.status}>"

    @property
    def total_debit(self) -> Decimal:
        """Calculate total debit amount"""
        return sum((line.debit for line in self.lines), Decimal("0.00"))

    @property
    def total_credit(self) -> Decimal:
        """Calculate total credit amount"""
        return sum((line.credit for line in self.lines), Decimal("0.00"))

    @property
    def is_balanced(self) -> bool:
        """Check if debits equal credits"""
        return self.total_debit == self.total_credit

    @property
    def is_mutable(self) -> bool:
        """Check if entry can be modified"""
        return self.status == TransactionStatus.DRAFT


class TransactionLine(Base):
    """
    Transaction Line (Journal Entry Line)
    Individual debit/credit line in a journal entry
    """
    __tablename__ = "transaction_lines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_entry_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=False, index=True)
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False, index=True)

    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    # Amounts (Decimal for money)
    debit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    credit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", foreign_keys=[account_id])

    def __repr__(self):
        return f"<TransactionLine {self.line_number} - Dr:{self.debit} Cr:{self.credit}>"

    @property
    def debit_decimal(self) -> Decimal:
        """Get debit as Decimal"""
        return Decimal(str(self.debit))

    @property
    def credit_decimal(self) -> Decimal:
        """Get credit as Decimal"""
        return Decimal(str(self.credit))

    @property
    def amount(self) -> Decimal:
        """Get net amount (debit - credit)"""
        return self.debit_decimal - self.credit_decimal
