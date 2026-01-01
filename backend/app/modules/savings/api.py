"""
Savings Module - API Endpoints
Complete REST API for savings and investments tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from .models import SavingsAccount, SavingsEntry, SavingsGoal, AccountStatus, EntryType
from .schemas import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsAccountResponse,
    SavingsEntryCreate,
    SavingsEntryResponse,
    SavingsSummary,
    AccountSummary,
    MaturityItem,
    ROICalculationRequest,
    RDCalculationRequest,
    PPFCalculationRequest,
    SavingsGoalCreate,
    SavingsGoalResponse
)
from app.modules.calculations.roi_calculator import roi_calculator


router = APIRouter(prefix="/savings", tags=["Savings"])


# ==================== Accounts ====================

@router.post("/accounts", response_model=SavingsAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_account(
    account_data: SavingsAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new savings account

    Automatically calculates expected maturity amount and maturity date based on account type
    """
    try:
        # Create account
        account = SavingsAccount(**account_data.model_dump())

        # Calculate maturity date if not provided and tenure is given
        if not account.maturity_date and account.tenure_months:
            from dateutil.relativedelta import relativedelta
            account.maturity_date = account.opening_date + relativedelta(months=account.tenure_months)

        # Calculate expected maturity amount if applicable
        if account.interest_rate and account.initial_amount > 0:
            if account.account_type.value == "Fixed Deposit":
                # Calculate FD maturity
                result = roi_calculator.compound_interest(
                    principal=account.initial_amount,
                    rate=account.interest_rate,
                    time_years=account.tenure_months / 12 if account.tenure_months else 1,
                    compounding_frequency=4  # Quarterly by default
                )
                account.expected_maturity_amount = result['maturity_amount']

            elif account.account_type.value == "Recurring Deposit" and account.monthly_installment:
                # Calculate RD maturity
                result = roi_calculator.recurring_deposit(
                    monthly_installment=account.monthly_installment,
                    rate=account.interest_rate,
                    tenure_months=account.tenure_months or 12
                )
                account.expected_maturity_amount = result['maturity_amount']

        # Set initial balance
        account.current_balance = account.initial_amount

        db.add(account)
        await db.commit()
        await db.refresh(account)

        return account

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}"
        )


@router.get("/accounts", response_model=List[SavingsAccountResponse])
async def get_savings_accounts(
    account_type: Optional[str] = None,
    status_filter: Optional[AccountStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all savings accounts with optional filters
    """
    try:
        query = select(SavingsAccount)

        # Apply filters
        conditions = []
        if account_type:
            conditions.append(SavingsAccount.account_type == account_type)
        if status_filter:
            conditions.append(SavingsAccount.status == status_filter)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(SavingsAccount.opening_date.desc())

        result = await db.execute(query)
        accounts = result.scalars().all()

        return accounts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accounts: {str(e)}"
        )


@router.get("/accounts/{account_id}", response_model=SavingsAccountResponse)
async def get_savings_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get single savings account by ID
    """
    try:
        query = select(SavingsAccount).where(SavingsAccount.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        return account

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch account: {str(e)}"
        )


@router.put("/accounts/{account_id}", response_model=SavingsAccountResponse)
async def update_savings_account(
    account_id: int,
    account_data: SavingsAccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update savings account
    """
    try:
        query = select(SavingsAccount).where(SavingsAccount.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Update fields
        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)

        await db.commit()
        await db.refresh(account)

        return account

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account: {str(e)}"
        )


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_savings_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete savings account (cascades to entries)
    """
    try:
        query = select(SavingsAccount).where(SavingsAccount.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        await db.delete(account)
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )


# ==================== Entries ====================

@router.post("/entries", response_model=SavingsEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_entry(
    entry_data: SavingsEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create savings entry (deposit/withdrawal/interest)

    Automatically updates account balance
    """
    try:
        # Verify account exists
        account_query = select(SavingsAccount).where(SavingsAccount.id == entry_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate new balance
        current_balance = account.current_balance

        if entry_data.entry_type in [EntryType.DEPOSIT, EntryType.INTEREST_CREDIT, EntryType.DIVIDEND]:
            new_balance = current_balance + entry_data.amount
        elif entry_data.entry_type in [EntryType.WITHDRAWAL, EntryType.FEE]:
            new_balance = current_balance - entry_data.amount
            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance for withdrawal"
                )
        elif entry_data.entry_type == EntryType.MATURITY:
            new_balance = 0  # Maturity closes the account
            account.actual_maturity_amount = entry_data.amount
            account.status = AccountStatus.MATURED
            account.closing_date = entry_data.entry_date
        else:
            new_balance = current_balance

        # Create entry
        entry = SavingsEntry(
            **entry_data.model_dump(),
            balance_after=new_balance
        )

        # Update account balance
        account.current_balance = new_balance

        # Update total interest if it's interest credit
        if entry_data.entry_type == EntryType.INTEREST_CREDIT:
            account.total_interest_earned += entry_data.amount

        db.add(entry)
        await db.commit()
        await db.refresh(entry)

        return entry

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entry: {str(e)}"
        )


@router.get("/entries", response_model=List[SavingsEntryResponse])
async def get_savings_entries(
    account_id: Optional[int] = None,
    entry_type: Optional[EntryType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get savings entries with filters
    """
    try:
        query = select(SavingsEntry)

        # Apply filters
        conditions = []
        if account_id:
            conditions.append(SavingsEntry.account_id == account_id)
        if entry_type:
            conditions.append(SavingsEntry.entry_type == entry_type)
        if start_date:
            conditions.append(SavingsEntry.entry_date >= start_date)
        if end_date:
            conditions.append(SavingsEntry.entry_date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(SavingsEntry.entry_date.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        entries = result.scalars().all()

        return entries

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch entries: {str(e)}"
        )


# ==================== Dashboard & Analytics ====================

@router.get("/dashboard", response_model=SavingsSummary)
async def get_savings_dashboard(db: AsyncSession = Depends(get_db)):
    """
    Get savings dashboard summary
    """
    try:
        # Total accounts
        total_query = select(func.count(SavingsAccount.id))
        total_result = await db.execute(total_query)
        total_accounts = total_result.scalar() or 0

        # Active accounts
        active_query = select(func.count(SavingsAccount.id)).where(
            SavingsAccount.status == AccountStatus.ACTIVE
        )
        active_result = await db.execute(active_query)
        active_accounts = active_result.scalar() or 0

        # Total savings
        savings_query = select(func.sum(SavingsAccount.current_balance))
        savings_result = await db.execute(savings_query)
        total_savings = savings_result.scalar() or 0.0

        # Total interest
        interest_query = select(func.sum(SavingsAccount.total_interest_earned))
        interest_result = await db.execute(interest_query)
        total_interest = interest_result.scalar() or 0.0

        # Maturing soon (next 30 days)
        today = date.today()
        thirty_days = today + timedelta(days=30)

        maturing_query = select(
            func.count(SavingsAccount.id),
            func.sum(SavingsAccount.expected_maturity_amount)
        ).where(
            and_(
                SavingsAccount.maturity_date.isnot(None),
                SavingsAccount.maturity_date >= today,
                SavingsAccount.maturity_date <= thirty_days,
                SavingsAccount.status == AccountStatus.ACTIVE
            )
        )
        maturing_result = await db.execute(maturing_query)
        maturing_data = maturing_result.one()

        return SavingsSummary(
            total_accounts=total_accounts,
            active_accounts=active_accounts,
            total_savings=total_savings,
            total_interest_earned=total_interest,
            maturing_soon_count=maturing_data[0] or 0,
            maturing_soon_amount=maturing_data[1] or 0.0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


@router.get("/maturities", response_model=List[MaturityItem])
async def get_maturity_schedule(
    days: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get maturity schedule for upcoming maturities
    """
    try:
        today = date.today()
        end_date = today + timedelta(days=days)

        query = select(SavingsAccount).where(
            and_(
                SavingsAccount.maturity_date.isnot(None),
                SavingsAccount.maturity_date >= today,
                SavingsAccount.maturity_date <= end_date,
                SavingsAccount.status == AccountStatus.ACTIVE
            )
        ).order_by(SavingsAccount.maturity_date)

        result = await db.execute(query)
        accounts = result.scalars().all()

        maturity_items = []
        for account in accounts:
            days_remaining = (account.maturity_date - today).days
            maturity_items.append(MaturityItem(
                account_id=account.id,
                account_name=account.account_name,
                account_type=account.account_type,
                bank_or_institution=account.bank_or_institution,
                maturity_date=account.maturity_date,
                expected_amount=account.expected_maturity_amount or account.current_balance,
                current_balance=account.current_balance,
                days_remaining=days_remaining
            ))

        return maturity_items

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch maturity schedule: {str(e)}"
        )


# ==================== Calculations ====================

@router.post("/calculate/roi")
async def calculate_roi(request: ROICalculationRequest):
    """
    Calculate ROI for given parameters
    """
    try:
        # Determine compounding frequency
        freq_map = {
            "Yearly": 1,
            "Half-Yearly": 2,
            "Quarterly": 4,
            "Monthly": 12
        }
        frequency = freq_map.get(request.compounding_frequency.value, 1)

        result = roi_calculator.compound_interest(
            principal=request.principal,
            rate=request.interest_rate,
            time_years=request.tenure_months / 12,
            compounding_frequency=frequency
        )

        # Add maturity date
        from dateutil.relativedelta import relativedelta
        today = date.today()
        maturity_date = today + relativedelta(months=request.tenure_months)

        result['maturity_date'] = maturity_date.isoformat()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/calculate/rd")
async def calculate_rd(request: RDCalculationRequest):
    """
    Calculate Recurring Deposit maturity
    """
    try:
        result = roi_calculator.recurring_deposit(
            monthly_installment=request.monthly_installment,
            rate=request.interest_rate,
            tenure_months=request.tenure_months
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/calculate/ppf")
async def calculate_ppf(request: PPFCalculationRequest):
    """
    Calculate PPF maturity
    """
    try:
        result = roi_calculator.ppf_maturity(
            annual_deposit=request.annual_deposit,
            rate=request.interest_rate,
            years=request.years
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )
