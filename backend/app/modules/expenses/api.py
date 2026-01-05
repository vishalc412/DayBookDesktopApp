"""
Expenses Module - API Endpoints
Complete REST API for expense tracking and budgeting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, extract
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from app.core.database import get_db
from .models import Expense, ExpenseBudget, ExpenseCategory_Custom, ExpenseCategory, PaymentMethod
from .schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseBulkCreate,
    ExpenseBudgetCreate,
    ExpenseBudgetUpdate,
    ExpenseBudgetResponse,
    ExpenseSummary,
    CategorySummary,
    MonthlySummary,
    PaymentMethodSummary,
    TopExpense,
    BudgetStatus,
    ExpenseReportRequest,
    MonthlyReportRequest,
    YearlyReportRequest,
    CustomCategoryCreate,
    CustomCategoryResponse
)


router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ==================== Expenses CRUD ====================

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new expense

    Automatically checks budget and updates budget tracking
    """
    try:
        expense = Expense(**expense_data.model_dump())

        # Check if this category has a budget
        budget_query = select(ExpenseBudget).where(
            and_(
                ExpenseBudget.category == expense.category,
                ExpenseBudget.is_active == True
            )
        )
        budget_result = await db.execute(budget_query)
        budget = budget_result.scalar_one_or_none()

        if budget:
            expense.is_budgeted = True
            # Check if budget exceeded
            total_spent = budget.spent_amount + expense.amount
            if total_spent > budget.budget_amount:
                expense.budget_exceeded = True

        db.add(expense)
        await db.commit()
        await db.refresh(expense)

        # Update budget if exists
        if budget:
            await _update_budget_spent(db, budget)

        return expense

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expense: {str(e)}"
        )


@router.post("/bulk", response_model=List[ExpenseResponse], status_code=status.HTTP_201_CREATED)
async def create_expenses_bulk(
    bulk_data: ExpenseBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple expenses at once
    """
    try:
        created_expenses = []

        for expense_data in bulk_data.expenses:
            expense = Expense(**expense_data.model_dump())
            db.add(expense)
            created_expenses.append(expense)

        await db.commit()

        # Refresh all
        for expense in created_expenses:
            await db.refresh(expense)

        return created_expenses

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expenses: {str(e)}"
        )


@router.get("", response_model=List[ExpenseResponse])
async def get_expenses(
    category: Optional[ExpenseCategory] = None,
    payment_method: Optional[PaymentMethod] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get expenses with comprehensive filters
    """
    try:
        query = select(Expense)

        conditions = []
        if category:
            conditions.append(Expense.category == category)
        if payment_method:
            conditions.append(Expense.payment_method == payment_method)
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        if end_date:
            conditions.append(Expense.expense_date <= end_date)
        if min_amount:
            conditions.append(Expense.amount >= min_amount)
        if max_amount:
            conditions.append(Expense.amount <= max_amount)
        if search:
            conditions.append(
                or_(
                    Expense.description.ilike(f"%{search}%"),
                    Expense.vendor.ilike(f"%{search}%"),
                    Expense.notes.ilike(f"%{search}%")
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Expense.expense_date.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        expenses = result.scalars().all()

        return expenses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch expenses: {str(e)}"
        )


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get single expense by ID
    """
    try:
        query = select(Expense).where(Expense.id == expense_id)
        result = await db.execute(query)
        expense = result.scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        return expense

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch expense: {str(e)}"
        )


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update expense
    """
    try:
        query = select(Expense).where(Expense.id == expense_id)
        result = await db.execute(query)
        expense = result.scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        await db.commit()
        await db.refresh(expense)

        return expense

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update expense: {str(e)}"
        )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete expense
    """
    try:
        query = select(Expense).where(Expense.id == expense_id)
        result = await db.execute(query)
        expense = result.scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        db.delete(expense)
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete expense: {str(e)}"
        )


# ==================== Budgets ====================

@router.post("/budgets", response_model=ExpenseBudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: ExpenseBudgetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create expense budget
    """
    try:
        budget = ExpenseBudget(**budget_data.model_dump())
        budget.remaining_amount = budget.budget_amount

        db.add(budget)
        await db.commit()
        await db.refresh(budget)

        # Calculate spent amount
        await _update_budget_spent(db, budget)

        return budget

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create budget: {str(e)}"
        )


@router.get("/budgets", response_model=List[ExpenseBudgetResponse])
async def get_budgets(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all budgets
    """
    try:
        query = select(ExpenseBudget)

        if is_active is not None:
            query = query.where(ExpenseBudget.is_active == is_active)

        query = query.order_by(ExpenseBudget.category)

        result = await db.execute(query)
        budgets = result.scalars().all()

        return budgets

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch budgets: {str(e)}"
        )


@router.put("/budgets/{budget_id}", response_model=ExpenseBudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: ExpenseBudgetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update budget
    """
    try:
        query = select(ExpenseBudget).where(ExpenseBudget.id == budget_id)
        result = await db.execute(query)
        budget = result.scalar_one_or_none()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )

        update_data = budget_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)

        await db.commit()
        await db.refresh(budget)

        # Recalculate spent
        await _update_budget_spent(db, budget)

        return budget

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update budget: {str(e)}"
        )


@router.get("/budgets/status", response_model=List[BudgetStatus])
async def get_budget_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Get budget status for all categories
    """
    try:
        query = select(ExpenseBudget).where(ExpenseBudget.is_active == True)
        result = await db.execute(query)
        budgets = result.scalars().all()

        budget_statuses = []

        for budget in budgets:
            # Calculate days remaining in period
            today = date.today()
            if budget.period_type == "monthly":
                days_in_month = (date(today.year, today.month + 1, 1) - timedelta(days=1)).day if today.month < 12 else 31
                days_remaining = days_in_month - today.day
            else:  # yearly
                days_remaining = (date(today.year, 12, 31) - today).days

            budget_statuses.append(BudgetStatus(
                category=budget.category.value,
                budget_amount=budget.budget_amount,
                spent_amount=budget.spent_amount,
                remaining_amount=budget.remaining_amount or 0,
                percentage_used=budget.percentage_used,
                is_exceeded=budget.is_exceeded,
                is_alert=budget.alert_triggered,  # Alert triggered status
                days_remaining=days_remaining
            ))

        return budget_statuses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch budget status: {str(e)}"
        )


# ==================== Analytics ====================

@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(db: AsyncSession = Depends(get_db)):
    """
    Get expense summary statistics
    """
    try:
        # Total expenses
        total_query = select(
            func.sum(Expense.amount),
            func.count(Expense.id),
            func.avg(Expense.amount)
        )
        total_result = await db.execute(total_query)
        total_data = total_result.one()

        total_expenses = total_data[0] or 0.0
        total_count = total_data[1] or 0
        average_expense = total_data[2] or 0.0

        # This month
        today = date.today()
        month_start = date(today.year, today.month, 1)

        month_query = select(
            func.sum(Expense.amount),
            func.count(Expense.id)
        ).where(Expense.expense_date >= month_start)

        month_result = await db.execute(month_query)
        month_data = month_result.one()

        this_month_expenses = month_data[0] or 0.0
        this_month_count = month_data[1] or 0

        # Top category
        top_category_query = select(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).limit(1)

        top_result = await db.execute(top_category_query)
        top_data = top_result.one_or_none()

        if top_data and top_data[0]:
            top_category = top_data[0].value if hasattr(top_data[0], 'value') else str(top_data[0])
            top_category_amount = top_data[1]
        else:
            top_category = "None"
            top_category_amount = 0.0

        return ExpenseSummary(
            total_expenses=total_expenses,
            total_count=total_count,
            transaction_count=total_count,  # Frontend compatibility
            this_month_expenses=this_month_expenses,
            this_month_count=this_month_count,
            average_expense=average_expense,
            top_category=top_category,
            top_category_amount=top_category_amount
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch summary: {str(e)}"
        )


@router.get("/by-category", response_model=List[CategorySummary])
async def get_expenses_by_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get expense breakdown by category
    """
    try:
        query = select(
            Expense.category,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count'),
            func.avg(Expense.amount).label('average')
        )

        conditions = []
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        if end_date:
            conditions.append(Expense.expense_date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.group_by(Expense.category).order_by(func.sum(Expense.amount).desc())

        result = await db.execute(query)
        categories = result.all()

        # Calculate total for percentage
        total_amount = sum(cat[1] for cat in categories)

        category_summaries = []
        for cat in categories:
            percentage = (cat[1] / total_amount * 100) if total_amount > 0 else 0
            # Handle enum conversion safely
            category_value = cat[0].value if hasattr(cat[0], 'value') else str(cat[0])
            category_summaries.append(CategorySummary(
                category=category_value,
                total_amount=cat[1],
                amount=cat[1],  # Frontend compatibility
                count=cat[2],
                percentage=round(percentage, 2),
                average=cat[3]
            ))

        return category_summaries

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category breakdown: {str(e)}"
        )


@router.get("/by-payment-method", response_model=List[PaymentMethodSummary])
async def get_expenses_by_payment_method(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get expense breakdown by payment method
    """
    try:
        query = select(
            Expense.payment_method,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        )

        conditions = []
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        if end_date:
            conditions.append(Expense.expense_date <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.group_by(Expense.payment_method).order_by(func.sum(Expense.amount).desc())

        result = await db.execute(query)
        methods = result.all()

        # Calculate total
        total_amount = sum(m[1] for m in methods)

        summaries = []
        for method in methods:
            percentage = (method[1] / total_amount * 100) if total_amount > 0 else 0
            summaries.append(PaymentMethodSummary(
                payment_method=method[0].value,
                total_amount=method[1],
                count=method[2],
                percentage=round(percentage, 2)
            ))

        return summaries

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment method breakdown: {str(e)}"
        )


@router.get("/monthly-trend", response_model=List[MonthlySummary])
async def get_monthly_trend(
    months: int = Query(12, ge=1, le=36),
    db: AsyncSession = Depends(get_db)
):
    """
    Get monthly expense trend
    """
    try:
        # Calculate date range
        today = date.today()
        start_date = today - relativedelta(months=months)

        # Query expenses
        query = select(Expense).where(Expense.expense_date >= start_date)
        result = await db.execute(query)
        expenses = result.scalars().all()

        # Group by month
        monthly_data = defaultdict(lambda: {'total': 0, 'count': 0, 'categories': defaultdict(float)})

        for expense in expenses:
            month_key = f"{expense.expense_date.year}-{expense.expense_date.month:02d}"
            monthly_data[month_key]['total'] += expense.amount
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['categories'][expense.category.value] += expense.amount

        # Convert to response format
        summaries = []
        for month_key, data in sorted(monthly_data.items()):
            year, month = map(int, month_key.split('-'))
            summaries.append(MonthlySummary(
                month=month_key,
                year=year,
                month_num=month,
                total_expenses=data['total'],
                count=data['count'],
                categories=dict(data['categories'])
            ))

        return summaries

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch monthly trend: {str(e)}"
        )


@router.get("/top-expenses", response_model=List[TopExpense])
async def get_top_expenses(
    limit: int = Query(10, ge=1, le=100),
    period: str = Query("month", pattern="^(week|month|year|all)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top expenses by amount
    """
    try:
        query = select(Expense)

        # Apply period filter
        today = date.today()
        if period == "week":
            start_date = today - timedelta(days=7)
            query = query.where(Expense.expense_date >= start_date)
        elif period == "month":
            start_date = date(today.year, today.month, 1)
            query = query.where(Expense.expense_date >= start_date)
        elif period == "year":
            start_date = date(today.year, 1, 1)
            query = query.where(Expense.expense_date >= start_date)

        query = query.order_by(Expense.amount.desc()).limit(limit)

        result = await db.execute(query)
        expenses = result.scalars().all()

        top_expenses = []
        for expense in expenses:
            top_expenses.append(TopExpense(
                id=expense.id,
                description=expense.description,
                amount=expense.amount,
                category=expense.category.value,
                expense_date=expense.expense_date,
                vendor=expense.vendor
            ))

        return top_expenses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top expenses: {str(e)}"
        )


# ==================== Helper Functions ====================

async def _update_budget_spent(db: AsyncSession, budget: ExpenseBudget):
    """
    Update budget spent amount and status
    """
    # Determine date range based on period
    if budget.period_type == "monthly":
        start_date = date(budget.period_year, budget.period_month, 1)
        if budget.period_month == 12:
            end_date = date(budget.period_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(budget.period_year, budget.period_month + 1, 1) - timedelta(days=1)
    else:  # yearly
        start_date = date(budget.period_year, 1, 1)
        end_date = date(budget.period_year, 12, 31)

    # Calculate spent
    spent_query = select(func.sum(Expense.amount)).where(
        and_(
            Expense.category == budget.category,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    )
    spent_result = await db.execute(spent_query)
    spent_amount = spent_result.scalar() or 0.0

    # Update budget
    budget.spent_amount = spent_amount
    budget.remaining_amount = budget.budget_amount - spent_amount
    budget.percentage_used = (spent_amount / budget.budget_amount * 100) if budget.budget_amount > 0 else 0
    budget.is_exceeded = spent_amount > budget.budget_amount

    # Check alert threshold
    if budget.percentage_used >= budget.alert_at_percentage and not budget.alert_triggered:
        budget.alert_triggered = True

    await db.commit()
