"""
Precious Metals Module - API Endpoints
Complete REST API for gold and silver portfolio tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from .models import (
    PreciousMetalsAccount,
    PreciousMetalsTransaction,
    PreciousMetalsRate,
    MetalType,
    MarketType,
    TransactionType
)
from .schemas import (
    PreciousMetalsAccountCreate,
    PreciousMetalsAccountUpdate,
    PreciousMetalsAccountResponse,
    IndianGoldTransactionCreate,
    IndianSilverTransactionCreate,
    InternationalBullionTransactionCreate,
    SGBTransactionCreate,
    PreciousMetalsTransactionResponse,
    PreciousMetalsRateCreate,
    PreciousMetalsRateResponse,
    PortfolioSummary,
    AccountPortfolioSummary,
    IndianGoldCostRequest,
    IndianSilverCostRequest,
    InternationalBullionCostRequest,
    SGBReturnsRequest,
    PortfolioValuationRequest
)
from app.modules.calculations.precious_metals_calculator import precious_metals_calculator
from app.modules.calculations.roi_calculator import roi_calculator


router = APIRouter(prefix="/api/precious-metals", tags=["Precious Metals"])


# ==================== Accounts ====================

@router.post("/accounts", response_model=PreciousMetalsAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_precious_metals_account(
    account_data: PreciousMetalsAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new precious metals account (portfolio)
    """
    try:
        account = PreciousMetalsAccount(**account_data.model_dump())

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


@router.get("/accounts", response_model=List[PreciousMetalsAccountResponse])
async def get_precious_metals_accounts(
    metal_type: Optional[MetalType] = None,
    market_type: Optional[MarketType] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all precious metals accounts with optional filters
    """
    try:
        query = select(PreciousMetalsAccount)

        conditions = []
        if metal_type:
            conditions.append(PreciousMetalsAccount.metal_type == metal_type)
        if market_type:
            conditions.append(PreciousMetalsAccount.market_type == market_type)
        if is_active is not None:
            conditions.append(PreciousMetalsAccount.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(PreciousMetalsAccount.created_at.desc())

        result = await db.execute(query)
        accounts = result.scalars().all()

        return accounts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accounts: {str(e)}"
        )


@router.get("/accounts/{account_id}", response_model=PreciousMetalsAccountResponse)
async def get_precious_metals_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get single precious metals account by ID
    """
    try:
        query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == account_id)
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


@router.put("/accounts/{account_id}", response_model=PreciousMetalsAccountResponse)
async def update_precious_metals_account(
    account_id: int,
    account_data: PreciousMetalsAccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update precious metals account
    """
    try:
        query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

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
async def delete_precious_metals_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete precious metals account (cascades to transactions)
    """
    try:
        query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        db.delete(account)
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )


# ==================== Transactions ====================

@router.post("/transactions/indian-gold", response_model=PreciousMetalsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_indian_gold_transaction(
    transaction_data: IndianGoldTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create Indian gold transaction with automatic cost calculation
    """
    try:
        # Verify account exists
        account_query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == transaction_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate cost using calculator
        cost_calculation = precious_metals_calculator.indian_gold_cost(
            quantity_grams=transaction_data.quantity_grams,
            gold_rate_per_10g=transaction_data.gold_rate_per_10g,
            purity=transaction_data.purity.value,
            making_charges_type=transaction_data.making_charges_type,
            making_charges_value=transaction_data.making_charges_value,
            include_gst=transaction_data.include_gst,
            include_hallmark=transaction_data.include_hallmark,
            num_items=transaction_data.item_count
        )

        # Create transaction
        transaction = PreciousMetalsTransaction(
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            purchase_form=transaction_data.purchase_form,
            purity=transaction_data.purity,
            quantity_grams=transaction_data.quantity_grams,
            gold_rate_per_10g=transaction_data.gold_rate_per_10g,
            base_metal_cost=cost_calculation['base_gold_cost'],
            making_charges=cost_calculation['making_charges'],
            hallmark_charges=cost_calculation['hallmark_charges'],
            gst_amount=cost_calculation['gst_amount'],
            total_cost=cost_calculation['total_cost'],
            effective_rate_per_gram=cost_calculation['effective_rate_per_gram'],
            vendor_or_buyer=transaction_data.vendor_or_buyer,
            bill_number=transaction_data.bill_number,
            item_description=transaction_data.item_description,
            item_count=transaction_data.item_count,
            notes=transaction_data.notes,
            making_charges_type=transaction_data.making_charges_type
        )

        # Update account totals
        if transaction_data.transaction_type == TransactionType.BUY:
            account.total_quantity_grams += transaction_data.quantity_grams
            account.total_invested += cost_calculation['total_cost']
        elif transaction_data.transaction_type == TransactionType.SELL:
            account.total_quantity_grams -= transaction_data.quantity_grams
            # Don't reduce invested (for profit/loss calculation)

        # Update average purchase price
        if account.total_quantity_grams > 0:
            account.average_purchase_price = account.total_invested / account.total_quantity_grams
        else:
            account.average_purchase_price = 0

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )


@router.post("/transactions/indian-silver", response_model=PreciousMetalsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_indian_silver_transaction(
    transaction_data: IndianSilverTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create Indian silver transaction with automatic cost calculation
    """
    try:
        # Verify account
        account_query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == transaction_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate cost
        cost_calculation = precious_metals_calculator.indian_silver_cost(
            quantity_grams=transaction_data.quantity_grams,
            silver_rate_per_kg=transaction_data.silver_rate_per_kg,
            making_charges_type=transaction_data.making_charges_type,
            making_charges_value=transaction_data.making_charges_value,
            include_gst=transaction_data.include_gst,
            include_hallmark=transaction_data.include_hallmark,
            num_items=transaction_data.item_count
        )

        # Create transaction
        transaction = PreciousMetalsTransaction(
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            purchase_form=transaction_data.purchase_form,
            quantity_grams=transaction_data.quantity_grams,
            silver_rate_per_kg=transaction_data.silver_rate_per_kg,
            base_metal_cost=cost_calculation['base_silver_cost'],
            making_charges=cost_calculation['making_charges'],
            hallmark_charges=cost_calculation['hallmark_charges'],
            gst_amount=cost_calculation['gst_amount'],
            total_cost=cost_calculation['total_cost'],
            effective_rate_per_gram=cost_calculation['effective_rate_per_gram'],
            vendor_or_buyer=transaction_data.vendor_or_buyer,
            bill_number=transaction_data.bill_number,
            item_description=transaction_data.item_description,
            item_count=transaction_data.item_count,
            notes=transaction_data.notes,
            making_charges_type=transaction_data.making_charges_type
        )

        # Update account
        if transaction_data.transaction_type == TransactionType.BUY:
            account.total_quantity_grams += transaction_data.quantity_grams
            account.total_invested += cost_calculation['total_cost']
        elif transaction_data.transaction_type == TransactionType.SELL:
            account.total_quantity_grams -= transaction_data.quantity_grams

        if account.total_quantity_grams > 0:
            account.average_purchase_price = account.total_invested / account.total_quantity_grams

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )


@router.post("/transactions/international", response_model=PreciousMetalsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_international_transaction(
    transaction_data: InternationalBullionTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create international bullion transaction
    """
    try:
        # Verify account
        account_query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == transaction_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate cost
        cost_calculation = precious_metals_calculator.international_bullion_cost(
            quantity_troy_oz=transaction_data.quantity_troy_oz,
            usd_per_troy_oz=transaction_data.usd_per_troy_oz,
            usd_to_inr_rate=transaction_data.usd_to_inr_rate,
            import_duty_percentage=transaction_data.import_duty_percentage,
            shipping_charges=transaction_data.shipping_charges,
            customs_charges=transaction_data.customs_charges
        )

        # Create transaction
        transaction = PreciousMetalsTransaction(
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            purchase_form=transaction_data.purchase_form,
            quantity_grams=cost_calculation['quantity_grams'],
            quantity_troy_oz=transaction_data.quantity_troy_oz,
            usd_per_troy_oz=transaction_data.usd_per_troy_oz,
            usd_to_inr_rate=transaction_data.usd_to_inr_rate,
            base_metal_cost=cost_calculation['cost_inr_before_duty'],
            import_duty=cost_calculation['import_duty'],
            shipping_charges=transaction_data.shipping_charges,
            customs_charges=transaction_data.customs_charges,
            total_cost=cost_calculation['total_cost_inr'],
            effective_rate_per_gram=cost_calculation['effective_rate_per_gram'],
            vendor_or_buyer=transaction_data.vendor_or_buyer,
            item_description=transaction_data.item_description,
            notes=transaction_data.notes
        )

        # Update account
        if transaction_data.transaction_type == TransactionType.BUY:
            account.total_quantity_grams += cost_calculation['quantity_grams']
            account.total_invested += cost_calculation['total_cost_inr']
        elif transaction_data.transaction_type == TransactionType.SELL:
            account.total_quantity_grams -= cost_calculation['quantity_grams']

        if account.total_quantity_grams > 0:
            account.average_purchase_price = account.total_invested / account.total_quantity_grams

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )


@router.post("/transactions/sgb", response_model=PreciousMetalsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_sgb_transaction(
    transaction_data: SGBTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create Sovereign Gold Bonds transaction
    """
    try:
        # Verify account
        account_query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == transaction_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate total cost
        total_cost = transaction_data.quantity_grams * transaction_data.sgb_issue_price

        # Create transaction
        transaction = PreciousMetalsTransaction(
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            purchase_form="SOVEREIGN_GOLD_BONDS",
            quantity_grams=transaction_data.quantity_grams,
            sgb_issue_price=transaction_data.sgb_issue_price,
            sgb_issue_date=transaction_data.sgb_issue_date,
            sgb_certificate_number=transaction_data.sgb_certificate_number,
            total_cost=total_cost,
            effective_rate_per_gram=transaction_data.sgb_issue_price,
            vendor_or_buyer=transaction_data.vendor_or_buyer,
            notes=transaction_data.notes
        )

        # Update account
        if transaction_data.transaction_type == TransactionType.BUY:
            account.total_quantity_grams += transaction_data.quantity_grams
            account.total_invested += total_cost
        elif transaction_data.transaction_type == TransactionType.SELL:
            account.total_quantity_grams -= transaction_data.quantity_grams

        if account.total_quantity_grams > 0:
            account.average_purchase_price = account.total_invested / account.total_quantity_grams

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )


@router.get("/transactions", response_model=List[PreciousMetalsTransactionResponse])
async def get_precious_metals_transactions(
    account_id: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get precious metals transactions with filters
    """
    try:
        query = select(PreciousMetalsTransaction)

        conditions = []
        if account_id:
            conditions.append(PreciousMetalsTransaction.account_id == account_id)
        if transaction_type:
            conditions.append(PreciousMetalsTransaction.transaction_type == transaction_type)
        if start_date:
            conditions.append(PreciousMetalsTransaction.transaction_date >= start_date)
        if end_date:
            conditions.append(PreciousMetalsTransaction.transaction_date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(PreciousMetalsTransaction.transaction_date.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        transactions = result.scalars().all()

        return transactions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )


# ==================== Rates ====================

@router.post("/rates", response_model=PreciousMetalsRateResponse, status_code=status.HTTP_201_CREATED)
async def create_precious_metals_rate(
    rate_data: PreciousMetalsRateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create/update precious metals rate for a specific date
    """
    try:
        rate = PreciousMetalsRate(**rate_data.model_dump())

        db.add(rate)
        await db.commit()
        await db.refresh(rate)

        return rate

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rate: {str(e)}"
        )


@router.get("/rates/latest", response_model=PreciousMetalsRateResponse)
async def get_latest_rate(
    metal_type: MetalType,
    market_type: MarketType,
    purity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest rate for a specific metal/market combination
    """
    try:
        query = select(PreciousMetalsRate).where(
            and_(
                PreciousMetalsRate.metal_type == metal_type,
                PreciousMetalsRate.market_type == market_type
            )
        )

        if purity:
            query = query.where(PreciousMetalsRate.purity == purity)

        query = query.order_by(PreciousMetalsRate.rate_date.desc()).limit(1)

        result = await db.execute(query)
        rate = result.scalar_one_or_none()

        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No rate found for specified criteria"
            )

        return rate

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rate: {str(e)}"
        )


# ==================== Portfolio & Analytics ====================

@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: AsyncSession = Depends(get_db)):
    """
    Get overall portfolio summary
    """
    try:
        # Count accounts
        count_query = select(func.count(PreciousMetalsAccount.id))
        count_result = await db.execute(count_query)
        total_accounts = count_result.scalar() or 0

        # Sum by metal type
        gold_query = select(
            func.sum(PreciousMetalsAccount.total_quantity_grams),
            func.sum(PreciousMetalsAccount.total_invested)
        ).where(PreciousMetalsAccount.metal_type == MetalType.GOLD)

        gold_result = await db.execute(gold_query)
        gold_data = gold_result.one()

        silver_query = select(
            func.sum(PreciousMetalsAccount.total_quantity_grams),
            func.sum(PreciousMetalsAccount.total_invested)
        ).where(PreciousMetalsAccount.metal_type == MetalType.SILVER)

        silver_result = await db.execute(silver_query)
        silver_data = silver_result.one()

        total_gold_grams = gold_data[0] or 0.0
        total_silver_grams = silver_data[0] or 0.0
        total_invested = (gold_data[1] or 0.0) + (silver_data[1] or 0.0)

        # For now, current value = invested (update when rates are available)
        current_market_value = total_invested
        total_profit_loss = 0.0
        profit_loss_percentage = 0.0

        return PortfolioSummary(
            total_accounts=total_accounts,
            total_gold_grams=total_gold_grams,
            total_silver_grams=total_silver_grams,
            total_invested=total_invested,
            current_market_value=current_market_value,
            total_profit_loss=total_profit_loss,
            profit_loss_percentage=profit_loss_percentage
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio summary: {str(e)}"
        )


@router.post("/portfolio/valuate")
async def valuate_portfolio(
    request: PortfolioValuationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Valuate portfolio at current market price
    """
    try:
        # Get account
        account_query = select(PreciousMetalsAccount).where(PreciousMetalsAccount.id == request.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Calculate portfolio value
        valuation = precious_metals_calculator.current_portfolio_value(
            total_quantity_grams=account.total_quantity_grams,
            average_purchase_price_per_gram=account.average_purchase_price,
            current_market_price_per_gram=request.current_market_price_per_gram
        )

        # Update account
        account.current_market_value = valuation['current_value']
        account.profit_loss = valuation['profit_loss']

        await db.commit()

        return valuation

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to valuate portfolio: {str(e)}"
        )


# ==================== Calculations ====================

@router.post("/calculate/indian-gold")
async def calculate_indian_gold_cost(request: IndianGoldCostRequest):
    """
    Calculate Indian gold cost with all charges
    """
    try:
        result = precious_metals_calculator.indian_gold_cost(
            quantity_grams=request.quantity_grams,
            gold_rate_per_10g=request.gold_rate_per_10g,
            purity=request.purity.value,
            making_charges_type=request.making_charges_type,
            making_charges_value=request.making_charges_value,
            include_gst=request.include_gst,
            include_hallmark=request.include_hallmark,
            num_items=request.num_items
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/calculate/indian-silver")
async def calculate_indian_silver_cost(request: IndianSilverCostRequest):
    """
    Calculate Indian silver cost with all charges
    """
    try:
        result = precious_metals_calculator.indian_silver_cost(
            quantity_grams=request.quantity_grams,
            silver_rate_per_kg=request.silver_rate_per_kg,
            making_charges_type=request.making_charges_type,
            making_charges_value=request.making_charges_value,
            include_gst=request.include_gst,
            include_hallmark=request.include_hallmark,
            num_items=request.num_items
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/calculate/international-bullion")
async def calculate_international_bullion_cost(request: InternationalBullionCostRequest):
    """
    Calculate international bullion cost
    """
    try:
        result = precious_metals_calculator.international_bullion_cost(
            quantity_troy_oz=request.quantity_troy_oz,
            usd_per_troy_oz=request.usd_per_troy_oz,
            usd_to_inr_rate=request.usd_to_inr_rate,
            import_duty_percentage=request.import_duty_percentage,
            shipping_charges=request.shipping_charges,
            customs_charges=request.customs_charges
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/calculate/sgb-returns")
async def calculate_sgb_returns(request: SGBReturnsRequest):
    """
    Calculate Sovereign Gold Bonds returns
    """
    try:
        result = roi_calculator.sgb_returns(
            issue_price=request.issue_price,
            quantity_grams=request.quantity_grams,
            purchase_date=request.purchase_date,
            annual_interest_rate=request.annual_interest_rate,
            current_gold_price=request.current_gold_price,
            redemption_date=request.redemption_date
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation failed: {str(e)}"
        )
