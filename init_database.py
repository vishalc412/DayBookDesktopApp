#!/usr/bin/env python3
"""
Database Initialization Script
Initializes all database tables for DayBook v2.0

This script will create all missing tables including:
- expenses and expense_budgets
- savings_accounts, savings_entries, savings_goals
- precious_metals_accounts, precious_metals_transactions, precious_metals_rates
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import init_db, engine
from app.models_registry import *  # Import all models to register them


async def main():
    """Initialize database with all tables"""
    print("=" * 60)
    print("DayBook v2.0 - Database Initialization")
    print("=" * 60)
    print()

    print("This will create all missing database tables.")
    print("Existing tables and data will NOT be affected.")
    print()

    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    print("Initializing database tables...")

    try:
        await init_db()
        print("✓ Database initialized successfully!")
        print()
        print("The following tables have been created/verified:")
        print("  - expenses, expense_budgets, expense_categories_custom")
        print("  - savings_accounts, savings_entries, savings_goals")
        print("  - precious_metals_accounts, precious_metals_transactions, precious_metals_rates")
        print()
        print("You can now start the application with: ./start.sh (or start.bat)")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
