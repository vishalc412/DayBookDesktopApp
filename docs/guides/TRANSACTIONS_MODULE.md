# 📊 Transactions Module - Complete Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Double-Entry Accounting](#double-entry-accounting)
3. [Models Deep Dive](#models-deep-dive)
4. [Schemas & Validation](#schemas--validation)
5. [Repository Layer](#repository-layer)
6. [Service Layer](#service-layer)
7. [Validators](#validators)
8. [Transaction Lifecycle](#transaction-lifecycle)
9. [Code Examples](#code-examples)
10. [Testing](#testing)

---

## Overview

The **Transactions Module** is the **heart of the accounting system**. It implements proper double-entry bookkeeping with:

- ✅ **Immutability** after posting
- ✅ **Balance validation** (debits = credits)
- ✅ **State management** (DRAFT → POSTED → REVERSED)
- ✅ **Reversal instead of deletion**
- ✅ **Decimal-based money** (no floats)
- ✅ **Event-driven updates**

```
app/modules/transactions/
├── __init__.py
├── models.py          # JournalEntry, TransactionLine (DATABASE)
├── schemas.py         # Pydantic request/response (API)
├── repository.py      # Database operations (DATA ACCESS)
├── service.py         # Business logic (CORE LOGIC)
└── validators.py      # Accounting rules (RULES)
```

---

## Double-Entry Accounting

### The Fundamental Rule

**EVERY transaction MUST have:**
- At least **2 lines** (double-entry)
- **Debits MUST equal Credits**

```
Example: Cash Sale of $1,000

Dr. Cash                 $1,000  (Asset increases)
    Cr. Sales Revenue            $1,000  (Revenue increases)
                         ------   ------
Total                    $1,000   $1,000  ← MUST BALANCE
```

### Why This Matters

```python
# This is INVALID and will be rejected:
{
  "lines": [
    {"account": "cash", "debit": 1000, "credit": 0}  # Only 1 line
  ]
}
# Error: "A transaction must have at least 2 lines"

# This is INVALID and will be rejected:
{
  "lines": [
    {"account": "cash", "debit": 1000, "credit": 0},
    {"account": "revenue", "debit": 0, "credit": 900}  # Doesn't balance
  ]
}
# Error: "Debits (1000) must equal credits (900)"

# This is VALID:
{
  "lines": [
    {"account": "cash", "debit": 1000, "credit": 0},
    {"account": "revenue", "debit": 0, "credit": 1000}  # Balanced!
  ]
}
```

---

## Models Deep Dive

### File: `backend/app/modules/transactions/models.py`

#### JournalEntry Model

```python
from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class JournalEntry(Base):
    """
    Journal Entry = Complete Transaction

    Think of it as a container for all the debit/credit lines
    that make up one business transaction.

    Example:
        Entry: "Sold services for cash $1,000"
        Lines:
            - Dr. Cash $1,000
            - Cr. Revenue $1,000
    """
    __tablename__ = "journal_entries"

    # === PRIMARY KEY ===
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    """UUID primary key - unique identifier"""

    # === BUSINESS FIELDS ===
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    """
    Unique entry number: JE000001, JE000002, etc.
    Used for human-readable reference.
    """

    date = Column(DateTime, nullable=False, index=True)
    """
    Transaction date - when the transaction occurred.
    Indexed for fast date range queries.
    """

    description = Column(Text, nullable=False)
    """
    What happened: "Sold consulting services to ABC Corp"
    Required field - every transaction needs a description.
    """

    reference = Column(String(100), nullable=True)
    """
    Optional reference: Invoice number, PO number, etc.
    Examples: "INV-001", "PO-12345"
    """

    # === STATE MANAGEMENT ===
    status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.DRAFT,
        nullable=False,
        index=True
    )
    """
    Transaction state lifecycle:
    - DRAFT: Can be edited/deleted
    - POSTED: Immutable, affects balances
    - REVERSED: Cancelled via reversal entry
    """

    source = Column(
        Enum(TransactionSource),
        default=TransactionSource.APP,
        nullable=False
    )
    """
    Where did this transaction come from?
    - APP: Created by user
    - EXCEL_IMPORT: Imported from Excel
    - RECOVERY: Database recovery
    """

    excel_sync_status = Column(
        Enum(ExcelSyncStatus),
        default=ExcelSyncStatus.PENDING,
        nullable=False
    )
    """
    Has this been synced to Excel?
    - PENDING: Not yet synced
    - SYNCED: Successfully written to Excel
    - FAILED: Sync failed
    """

    # === REVERSAL TRACKING ===
    reversed_by_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=True)
    """
    If this entry was reversed, points to the reversal entry.
    Example: Original entry ID=1, reversed by entry ID=2
    """

    reverses_entry_id = Column(String(36), ForeignKey('journal_entries.id'), nullable=True)
    """
    If this entry is a reversal, points to the original entry.
    Example: Reversal entry ID=2, reverses entry ID=1
    """

    # === AUDIT FIELDS ===
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    """When was this entry posted (made immutable)?"""

    created_by = Column(String(50), default="system")
    """Who created this entry? Future: real user IDs"""

    # === RELATIONSHIPS ===
    lines = relationship(
        "TransactionLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",  # Delete lines when entry deleted
        lazy="selectinload"  # Automatically load lines with entry
    )
    """
    The debit/credit lines that make up this transaction.
    cascade="all, delete-orphan" means:
        - If you delete the entry, all lines are deleted too
        - If you remove a line from entry.lines, it's deleted
    lazy="selectinload" means:
        - Lines are always loaded when you fetch an entry
        - No N+1 query problem
    """

    # === COMPUTED PROPERTIES ===
    @property
    def total_debit(self) -> Decimal:
        """
        Sum of all debit amounts in this entry.

        Example:
            Line 1: Dr $1,000
            Line 2: Dr $500
            Total Debit: $1,500
        """
        return sum((line.debit for line in self.lines), Decimal("0.00"))

    @property
    def total_credit(self) -> Decimal:
        """Sum of all credit amounts"""
        return sum((line.credit for line in self.lines), Decimal("0.00"))

    @property
    def is_balanced(self) -> bool:
        """
        Check if entry is balanced (debits = credits).

        This is THE MOST IMPORTANT check in double-entry accounting!
        """
        return self.total_debit == self.total_credit

    @property
    def is_mutable(self) -> bool:
        """
        Can this entry be modified?
        Only DRAFT entries can be edited or deleted.
        """
        return self.status == TransactionStatus.DRAFT

    def __repr__(self):
        return f"<JournalEntry {self.entry_number} - {self.status}>"
```

#### TransactionLine Model

```python
class TransactionLine(Base):
    """
    One line in a journal entry = One debit OR credit

    Example Entry: "Sold services $1,000"
        Line 1: Dr. Cash $1,000 (this is one TransactionLine)
        Line 2: Cr. Revenue $1,000 (this is another TransactionLine)

    RULES:
    - Each line affects exactly ONE account
    - Each line has EITHER debit OR credit (never both)
    - Each line has exactly ONE non-zero amount
    """
    __tablename__ = "transaction_lines"

    # === PRIMARY KEY ===
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # === FOREIGN KEYS ===
    journal_entry_id = Column(String(36), ForeignKey('journal_entries.id'),
                              nullable=False, index=True)
    """Which journal entry does this line belong to?"""

    account_id = Column(String(36), ForeignKey('accounts.id'),
                        nullable=False, index=True)
    """Which account does this line affect?"""

    # === LINE METADATA ===
    line_number = Column(Integer, nullable=False)
    """
    Line sequence within the entry: 1, 2, 3, ...
    Helps maintain order when displaying
    """

    description = Column(Text, nullable=True)
    """
    Optional line-specific description.
    Example: "Payment received via bank transfer"
    """

    # === AMOUNTS (THE MOST IMPORTANT PART!) ===
    debit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """
    Debit amount (left side of T-account)
    - Increases: Assets, Expenses
    - Decreases: Liabilities, Equity, Revenue

    IMPORTANT: Use Decimal, never float!
    Numeric(15, 2) = 15 total digits, 2 after decimal
    Max value: 9,999,999,999,999.99
    """

    credit = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    """
    Credit amount (right side of T-account)
    - Increases: Liabilities, Equity, Revenue
    - Decreases: Assets, Expenses
    """

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # === RELATIONSHIPS ===
    journal_entry = relationship("JournalEntry", back_populates="lines")
    """Link back to the parent journal entry"""

    account = relationship("Account", foreign_keys=[account_id])
    """Link to the account this line affects"""

    # === COMPUTED PROPERTIES ===
    @property
    def debit_decimal(self) -> Decimal:
        """Get debit as Decimal (ensures type safety)"""
        return Decimal(str(self.debit))

    @property
    def credit_decimal(self) -> Decimal:
        """Get credit as Decimal"""
        return Decimal(str(self.credit))

    @property
    def amount(self) -> Decimal:
        """
        Net amount (used for balance calculations)
        - Positive debit = +amount
        - Positive credit = -amount

        Example:
            Dr $1,000: amount = +1,000
            Cr $1,000: amount = -1,000
        """
        return self.debit_decimal - self.credit_decimal

    def __repr__(self):
        return f"<TransactionLine {self.line_number} - Dr:{self.debit} Cr:{self.credit}>"
```

#### Key Design Decisions Explained

**1. Why UUID for IDs?**
```python
id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

# Why not auto-increment integers?
# - UUIDs are globally unique (can merge databases)
# - UUIDs don't leak information (can't guess next ID)
# - UUIDs work in distributed systems
```

**2. Why Decimal for Money?**
```python
debit = Column(Numeric(15, 2), default=Decimal("0.00"))

# Why not Float?
# NEVER use float for money!

# Float problem:
0.1 + 0.2 = 0.30000000000000004  # ❌ Wrong!

# Decimal solution:
Decimal("0.1") + Decimal("0.2") = Decimal("0.3")  # ✅ Exact!
```

**3. Why Both `reversed_by_id` and `reverses_entry_id`?**
```python
# Bidirectional relationship for reversals

# Original entry (ID=1)
entry1.reversed_by_id = "2"  # Points to reversal

# Reversal entry (ID=2)
entry2.reverses_entry_id = "1"  # Points to original

# This allows:
# - Find what reversed an entry: entry.reversed_by
# - Find what an entry reverses: entry.reverses_entry
```

---

## Schemas & Validation

### File: `backend/app/modules/transactions/schemas.py`

#### TransactionLineCreate

```python
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class TransactionLineCreate(BaseModel):
    """
    Schema for creating a transaction line via API.

    This defines what the API accepts and validates.
    """
    account_id: str
    """Which account to debit/credit"""

    description: Optional[str] = None
    """Optional line description"""

    debit: Decimal = Field(Decimal("0.00"), ge=0)
    """
    Debit amount (must be >= 0)
    Field(ge=0) = greater-than-or-equal-to zero
    """

    credit: Decimal = Field(Decimal("0.00"), ge=0)
    """Credit amount (must be >= 0)"""

    @field_validator('debit', 'credit')
    @classmethod
    def validate_amounts(cls, v):
        """
        Ensure amounts are non-negative.

        Why? You can't have negative money amounts.
        Use credit instead of negative debit, and vice versa.
        """
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    def model_post_init(self, __context):
        """
        Called AFTER all fields are set.
        Validates the COMBINATION of fields.

        CRITICAL RULES:
        1. Cannot have both debit AND credit
        2. Must have either debit OR credit
        """
        if self.debit > 0 and self.credit > 0:
            raise ValueError(
                "A line cannot have both debit and credit. "
                "Use separate lines for debit and credit."
            )

        if self.debit == 0 and self.credit == 0:
            raise ValueError(
                "A line must have either debit or credit. "
                "Zero-amount lines are not allowed."
            )

# Example usage:
# VALID:
line1 = TransactionLineCreate(account_id="cash", debit=1000, credit=0)  # ✅
line2 = TransactionLineCreate(account_id="revenue", debit=0, credit=1000)  # ✅

# INVALID:
line3 = TransactionLineCreate(account_id="cash", debit=1000, credit=500)  # ❌
# Error: "A line cannot have both debit and credit"

line4 = TransactionLineCreate(account_id="cash", debit=0, credit=0)  # ❌
# Error: "A line must have either debit or credit"
```

#### JournalEntryCreate

```python
class JournalEntryCreate(BaseModel):
    """
    Schema for creating a complete journal entry.

    This is what the API POST /transactions endpoint accepts.
    """
    date: datetime
    """When did this transaction occur?"""

    description: str = Field(..., min_length=1, max_length=500)
    """
    What happened?
    ... = required field
    min_length=1 = can't be empty
    max_length=500 = reasonable limit
    """

    reference: Optional[str] = Field(None, max_length=100)
    """Optional reference (invoice number, etc.)"""

    lines: List[TransactionLineCreate] = Field(..., min_length=2)
    """
    The debit/credit lines
    min_length=2 = MUST have at least 2 lines (double-entry!)
    """

    @field_validator('lines')
    @classmethod
    def validate_lines(cls, v):
        """
        Validate the lines list AFTER it's been created.

        This is THE MOST IMPORTANT validation in the entire system!
        """
        # Check #1: Minimum 2 lines
        if len(v) < 2:
            raise ValueError(
                "A transaction must have at least 2 lines for double-entry accounting. "
                "Every debit needs a corresponding credit."
            )

        # Check #2: Calculate totals
        total_debit = sum(line.debit for line in v)
        total_credit = sum(line.credit for line in v)

        # Check #3: MUST BALANCE!
        if total_debit != total_credit:
            raise ValueError(
                f"Transaction is not balanced! "
                f"Debits ({total_debit}) must equal credits ({total_credit}). "
                f"Difference: {total_debit - total_credit}"
            )

        return v

# Example valid request:
{
  "date": "2024-12-15T10:00:00",
  "description": "Sold consulting services",
  "reference": "INV-001",
  "lines": [
    {
      "account_id": "cash-account-uuid",
      "description": "Cash received",
      "debit": 1000.00,
      "credit": 0.00
    },
    {
      "account_id": "revenue-account-uuid",
      "description": "Service revenue",
      "debit": 0.00,
      "credit": 1000.00
    }
  ]
}
# ✅ Valid: 2 lines, balanced ($1,000 = $1,000)

# Example invalid request:
{
  "lines": [
    {"account_id": "cash", "debit": 1000, "credit": 0}
  ]
}
# ❌ Error: "A transaction must have at least 2 lines"

# Example invalid request:
{
  "lines": [
    {"account_id": "cash", "debit": 1000, "credit": 0},
    {"account_id": "revenue", "debit": 0, "credit": 900}
  ]
}
# ❌ Error: "Debits (1000) must equal credits (900)"
```

---

## Service Layer

### File: `backend/app/modules/transactions/service.py`

This is where ALL the business logic lives!

#### post_transaction() - Most Important Method

```python
async def post_transaction(self, entry_id: str) -> JournalEntry:
    """
    POST a transaction = Make it IMMUTABLE and update account balances.

    This is the MOST CRITICAL operation in the entire system!

    What happens when you post:
    1. Transaction becomes IMMUTABLE (can never be edited)
    2. Account balances are UPDATED
    3. Events are PUBLISHED (Excel sync, audit log)
    4. Status changes: DRAFT → POSTED

    Args:
        entry_id: UUID of the journal entry to post

    Returns:
        The posted journal entry

    Raises:
        ValueError: If entry not found, already posted, or not balanced

    Example:
        # Create draft transaction
        entry = await service.create_transaction(data)
        # entry.status = DRAFT

        # Post it
        entry = await service.post_transaction(entry.id)
        # entry.status = POSTED
        # entry.posted_at = now
        # Account balances updated
    """
    # Step 1: Fetch the entry from database
    entry = await self.repository.get_by_id(entry_id)
    if not entry:
        raise ValueError(f"Transaction {entry_id} not found")

    # Step 2: Validate that it CAN be posted
    self.validator.validate_can_post(entry)
    """
    This checks:
    - Status is DRAFT (not already POSTED or REVERSED)
    - Entry is balanced (debits = credits)
    - Has at least 2 lines
    """

    # Step 3: Update ALL account balances
    for line in entry.lines:
        # Calculate amount to apply to account
        # Debit = positive, Credit = negative
        amount = line.debit_decimal - line.credit_decimal

        # Update the account's balance
        await self.account_service.apply_transaction_line(
            account_id=line.account_id,
            amount=amount,
            reason=f"Transaction {entry.entry_number}"
        )

        """
        How balance updates work:

        Example: Asset account (Cash)
        - Start: balance = 0
        - Line: Dr. Cash $1,000 (amount = +1,000)
        - End: balance = 1,000

        Example: Revenue account (Sales)
        - Start: balance = 0
        - Line: Cr. Sales $1,000 (amount = -1,000)
        - End: balance = -1,000

        Why negative for revenue? Because revenue increases with CREDITS,
        and we store credit increases as negative amounts. This is
        accounting convention - revenue/liability/equity accounts have
        credit balances (shown as negative in our system, positive to users).
        """

    # Step 4: Mark entry as POSTED
    entry = await self.repository.mark_posted(entry)
    """
    This updates:
    - status = POSTED
    - posted_at = current timestamp
    - updated_at = current timestamp
    """

    # Step 5: Publish event (triggers Excel sync, audit log, etc.)
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
```

#### reverse_transaction() - Reversal Logic

```python
async def reverse_transaction(
    self,
    entry_id: str,
    reason: str,
    reversal_date: Optional[datetime] = None
) -> JournalEntry:
    """
    REVERSE a posted transaction (undo it properly).

    This is the CORRECT way to "delete" a posted transaction.
    We NEVER actually delete - we create an opposite transaction.

    Why? For audit trail and accounting compliance.

    Example:
        Original Entry (ID=1):
        Dr. Cash $1,000
            Cr. Revenue $1,000

        Reversal Entry (ID=2):
        Dr. Revenue $1,000  ← Opposite!
            Cr. Cash $1,000  ← Opposite!

        Net Effect: $1,000 - $1,000 = $0 (like it never happened)

    Args:
        entry_id: Original entry to reverse
        reason: Why are we reversing? (required for audit)
        reversal_date: When to date the reversal (defaults to now)

    Returns:
        The newly created reversal entry

    Process:
        1. Validate original can be reversed
        2. Create new entry with OPPOSITE lines
        3. Auto-POST the reversal
        4. Mark original as REVERSED
        5. Publish event
    """
    # Step 1: Get original entry
    original_entry = await self.repository.get_by_id(entry_id)
    if not original_entry:
        raise ValueError(f"Transaction {entry_id} not found")

    # Step 2: Validate can reverse
    self.validator.validate_can_reverse(original_entry)
    """
    Checks:
    - Status is POSTED (can't reverse DRAFT or already REVERSED)
    - Not already reversed (can't reverse twice)
    """

    # Step 3: Create reversal entry
    reversal_date = reversal_date or datetime.utcnow()
    reversal_number = await self.repository.get_next_entry_number("REV")

    reversal_entry = JournalEntry(
        entry_number=reversal_number,  # REV000001
        date=reversal_date,
        description=f"REVERSAL: {reason} (Original: {original_entry.entry_number})",
        reference=original_entry.reference,
        status=TransactionStatus.DRAFT,  # Start as draft
        source=TransactionSource.APP,
        reverses_entry_id=original_entry.id  # Link to original
    )

    # Step 4: Create OPPOSITE lines
    for line in original_entry.lines:
        reversal_line = TransactionLine(
            account_id=line.account_id,
            line_number=line.line_number,
            description=f"Reversal of {line.description or ''}",
            debit=line.credit,   # ← SWAP!
            credit=line.debit    # ← SWAP!
        )
        reversal_entry.lines.append(reversal_line)

    """
    Original:
    Dr. Cash $1,000  →  Cr. Cash $1,000
    Cr. Revenue $1,000  →  Dr. Revenue $1,000
    """

    # Step 5: Save reversal entry
    reversal_entry = await self.repository.create(reversal_entry)

    # Step 6: Auto-POST the reversal (immediately applies it)
    reversal_entry = await self.post_transaction(reversal_entry.id)

    # Step 7: Mark original as REVERSED
    await self.repository.mark_reversed(original_entry, reversal_entry.id)

    # Step 8: Publish event
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
```

---

## Complete Usage Example

```python
from datetime import datetime
from decimal import Decimal

# === STEP 1: Create a transaction (DRAFT) ===

create_data = JournalEntryCreate(
    date=datetime(2024, 12, 15, 10, 0, 0),
    description="Sold consulting services to ABC Corp",
    reference="INV-001",
    lines=[
        TransactionLineCreate(
            account_id="cash-account-uuid",
            description="Cash received via bank transfer",
            debit=Decimal("1000.00"),
            credit=Decimal("0.00")
        ),
        TransactionLineCreate(
            account_id="revenue-account-uuid",
            description="Consulting revenue",
            debit=Decimal("0.00"),
            credit=Decimal("1000.00")
        )
    ]
)

# Create via service
entry = await transaction_service.create_transaction(create_data)

# At this point:
# - entry.status = DRAFT
# - entry.entry_number = "JE000001"
# - Account balances NOT yet updated
# - Can still edit or delete

# === STEP 2: Post the transaction (make immutable) ===

entry = await transaction_service.post_transaction(entry.id)

# Now:
# - entry.status = POSTED
# - entry.posted_at = current timestamp
# - entry.is_mutable = False
# - Cash account balance increased by $1,000
# - Revenue account balance increased by $1,000
# - Excel file updated
# - Audit log created

# === STEP 3: Oops, need to reverse ===

reversal = await transaction_service.reverse_transaction(
    entry_id=entry.id,
    reason="Customer requested refund"
)

# Result:
# - reversal.entry_number = "REV000001"
# - reversal.status = POSTED
# - reversal.reverses_entry_id = entry.id
# - Original entry.reversed_by_id = reversal.id
# - Original entry.status = REVERSED
# - Balances back to original (reversed)
```

---

## Testing Examples

```python
import pytest
from decimal import Decimal

async def test_create_transaction(db_session):
    """Test creating a draft transaction"""
    service = TransactionService(db_session)

    data = JournalEntryCreate(
        date=datetime.now(),
        description="Test transaction",
        lines=[
            TransactionLineCreate(account_id="acc1", debit=100, credit=0),
            TransactionLineCreate(account_id="acc2", debit=0, credit=100)
        ]
    )

    entry = await service.create_transaction(data)

    assert entry.status == TransactionStatus.DRAFT
    assert entry.is_balanced == True
    assert len(entry.lines) == 2

async def test_post_transaction_updates_balances(db_session):
    """Test that posting updates account balances"""
    # Create accounts
    cash = Account(code="1000", name="Cash", account_type=AccountType.ASSET, balance=0)
    revenue = Account(code="4000", name="Revenue", account_type=AccountType.REVENUE, balance=0)

    # Create and post transaction
    entry = await service.create_transaction(...)
    await service.post_transaction(entry.id)

    # Check balances updated
    assert cash.balance == 1000
    assert revenue.balance == -1000  # Revenue has credit balance

async def test_cannot_post_unbalanced_transaction(db_session):
    """Test validation prevents posting unbalanced entries"""
    data = JournalEntryCreate(
        date=datetime.now(),
        description="Unbalanced",
        lines=[
            TransactionLineCreate(account_id="acc1", debit=100, credit=0),
            TransactionLineCreate(account_id="acc2", debit=0, credit=50)  # Wrong!
        ]
    )

    with pytest.raises(ValueError, match="not balanced"):
        await service.create_transaction(data)
```

---

## Summary

The Transactions Module is the **core of the accounting system**. It implements:

✅ **Double-entry accounting** (debits = credits)
✅ **Immutability** (POSTED transactions cannot change)
✅ **Proper reversals** (no deletion of posted entries)
✅ **Decimal math** (accurate money calculations)
✅ **Event-driven updates** (Excel sync, audit logs)
✅ **Multi-layer validation** (schemas, validators, service)

Understanding this module is **essential** to understanding the entire application!

---

[← Back to Index](../INDEX.md) | [Next: Accounting Principles →](ACCOUNTING_PRINCIPLES.md)
