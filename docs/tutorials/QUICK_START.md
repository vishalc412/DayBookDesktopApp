# 🚀 Quick Start Tutorial - Get Running in 5 Minutes

This tutorial will get you up and running with the Daybook Desktop Application v2.0 in just 5 minutes!

---

## Prerequisites Check

Before starting, make sure you have:

```bash
# Check Python version (need 3.11+)
python3 --version
# Should show: Python 3.11.x or higher

# Check pip
pip --version
```

If you don't have Python 3.11+, [download it here](https://www.python.org/downloads/).

---

## Step 1: Install Dependencies (1 minute)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

You should see packages installing. This takes about 30-60 seconds.

---

## Step 2: Start the Server (30 seconds)

```bash
# Make sure you're in the backend directory with venv activated
python main_v2.py
```

You should see:

```
============================================================
Daybook Desktop Application v2.0
Enterprise-Grade Double-Entry Accounting System
============================================================
✓ Database initialized
✓ Excel sync handlers registered
✓ Default chart of accounts created
============================================================
Database: sqlite+aiosqlite:///./daybook.db
Excel File: daybook.xlsx
Server: http://127.0.0.1:5000
API Docs: http://127.0.0.1:5000/api/docs
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:5000
```

**✅ Your server is now running!**

---

## Step 3: Explore the API (1 minute)

Open your browser and go to:

**http://127.0.0.1:5000/api/docs**

You'll see the interactive API documentation (Swagger UI).

---

## Step 4: Create Your First Account (1 minute)

### Using the API Docs (Browser)

1. In Swagger UI, find **POST /api/accounts**
2. Click "Try it out"
3. Enter this JSON:

```json
{
  "code": "1000",
  "name": "Cash Account",
  "account_type": "ASSET"
}
```

4. Click "Execute"
5. You should see **201 Created** response!

### Using cURL (Command Line)

```bash
curl -X POST http://127.0.0.1:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "code": "1000",
    "name": "Cash Account",
    "account_type": "ASSET"
  }'
```

### Create a Few More Accounts

```bash
# Revenue account
curl -X POST http://127.0.0.1:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4000",
    "name": "Sales Revenue",
    "account_type": "REVENUE"
  }'

# Expense account
curl -X POST http://127.0.0.1:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "code": "5000",
    "name": "Rent Expense",
    "account_type": "EXPENSE"
  }'
```

---

## Step 5: Create Your First Transaction (2 minutes)

Now let's record a sale!

### Get Account IDs

First, get your account IDs:

```bash
curl http://127.0.0.1:5000/api/accounts
```

Copy the `id` values for Cash (1000) and Revenue (4000).

### Create a Transaction

Replace `CASH_ACCOUNT_ID` and `REVENUE_ACCOUNT_ID` with your actual IDs:

```bash
curl -X POST http://127.0.0.1:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-15T10:00:00",
    "description": "Sold consulting services to ABC Corp",
    "reference": "INV-001",
    "lines": [
      {
        "account_id": "CASH_ACCOUNT_ID",
        "description": "Cash received",
        "debit": 1000.00,
        "credit": 0.00
      },
      {
        "account_id": "REVENUE_ACCOUNT_ID",
        "description": "Service revenue",
        "debit": 0.00,
        "credit": 1000.00
      }
    ]
  }'
```

**✅ You just created your first double-entry transaction!**

The response shows your transaction in DRAFT status.

---

## Step 6: Post the Transaction (30 seconds)

Posting makes the transaction immutable and updates account balances.

Copy the transaction `id` from the previous response, then:

```bash
curl -X POST http://127.0.0.1:5000/api/transactions/TRANSACTION_ID/post \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

**✅ Transaction is now POSTED!**

- Account balances are updated
- Transaction is immutable (can't be edited)
- Entry is synced to Excel file

---

## Step 7: Check Excel File (30 seconds)

Look in your `backend/` directory. You should see `daybook.xlsx`!

Open it - you'll see your transaction formatted nicely:

| Entry Number | Date | Description | Account | Debit | Credit | Reference | Status |
|--------------|------|-------------|---------|-------|--------|-----------|--------|
| JE000001 | 2024-12-15 | Sold consulting... | Cash | 1000.00 | | INV-001 | POSTED |
| JE000001 | 2024-12-15 | Sold consulting... | Revenue | | 1000.00 | INV-001 | POSTED |

---

## Next Steps

### Try These Operations

**View All Transactions**
```bash
curl http://127.0.0.1:5000/api/transactions
```

**View Account Balances**
```bash
curl http://127.0.0.1:5000/api/accounts
```

**Reverse a Transaction**
```bash
curl -X POST http://127.0.0.1:5000/api/transactions/TRANSACTION_ID/reverse \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer requested refund",
    "date": "2024-12-16T10:00:00"
  }'
```

### Explore More

- 📖 Read the [Transaction Module Guide](../guides/TRANSACTIONS_MODULE.md) to understand how it all works
- 🏗️ Check the [Architecture Overview](../architecture/OVERVIEW.md) to see the big picture
- 📚 Review [Accounting Principles](../guides/ACCOUNTING_PRINCIPLES.md) to learn double-entry accounting
- 🔌 Explore the [API Reference](../api/OVERVIEW.md) for all available endpoints

---

## Common Commands Reference

```bash
# Start server
python main_v2.py

# Create account
curl -X POST http://127.0.0.1:5000/api/accounts -H "Content-Type: application/json" -d '{...}'

# List accounts
curl http://127.0.0.1:5000/api/accounts

# Create transaction (DRAFT)
curl -X POST http://127.0.0.1:5000/api/transactions -H "Content-Type: application/json" -d '{...}'

# Post transaction (make immutable)
curl -X POST http://127.0.0.1:5000/api/transactions/{id}/post -H "Content-Type: application/json" -d '{"confirm": true}'

# Reverse transaction
curl -X POST http://127.0.0.1:5000/api/transactions/{id}/reverse -H "Content-Type: application/json" -d '{"reason": "..."}'

# View API docs
# Open browser: http://127.0.0.1:5000/api/docs
```

---

## Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in backend/.env
PORT=8000

# Or use environment variable
PORT=8000 python main_v2.py
```

**Dependencies won't install?**
```bash
# Upgrade pip first
pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

**Database errors?**
```bash
# Delete and recreate database
rm daybook.db
python main_v2.py  # Will recreate automatically
```

---

## What You've Accomplished! 🎉

In just 5 minutes, you've:

✅ Installed and started the application
✅ Created accounts in your chart of accounts
✅ Created a properly balanced double-entry transaction
✅ Posted the transaction (made it immutable)
✅ Saw the transaction automatically sync to Excel
✅ Learned the basic API operations

You're now ready to explore the full power of enterprise-grade accounting!

---

[← Back to Index](../INDEX.md) | [Next: Managing Accounts →](MANAGE_ACCOUNTS.md)
