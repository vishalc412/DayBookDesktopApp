# 📖 Glossary - Terms & Definitions

## Accounting Terms

### Account
A record in the chart of accounts that tracks a specific type of asset, liability, equity, revenue, or expense.

Example: "Cash", "Accounts Receivable", "Sales Revenue"

### Account Balance
The current total amount in an account, calculated from all posted transactions affecting that account.

### Account Type
Category of account. The five types are:
- **ASSET**: Things owned (Cash, Equipment, Inventory)
- **LIABILITY**: Things owed (Loans, Accounts Payable)
- **EQUITY**: Owner's stake (Capital, Retained Earnings)
- **REVENUE**: Money earned (Sales, Service Revenue)
- **EXPENSE**: Costs incurred (Rent, Salaries, Utilities)

### Accounting Equation
The fundamental accounting formula:
```
Assets = Liabilities + Equity
```

This must ALWAYS balance.

### Chart of Accounts (COA)
The complete list of all accounts used by a business, typically organized by account type and numbered for reference.

Example:
```
1000 - Cash (Asset)
1100 - Accounts Receivable (Asset)
2000 - Accounts Payable (Liability)
4000 - Sales Revenue (Revenue)
5000 - Rent Expense (Expense)
```

### Credit (Cr.)
The right side of a T-account. Credits:
- **Increase**: Liabilities, Equity, Revenue
- **Decrease**: Assets, Expenses

Example: "Cr. Sales Revenue $1,000" means revenue increased by $1,000

### Debit (Dr.)
The left side of a T-account. Debits:
- **Increase**: Assets, Expenses
- **Decrease**: Liabilities, Equity, Revenue

Example: "Dr. Cash $1,000" means cash increased by $1,000

### Double-Entry Accounting
An accounting system where every transaction has at least two entries: a debit and a credit, and the total debits must equal total credits.

Example:
```
Sale of $1,000:
Dr. Cash $1,000
    Cr. Revenue $1,000
```

### Fiscal Period
A time period for which financial statements are prepared, typically a month, quarter, or year.

### General Ledger
The complete record of all accounts and transactions in the accounting system.

### Journal Entry
A complete transaction record consisting of:
- Date
- Description
- Two or more transaction lines (debits and credits)
- Reference information

Also called a "transaction" in our system.

### Posting
The act of finalizing a transaction, making it immutable and applying it to account balances.

Before posting: Transaction is in DRAFT status
After posting: Transaction is POSTED and affects balances

### Reversal
The proper way to "undo" a posted transaction by creating an opposite transaction that cancels out the original.

Original:
```
Dr. Cash $1,000
    Cr. Revenue $1,000
```

Reversal:
```
Dr. Revenue $1,000
    Cr. Cash $1,000
```

Net effect: Zero (as if original never happened)

### T-Account
A visual representation of an account showing debits on the left and credits on the right.

```
        Cash (Asset)
    ─────────────────────
    Dr. |          | Cr.
  1,000 |      500 |
  2,000 |          |
    ─────────────────────
  3,000 |      500 |
    ─────────────────────
    Balance: 2,500 (Dr.)
```

### Transaction
See "Journal Entry"

### Transaction Line
One debit or credit within a journal entry. Each line affects exactly one account.

### Trial Balance
A report showing the balance of every account, used to verify that total debits equal total credits.

---

## Technical Terms

### API (Application Programming Interface)
A set of endpoints that allow external programs to interact with the application.

Example: `POST /api/transactions` creates a new transaction

### Async/Await
Python's way of handling asynchronous operations (non-blocking code).

```python
# Blocking (bad)
result = get_data()  # Waits

# Non-blocking (good)
result = await get_data()  # Other code can run
```

### Base Model
In SQLAlchemy, the parent class that all database models inherit from.

```python
Base = declarative_base()

class Account(Base):  # Inherits from Base
    __tablename__ = "accounts"
```

### CASCADE
Database option that automatically deletes related records.

Example: When you delete a JournalEntry, all its TransactionLines are automatically deleted.

### Context Manager
Python's `with` statement for resource management.

```python
async with get_db_context() as db:
    # db is automatically closed when done
    result = await db.execute(query)
```

### Decimal
Python type for exact decimal arithmetic (required for money).

```python
from decimal import Decimal

price = Decimal("19.99")  # Exact
price = 19.99  # Float (WRONG for money!)
```

### Dependency Injection
A pattern where dependencies are "injected" rather than created internally.

```python
@app.post("/accounts")
async def create_account(
    db: AsyncSession = Depends(get_db)  # ← Injected
):
    pass
```

### Domain Event
A notification that something important happened in the system.

Example: `TRANSACTION_POSTED` event fires when a transaction is posted

### DTO (Data Transfer Object)
An object that carries data between layers. In our system, Pydantic schemas are DTOs.

### Entity
A business object with a unique identity (like Account, Transaction).

### Event Bus
A system for publishing and subscribing to events.

```python
# Subscribe
event_bus.subscribe(EventType.TRANSACTION_POSTED, handler)

# Publish
await event_bus.publish(event)
```

### FastAPI
The Python web framework we use for creating the REST API.

### Foreign Key
A database field that links to another table's primary key.

```python
account_id = Column(String(36), ForeignKey('accounts.id'))
```

### Immutability
The property of being unchangeable. Posted transactions are immutable.

### JSON (JavaScript Object Notation)
A text format for data exchange.

```json
{
  "name": "Cash",
  "balance": 1000.00
}
```

### Migration
A database schema change (add table, add column, etc.)

### ORM (Object-Relational Mapping)
Mapping between Python objects and database tables. We use SQLAlchemy.

```python
# Python object
account = Account(name="Cash")

# Becomes SQL
# INSERT INTO accounts (name) VALUES ('Cash')
```

### Pydantic
Python library for data validation using type hints.

```python
class AccountCreate(BaseModel):
    name: str  # Must be a string
    balance: Decimal  # Must be a Decimal
```

### Repository Pattern
A layer that handles all database operations for an entity.

```python
class AccountRepository:
    async def create(self, account): ...
    async def get_by_id(self, id): ...
```

### REST (Representational State Transfer)
An architectural style for web APIs.

```
GET    /accounts     # List
POST   /accounts     # Create
GET    /accounts/1   # Read
PUT    /accounts/1   # Update
DELETE /accounts/1   # Delete
```

### Schema
In Pydantic: A definition of what data looks like.
In Database: The structure of tables and columns.

### Service Layer
Where business logic lives.

```python
class AccountService:
    async def create_account(self, data):
        # Business logic here
        pass
```

### Session
A database connection that groups operations into a transaction.

```python
async with AsyncSession() as session:
    session.add(account)
    await session.commit()
```

### SQLAlchemy
Python ORM (Object-Relational Mapping) library for database access.

### State Machine
An object that can be in different states with defined transitions.

```
DRAFT → POST → POSTED → REVERSE → REVERSED
```

### UUID (Universally Unique Identifier)
A 128-bit unique identifier.

```
Example: "550e8400-e29b-41d4-a716-446655440000"
```

### Validation
Checking that data meets certain rules before processing.

```python
@field_validator('balance')
def validate_balance(cls, v):
    if v < 0:
        raise ValueError("Balance cannot be negative")
    return v
```

### Validator Pattern
A dedicated class for validation logic.

```python
class TransactionValidator:
    @staticmethod
    def validate_balanced(entry):
        if entry.total_debit != entry.total_credit:
            raise ValueError("Not balanced")
```

---

## Application-Specific Terms

### DRAFT Status
A transaction that can still be edited or deleted. Doesn't affect account balances yet.

### POSTED Status
A transaction that has been finalized. It is now immutable and has affected account balances.

### REVERSED Status
A transaction that has been cancelled via a reversal entry.

### Excel Sync
The automatic process of writing posted transactions to an Excel file.

### Entry Number
A unique human-readable identifier for a transaction.

Examples: `JE000001`, `JE000002`, `REV000001`

### Audit Trail
An immutable log of all changes in the system.

### Event Handler
A function that runs when a specific event is published.

```python
async def on_transaction_posted(event):
    # Do something when transaction is posted
    pass
```

---

## Abbreviations

- **API**: Application Programming Interface
- **CRUD**: Create, Read, Update, Delete
- **DB**: Database
- **DDD**: Domain-Driven Design
- **DTO**: Data Transfer Object
- **FK**: Foreign Key
- **JSON**: JavaScript Object Notation
- **ORM**: Object-Relational Mapping
- **PK**: Primary Key
- **REST**: Representational State Transfer
- **SQL**: Structured Query Language
- **UUID**: Universally Unique Identifier

---

## Symbols & Notations

### Dr.
Abbreviation for "Debit"

### Cr.
Abbreviation for "Credit"

### $
Dollar sign (currency symbol)

### ✅
Checkmark (valid/correct)

### ❌
X mark (invalid/incorrect)

### →
Arrow (transition/flow)

---

[← Back to Index](INDEX.md)
