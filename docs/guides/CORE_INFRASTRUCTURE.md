# 🏗️ Core Infrastructure - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Configuration System](#configuration-system)
3. [Database Layer](#database-layer)
4. [Event System](#event-system)
5. [Dependency Injection](#dependency-injection)
6. [Code Examples](#code-examples)

---

## Overview

The **Core Infrastructure** provides the foundation for the entire application. It consists of three main components:

1. **Configuration** (`config.py`) - Settings management
2. **Database** (`database.py`) - SQLAlchemy async engine
3. **Events** (`events.py`) - Event bus system

```
app/core/
├── __init__.py          # Exports
├── config.py           # Settings class
├── database.py         # Database engine & sessions
└── events.py           # Event bus implementation
```

---

## Configuration System

### File: `backend/app/core/config.py`

#### Purpose
Centralized configuration management using Pydantic for type safety and validation.

#### Code Walkthrough

```python
from pydantic import BaseModel
from pathlib import Path

class Settings(BaseModel):
    """Application settings with type validation"""

    # Application metadata
    APP_NAME: str = "Daybook Desktop Application"
    APP_VERSION: str = "2.0"
    DEBUG: bool = True

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 5000

    # Database connection string
    DATABASE_URL: str = "sqlite+aiosqlite:///./daybook.db"
    DATABASE_ECHO: bool = False  # Log SQL queries

    # Excel file path
    EXCEL_FILE_PATH: str = "daybook.xlsx"
    EXCEL_AUTO_SYNC: bool = True

    # Base directory for file paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent

# Global singleton instance
settings = Settings()
```

#### Why This Design?

1. **Type Safety**: Pydantic validates types at runtime
2. **Environment Variables**: Can be overridden via `.env` file
3. **Single Source of Truth**: One place for all configuration
4. **IDE Support**: Type hints enable autocomplete

#### Usage Examples

```python
# Import settings anywhere
from app.core.config import settings

# Access configuration
print(settings.APP_NAME)  # "Daybook Desktop Application"
print(settings.DATABASE_URL)  # "sqlite+aiosqlite:///./daybook.db"

# Use in other modules
def create_connection():
    return create_engine(settings.DATABASE_URL)
```

#### Environment Variables

Create `.env` file to override defaults:

```bash
# .env
DEBUG=False
PORT=8000
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/daybook
EXCEL_FILE_PATH=/data/daybook.xlsx
```

---

## Database Layer

### File: `backend/app/core/database.py`

#### Purpose
Provides async database engine, session management, and base model class.

#### Code Walkthrough

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from .config import settings

# 1. CREATE ASYNC ENGINE
engine = create_async_engine(
    settings.DATABASE_URL,      # Connection string
    echo=settings.DATABASE_ECHO, # Log SQL (debug)
    future=True                  # Use SQLAlchemy 2.0 API
)

# 2. CREATE SESSION FACTORY
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,        # Async session class
    expire_on_commit=False,     # Keep objects after commit
    autocommit=False,           # Manual commit control
    autoflush=False             # Manual flush control
)

# 3. BASE CLASS FOR ALL MODELS
Base = declarative_base()

# 4. DEPENDENCY FOR FASTAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()  # Always close

# 5. CONTEXT MANAGER FOR NON-FASTAPI CODE
@asynccontextmanager
async def get_db_context():
    """
    Context manager for database sessions outside FastAPI.

    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(Account))
            accounts = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 6. INITIALIZATION
async def init_db():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 7. CLEANUP
async def close_db():
    """Close all database connections"""
    await engine.dispose()
```

#### Key Concepts Explained

**1. Why Async?**
```python
# Synchronous (blocking)
result = db.execute(query)  # Waits for database

# Asynchronous (non-blocking)
result = await db.execute(query)  # Other requests can proceed
```

**2. Session Lifecycle**
```
Request → Create Session → Execute Queries → Commit → Close Session
             ↓                  ↓              ↓           ↓
          AsyncSessionLocal  db.execute()  db.commit()  finally
```

**3. Commit vs Flush**
```python
# Flush: Send to DB but don't commit
await db.flush()  # SQL sent, transaction open
obj.id  # ID available, but can still rollback

# Commit: Finalize transaction
await db.commit()  # Transaction committed, cannot rollback
```

#### Usage Patterns

**Pattern 1: In FastAPI Endpoints**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@app.post("/accounts")
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db)  # ← Dependency injection
):
    account = Account(**data.dict())
    db.add(account)
    await db.flush()  # Get ID
    return account
```

**Pattern 2: In Event Handlers**
```python
from app.core.database import get_db_context

async def on_transaction_posted(event):
    async with get_db_context() as db:
        # Fetch data
        result = await db.execute(
            select(JournalEntry).where(JournalEntry.id == event.data["id"])
        )
        entry = result.scalar_one_or_none()

        # Process
        if entry:
            await sync_to_excel(entry)
```

**Pattern 3: In Service Layer**
```python
class AccountService:
    def __init__(self, db: AsyncSession):
        self.db = db  # Injected from FastAPI

    async def create_account(self, data):
        account = Account(**data.dict())
        self.db.add(account)
        await self.db.flush()
        return account
```

---

## Event System

### File: `backend/app/core/events.py`

#### Purpose
Implements event-driven architecture for decoupled communication between modules.

#### Code Walkthrough

```python
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

# 1. EVENT TYPES
class EventType(str, Enum):
    """All event types in the system"""

    # Transaction events
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_POSTED = "transaction.posted"
    TRANSACTION_REVERSED = "transaction.reversed"

    # Account events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_BALANCE_UPDATED = "account.balance_updated"

    # Excel sync events
    EXCEL_SYNC_REQUESTED = "excel.sync_requested"
    EXCEL_SYNC_COMPLETED = "excel.sync_completed"
    EXCEL_SYNC_FAILED = "excel.sync_failed"

# 2. EVENT DATA STRUCTURE
@dataclass
class DomainEvent:
    """
    Immutable event that happened in the system.

    Attributes:
        event_type: What happened
        data: Event payload (dict)
        timestamp: When it happened
        user_id: Who triggered it
    """
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str = "system"

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()

# 3. EVENT BUS
class EventBus:
    """
    In-memory event bus for publish-subscribe pattern.

    How it works:
    1. Modules subscribe handlers to event types
    2. When event is published, all handlers are called
    3. Handlers run concurrently (async)
    """

    def __init__(self):
        # Storage: {EventType: [handler1, handler2, ...]}
        self._handlers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Register a handler for an event type.

        Args:
            event_type: Type of event to listen for
            handler: Async function to call when event fires

        Example:
            event_bus.subscribe(
                EventType.TRANSACTION_POSTED,
                on_transaction_posted
            )
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        print(f"✓ Subscribed {handler.__name__} to {event_type}")

    async def publish(self, event: DomainEvent):
        """
        Publish event to all subscribers.

        Args:
            event: The event to publish

        Process:
            1. Get all handlers for this event type
            2. Call each handler concurrently
            3. Catch and log any errors (don't fail)
        """
        print(f"📢 Publishing: {event.event_type}")

        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            print(f"⚠️  No handlers for {event.event_type}")
            return

        # Run all handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Async handler - run directly
                    tasks.append(handler(event))
                else:
                    # Sync handler - run in thread pool
                    tasks.append(asyncio.to_thread(handler, event))
            except Exception as e:
                print(f"❌ Handler {handler.__name__} error: {e}")

        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def clear(self):
        """Clear all handlers (useful for testing)"""
        self._handlers.clear()

# 4. GLOBAL SINGLETON
event_bus = EventBus()
```

#### Event Flow Diagram

```
Service Layer
     ↓
Publishes Event
     ↓
Event Bus
     ↓
├─→ Handler 1 (Excel Sync)
├─→ Handler 2 (Audit Log)
└─→ Handler 3 (Notifications)
     ↓
All run concurrently
```

#### Usage Examples

**Example 1: Publishing an Event**
```python
from app.core.events import event_bus, EventType, DomainEvent
from datetime import datetime

# In service layer after posting transaction
async def post_transaction(entry_id: str):
    # ... business logic ...
    entry = await repository.mark_posted(entry)

    # Publish event
    await event_bus.publish(DomainEvent(
        event_type=EventType.TRANSACTION_POSTED,
        data={
            "entry_id": entry.id,
            "entry_number": entry.entry_number,
            "total_debit": str(entry.total_debit)
        },
        timestamp=datetime.utcnow(),
        user_id="current_user"
    ))
```

**Example 2: Subscribing to Events**
```python
from app.core.events import event_bus, EventType, DomainEvent

# Define handler function
async def on_transaction_posted(event: DomainEvent):
    """Called when transaction is posted"""
    entry_id = event.data["entry_id"]
    print(f"Transaction {entry_id} posted at {event.timestamp}")

    # Do something (sync to Excel, send email, etc.)
    await sync_to_excel(entry_id)

# Register handler on app startup
def register_handlers():
    event_bus.subscribe(
        EventType.TRANSACTION_POSTED,
        on_transaction_posted
    )
```

**Example 3: Multiple Handlers**
```python
# Handler 1: Excel Sync
async def sync_to_excel(event: DomainEvent):
    entry_id = event.data["entry_id"]
    await excel_service.sync_transaction(entry_id)

# Handler 2: Send Notification
async def send_notification(event: DomainEvent):
    entry_number = event.data["entry_number"]
    await email_service.send(f"Transaction {entry_number} posted")

# Handler 3: Update Dashboard
async def update_dashboard(event: DomainEvent):
    await websocket.broadcast({"type": "transaction_posted"})

# Subscribe all handlers to same event
event_bus.subscribe(EventType.TRANSACTION_POSTED, sync_to_excel)
event_bus.subscribe(EventType.TRANSACTION_POSTED, send_notification)
event_bus.subscribe(EventType.TRANSACTION_POSTED, update_dashboard)
```

---

## Dependency Injection

### How FastAPI Dependency Injection Works

```python
# 1. Define dependency
async def get_db() -> AsyncSession:
    """Provides database session"""
    async with AsyncSessionLocal() as session:
        yield session

# 2. Use in endpoint
@app.post("/accounts")
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db)  # ← Dependency injected
):
    # db is automatically provided
    account = Account(**data.dict())
    db.add(account)
    await db.commit()
    return account

# 3. Dependency chain
def get_account_service(db: AsyncSession = Depends(get_db)):
    """Provides AccountService with injected DB"""
    return AccountService(db)

@app.post("/accounts")
async def create_account(
    data: AccountCreate,
    service: AccountService = Depends(get_account_service)
):
    # Both db and service are injected
    return await service.create_account(data)
```

---

## Complete Code Examples

### Example 1: Creating a New Module

```python
# 1. Create model (models.py)
from app.core.database import Base
from sqlalchemy import Column, String, Numeric

class Product(Base):
    __tablename__ = "products"
    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

# 2. Create schema (schemas.py)
from pydantic import BaseModel
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    price: Decimal

# 3. Create repository (repository.py)
class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product):
        self.db.add(product)
        await self.db.flush()
        return product

# 4. Create service (service.py)
class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)

    async def create_product(self, data: ProductCreate):
        product = Product(**data.dict())
        return await self.repository.create(product)

# 5. Create API endpoint (api.py)
from fastapi import Depends
from app.core.database import get_db

@app.post("/products")
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.create_product(data)
```

### Example 2: Using Events

```python
# 1. Define event type (in events.py)
class EventType(str, Enum):
    PRODUCT_CREATED = "product.created"

# 2. Publish event (in service)
async def create_product(self, data):
    product = await self.repository.create(Product(**data.dict()))

    # Publish event
    await event_bus.publish(DomainEvent(
        event_type=EventType.PRODUCT_CREATED,
        data={"product_id": product.id, "name": product.name},
        timestamp=datetime.utcnow()
    ))

    return product

# 3. Create handler
async def on_product_created(event: DomainEvent):
    product_id = event.data["product_id"]
    print(f"New product created: {product_id}")

# 4. Subscribe handler (in app startup)
def register_handlers():
    event_bus.subscribe(
        EventType.PRODUCT_CREATED,
        on_product_created
    )
```

---

## Best Practices

### ✅ DO

1. **Use dependency injection**
```python
# Good
def create_account(db: AsyncSession = Depends(get_db)):
    service = AccountService(db)
```

2. **Always use async/await**
```python
# Good
result = await db.execute(query)
```

3. **Handle exceptions in event handlers**
```python
async def handler(event):
    try:
        await do_something()
    except Exception as e:
        logger.error(f"Handler failed: {e}")
```

### ❌ DON'T

1. **Don't create your own sessions**
```python
# Bad
session = AsyncSessionLocal()
await session.execute(query)
```

2. **Don't use synchronous code**
```python
# Bad
result = db.execute(query)  # Missing await
```

3. **Don't let event handlers fail**
```python
# Bad
async def handler(event):
    await risky_operation()  # No try-catch
```

---

## Testing

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()

async def test_create_account(db_session):
    """Test account creation"""
    service = AccountService(db_session)
    account = await service.create_account(AccountCreate(
        code="1000",
        name="Cash",
        account_type=AccountType.ASSET
    ))
    assert account.code == "1000"
```

---

## Summary

The Core Infrastructure provides:

✅ **Configuration**: Type-safe settings management
✅ **Database**: Async SQLAlchemy with session management
✅ **Events**: Decoupled event-driven architecture
✅ **DI**: Dependency injection for clean code

This foundation enables scalable, maintainable, and testable code throughout the application.

---

[← Back to Index](../INDEX.md) | [Next: Accounts Module →](ACCOUNTS_MODULE.md)
