# Daybook Desktop v2.0 - Enterprise Architecture

## 🏗️ Architecture Overview

This document describes the enterprise-grade architecture implementation of the Daybook Desktop Application v2.0.

## 📊 Key Principles

### 1. **Double-Entry Accounting**
- ✅ Every transaction has **at least 2 lines**
- ✅ **Debits MUST equal Credits** (enforced at validation layer)
- ✅ Transactions are **immutable once POSTED**
- ✅ Deletions are **NEVER allowed** - use **REVERSAL** instead

### 2. **Money as Decimal**
- ❌ **NO floats** for money calculations
- ✅ All amounts use **Python Decimal** type
- ✅ Database stores as **NUMERIC(15, 2)**

### 3. **Transaction States**
```
DRAFT → POST → [POSTED] → REVERSE → [REVERSED]
  ↓       ↓        ↓          ↓           ↓
Edit   Validate  Immutable  Create    Both
Delete  Balance             Reversal  Immutable
               Update
```

- **DRAFT**: Can be edited/deleted
- **POSTED**: Immutable, affects account balances
- **REVERSED**: Cancelled via reversal entry

### 4. **Event-Driven Architecture**
- Events trigger side effects (Excel sync, audit logs)
- Decoupled modules communicate via events
- No tight coupling between modules

### 5. **Domain-Driven Design**
- Clear module boundaries
- Each module has: `models.py`, `schemas.py`, `repository.py`, `service.py`, `validators.py`
- Business logic ONLY in service layer

## 🗂️ Module Structure

```
backend/app/
├── core/                   # Infrastructure
│   ├── config.py          # Settings & environment
│   ├── database.py        # SQLAlchemy async engine
│   └── events.py          # Event bus system
│
├── shared/                 # Cross-cutting concerns
│   └── enums.py           # Shared enumerations
│
├── modules/                # Business domains
│   ├── accounts/          # Chart of Accounts
│   │   ├── models.py      # SQLAlchemy ORM
│   │   ├── schemas.py     # Pydantic request/response
│   │   ├── repository.py  # Database access ONLY
│   │   ├── service.py     # Business logic ONLY
│   │   └── validators.py  # Business rules
│   │
│   ├── transactions/      # Journal Entries
│   │   ├── models.py      # JournalEntry, TransactionLine
│   │   ├── schemas.py     # Double-entry validation
│   │   ├── repository.py  # Transaction DB ops
│   │   ├── service.py     # Post/Reverse logic
│   │   └── validators.py  # Accounting rules
│   │
│   ├── audit/             # Audit Trail
│   │   ├── models.py      # Immutable audit log
│   │   └── service.py     # Append-only logging
│   │
│   └── excel_sync/        # Excel Synchronization
│       └── service.py     # Event-driven sync
│
├── api_v2.py              # FastAPI application
└── main_v2.py             # Application entry point
```

## 🔄 Data Flow

### Creating & Posting a Transaction

```
1. API receives JournalEntryCreate
   ↓
2. TransactionService.create_transaction()
   - Validates dates
   - Validates accounts exist
   - Creates JournalEntry (DRAFT)
   - Creates TransactionLines
   - Validates: min 2 lines, debits = credits
   ↓
3. Save to Database (status=DRAFT)
   ↓
4. Publish TRANSACTION_CREATED event
   ↓
5. Return to user (editable)

---

When user POSTs transaction:

1. API calls TransactionService.post_transaction()
   ↓
2. Validate can post (is DRAFT, is balanced)
   ↓
3. Apply to account balances
   - For each line:
     amount = debit - credit
     account.balance += amount
   ↓
4. Update status to POSTED, set posted_at
   ↓
5. Publish TRANSACTION_POSTED event
   ↓
6. Event Handler: Excel Sync
   - Writes transaction to Excel file
   - Updates sync status
   ↓
7. Event Handler: Audit Log
   - Creates immutable audit entry
```

### Reversing a Transaction

```
1. API calls TransactionService.reverse_transaction()
   ↓
2. Validate: transaction is POSTED, not already reversed
   ↓
3. Create new JournalEntry (reversal)
   - Swap debits ↔ credits
   - Link to original via reverses_entry_id
   ↓
4. Auto-POST the reversal
   - Balances automatically corrected
   ↓
5. Mark original as REVERSED
   ↓
6. Publish TRANSACTION_REVERSED event
   ↓
7. Both entries synced to Excel
```

## 📐 Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    account_type ENUM('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'),
    parent_id VARCHAR(36),
    balance NUMERIC(15, 2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Journal Entries Table
```sql
CREATE TABLE journal_entries (
    id VARCHAR(36) PRIMARY KEY,
    entry_number VARCHAR(50) UNIQUE NOT NULL,
    date DATETIME NOT NULL,
    description TEXT NOT NULL,
    reference VARCHAR(100),
    status ENUM('DRAFT', 'POSTED', 'REVERSED') DEFAULT 'DRAFT',
    source ENUM('APP', 'EXCEL_IMPORT', 'RECOVERY'),
    excel_sync_status ENUM('PENDING', 'SYNCED', 'FAILED'),
    reversed_by_id VARCHAR(36),
    reverses_entry_id VARCHAR(36),
    created_at DATETIME,
    updated_at DATETIME,
    posted_at DATETIME,
    created_by VARCHAR(50)
);
```

### Transaction Lines Table
```sql
CREATE TABLE transaction_lines (
    id VARCHAR(36) PRIMARY KEY,
    journal_entry_id VARCHAR(36) NOT NULL,
    account_id VARCHAR(36) NOT NULL,
    line_number INTEGER NOT NULL,
    description TEXT,
    debit NUMERIC(15, 2) DEFAULT 0.00,
    credit NUMERIC(15, 2) DEFAULT 0.00,
    created_at DATETIME,
    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(50) DEFAULT 'system',
    action VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    old_data JSON,
    new_data JSON,
    changes JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(200)
);
```

## 🎯 API Endpoints

### Accounts
```
POST   /api/accounts              # Create account
GET    /api/accounts              # List all accounts
GET    /api/accounts/{id}         # Get account details
PUT    /api/accounts/{id}         # Update account
```

### Transactions
```
POST   /api/transactions          # Create transaction (DRAFT)
GET    /api/transactions          # List transactions
GET    /api/transactions/{id}     # Get transaction details
PUT    /api/transactions/{id}     # Update DRAFT transaction
DELETE /api/transactions/{id}     # Delete DRAFT transaction

POST   /api/transactions/{id}/post      # POST transaction (immutable)
POST   /api/transactions/{id}/reverse   # REVERSE posted transaction
```

## 🧪 Usage Examples

### Create a Transaction

```json
POST /api/transactions
{
  "date": "2024-12-15T10:00:00",
  "description": "Sale of services",
  "reference": "INV-001",
  "lines": [
    {
      "account_id": "cash-account-id",
      "description": "Cash received",
      "debit": 1000.00,
      "credit": 0.00
    },
    {
      "account_id": "revenue-account-id",
      "description": "Service revenue",
      "debit": 0.00,
      "credit": 1000.00
    }
  ]
}
```

### Post a Transaction

```json
POST /api/transactions/{id}/post
{
  "confirm": true
}
```

### Reverse a Transaction

```json
POST /api/transactions/{id}/reverse
{
  "reason": "Customer refund requested",
  "date": "2024-12-16T10:00:00"
}
```

## 🔒 Business Rules Enforced

### At Validation Layer
- ✅ Minimum 2 lines per transaction
- ✅ Debits MUST equal credits
- ✅ Amounts must be non-negative
- ✅ Line cannot have both debit AND credit
- ✅ Line must have either debit OR credit
- ✅ All accounts must exist and be active
- ✅ Transaction date cannot be in future

### At Service Layer
- ✅ Only DRAFT transactions can be edited
- ✅ Only DRAFT transactions can be deleted
- ✅ Only POSTED transactions can be reversed
- ✅ Balances update ONLY on POST
- ✅ Reversal creates opposite transaction
- ✅ Original transaction marked as REVERSED

### At Database Layer
- ✅ Unique entry numbers
- ✅ Unique account codes
- ✅ Foreign key constraints
- ✅ Decimal precision for money

## 📊 Accounting Equation

```
Assets = Liabilities + Equity

Revenue increases Equity
Expenses decrease Equity

Debit increases: Assets, Expenses
Credit increases: Liabilities, Equity, Revenue
```

## 🚀 Running v2

```bash
cd backend
python main_v2.py
```

Access API docs at: http://127.0.0.1:5000/api/docs

## 🔄 Migration from v1

v1 used simple daybook entries. v2 uses proper double-entry accounting.

**Key Differences:**

| Feature | v1 | v2 |
|---------|----|----|
| Accounting | Single entry | Double entry |
| Money type | Float | Decimal |
| Immutability | No | Yes (POSTED) |
| Deletion | Allowed | Only DRAFT |
| Database | Excel only | SQLite + Excel |
| Events | No | Yes |
| Audit | No | Yes |
| States | None | DRAFT/POSTED/REVERSED |

## 🎓 Learning Resources

- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)
- [Accounting Equation](https://www.investopedia.com/terms/a/accounting-equation.asp)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

---

**Built with enterprise-grade practices for production accounting systems** 🎯
