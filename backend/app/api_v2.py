"""
FastAPI Application v2.0
Enterprise-grade architecture with double-entry accounting
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core import settings, init_db, close_db, get_db
from app.modules.accounts.service import AccountService
from app.modules.accounts.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.modules.transactions.service import TransactionService
from app.modules.transactions.schemas import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    PostTransactionRequest,
    ReverseTransactionRequest,
)
from app.modules.audit.service import AuditService
from app.modules.excel_sync.service import register_excel_sync_handlers
from app.shared.enums import TransactionStatus, AccountType
from app.modules.auth.api import router as auth_router
from app.modules.daybook.api import router as daybook_router

# NEW - V2.0 Enhancement Modules
from app.modules.security.api import router as security_router
from app.modules.savings.api import router as savings_router
from app.modules.precious_metals.api import router as metals_router
from app.modules.expenses.api import router as expenses_router
import app.models_registry  # Import to register all models with SQLAlchemy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print("Enterprise-Grade Double-Entry Accounting System")
    print("=" * 60)

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Register event handlers
    register_excel_sync_handlers()
    print("✓ Excel sync handlers registered")

    # Initialize default accounts
    # from app.core.database import get_db_context
    # async with get_db_context() as db:
    #     account_service = AccountService(db)
    #     accounts = await account_service.get_all_accounts()
    #     if not accounts:
    #         await account_service.initialize_default_accounts()
    #         print("✓ Default chart of accounts created")

    yield

    # Shutdown
    await close_db()
    print("Database connections closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Enterprise-grade double-entry accounting with real-time Excel sync",
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================== ROUTERS ====================
    # Existing routers
    app.include_router(auth_router)
    app.include_router(daybook_router)

    # NEW - V2.0 Enhancement Routers
    app.include_router(security_router, prefix="/api")
    app.include_router(savings_router, prefix="/api")
    app.include_router(metals_router, prefix="/api")
    app.include_router(expenses_router, prefix="/api")

    # ==================== HEALTH ====================

    @app.get("/api/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "app_name": settings.APP_NAME,
        }

    # ==================== ACCOUNTS ====================

    @app.post(
        "/api/accounts",
        response_model=AccountResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Accounts"],
    )
    async def create_account(data: AccountCreate, db: AsyncSession = Depends(get_db)):
        """Create a new account"""
        try:
            service = AccountService(db)
            account = await service.create_account(data)

            # Audit log
            audit = AuditService(db)
            await audit.log_create(
                entity_type="account",
                entity_id=account.id,
                description=f"Created account {account.code} - {account.name}",
                data={
                    "code": account.code,
                    "name": account.name,
                    "type": account.account_type.value,
                },
            )

            return account
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.get("/api/accounts", response_model=List[AccountResponse], tags=["Accounts"])
    async def get_accounts(
        account_type: Optional[AccountType] = None,
        is_active: bool = True,
        db: AsyncSession = Depends(get_db),
    ):
        """Get all accounts"""
        service = AccountService(db)
        accounts = await service.get_all_accounts(account_type, is_active)
        return accounts

    @app.get(
        "/api/accounts/{account_id}", response_model=AccountResponse, tags=["Accounts"]
    )
    async def get_account(account_id: str, db: AsyncSession = Depends(get_db)):
        """Get account by ID"""
        service = AccountService(db)
        account = await service.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )
        return account

    @app.put(
        "/api/accounts/{account_id}", response_model=AccountResponse, tags=["Accounts"]
    )
    async def update_account(
        account_id: str, data: AccountUpdate, db: AsyncSession = Depends(get_db)
    ):
        """Update account"""
        try:
            service = AccountService(db)
            account = await service.update_account(account_id, data)

            # Audit log
            audit = AuditService(db)
            await audit.log_update(
                entity_type="account",
                entity_id=account.id,
                description=f"Updated account {account.code}",
                old_data={},  # TODO: Add old values
                new_data=data.model_dump(exclude_unset=True),
            )

            return account
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # ==================== TRANSACTIONS ====================

    @app.post(
        "/api/transactions",
        response_model=JournalEntryResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Transactions"],
    )
    async def create_transaction(
        data: JournalEntryCreate, db: AsyncSession = Depends(get_db)
    ):
        """Create a new transaction (DRAFT status)"""
        try:
            service = TransactionService(db)
            entry = await service.create_transaction(data)

            # Audit log
            audit = AuditService(db)
            await audit.log_create(
                entity_type="transaction",
                entity_id=entry.id,
                description=f"Created transaction {entry.entry_number}",
                data={
                    "entry_number": entry.entry_number,
                    "description": entry.description,
                },
            )

            return entry
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.get(
        "/api/transactions",
        response_model=List[JournalEntryResponse],
        tags=["Transactions"],
    )
    async def get_transactions(
        status_filter: Optional[TransactionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
    ):
        """Get all transactions"""
        service = TransactionService(db)
        transactions = await service.get_all_transactions(
            status=status_filter,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return transactions

    @app.get(
        "/api/transactions/{entry_id}",
        response_model=JournalEntryResponse,
        tags=["Transactions"],
    )
    async def get_transaction(entry_id: str, db: AsyncSession = Depends(get_db)):
        """Get transaction by ID"""
        service = TransactionService(db)
        entry = await service.get_transaction(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
        return entry

    @app.put(
        "/api/transactions/{entry_id}",
        response_model=JournalEntryResponse,
        tags=["Transactions"],
    )
    async def update_transaction(
        entry_id: str, data: JournalEntryUpdate, db: AsyncSession = Depends(get_db)
    ):
        """Update a DRAFT transaction"""
        try:
            service = TransactionService(db)
            entry = await service.update_draft_transaction(entry_id, data)

            # Audit log
            audit = AuditService(db)
            await audit.log_update(
                entity_type="transaction",
                entity_id=entry.id,
                description=f"Updated transaction {entry.entry_number}",
                old_data={},
                new_data=data.model_dump(exclude_unset=True),
            )

            return entry
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.post(
        "/api/transactions/{entry_id}/post",
        response_model=JournalEntryResponse,
        tags=["Transactions"],
    )
    async def post_transaction(
        entry_id: str,
        request: PostTransactionRequest,
        db: AsyncSession = Depends(get_db),
    ):
        """Post a transaction (makes it immutable and updates balances)"""
        try:
            service = TransactionService(db)
            entry = await service.post_transaction(entry_id)

            # Audit log
            audit = AuditService(db)
            await audit.log_post(
                entity_type="transaction",
                entity_id=entry.id,
                description=f"Posted transaction {entry.entry_number}",
                data={
                    "entry_number": entry.entry_number,
                    "total_debit": str(entry.total_debit),
                    "total_credit": str(entry.total_credit),
                },
            )

            return entry
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.post(
        "/api/transactions/{entry_id}/reverse",
        response_model=JournalEntryResponse,
        tags=["Transactions"],
    )
    async def reverse_transaction(
        entry_id: str,
        request: ReverseTransactionRequest,
        db: AsyncSession = Depends(get_db),
    ):
        """Reverse a POSTED transaction"""
        try:
            service = TransactionService(db)
            reversal_entry = await service.reverse_transaction(
                entry_id, request.reason, request.date
            )

            # Audit log
            audit = AuditService(db)
            await audit.log_reverse(
                entity_type="transaction",
                entity_id=entry_id,
                description=f"Reversed transaction, created {reversal_entry.entry_number}",
                data={"reversal_entry_id": reversal_entry.id, "reason": request.reason},
            )

            return reversal_entry
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.delete("/api/transactions/{entry_id}", tags=["Transactions"])
    async def delete_transaction(entry_id: str, db: AsyncSession = Depends(get_db)):
        """Delete a DRAFT transaction"""
        try:
            service = TransactionService(db)
            success = await service.delete_draft_transaction(entry_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found or cannot be deleted",
                )
            return {"success": True, "message": "Transaction deleted"}
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return app
