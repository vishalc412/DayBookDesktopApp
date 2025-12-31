"""
Reports Service
Business logic for report generation
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.modules.savings.models import SavingsAccount, SavingsEntry, AccountStatus
from app.modules.precious_metals.models import PreciousMetalsAccount, PreciousMetalsTransaction
from app.modules.expenses.models import Expense, ExpenseBudget
from .schemas import (
    TimePeriod, SavingsSummaryRequest, PreciousMetalsSummaryRequest,
    ExpenseSummaryRequest, BudgetAnalysisRequest, TaxSummaryRequest,
    ReportMetadata
)


class ReportsService:
    """Service for generating financial reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_date_range(time_period: TimePeriod, start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> tuple[date, date]:
        """Get start and end dates for a time period"""
        today = date.today()

        if time_period == TimePeriod.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("start_date and end_date required for CUSTOM period")
            return start_date, end_date

        elif time_period == TimePeriod.CURRENT_MONTH:
            start = today.replace(day=1)
            end = today

        elif time_period == TimePeriod.LAST_MONTH:
            first_of_month = today.replace(day=1)
            end = first_of_month - timedelta(days=1)
            start = end.replace(day=1)

        elif time_period == TimePeriod.CURRENT_QUARTER:
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            end = today

        elif time_period == TimePeriod.LAST_QUARTER:
            current_quarter = (today.month - 1) // 3
            last_quarter = current_quarter - 1 if current_quarter > 0 else 3
            year = today.year if current_quarter > 0 else today.year - 1
            start = date(year, last_quarter * 3 + 1, 1)
            end = (start + relativedelta(months=3)) - timedelta(days=1)

        elif time_period == TimePeriod.CURRENT_YEAR:
            start = today.replace(month=1, day=1)
            end = today

        elif time_period == TimePeriod.LAST_YEAR:
            start = date(today.year - 1, 1, 1)
            end = date(today.year - 1, 12, 31)

        elif time_period == TimePeriod.ALL_TIME:
            start = date(2000, 1, 1)  # Far past
            end = today

        else:
            start = today.replace(day=1)
            end = today

        return start, end

    async def generate_savings_summary(
        self, request: SavingsSummaryRequest
    ) -> Dict[str, Any]:
        """Generate savings summary report"""
        start_date, end_date = self.get_date_range(
            request.time_period, request.start_date, request.end_date
        )

        # Build query
        query = select(SavingsAccount)
        conditions = []

        if request.account_types:
            conditions.append(SavingsAccount.account_type.in_(request.account_types))

        if not request.include_matured:
            conditions.append(SavingsAccount.status != AccountStatus.MATURED)

        if not request.include_closed:
            conditions.append(SavingsAccount.status != AccountStatus.CLOSED)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        accounts = result.scalars().all()

        # Calculate summary
        total_invested = sum(acc.initial_amount for acc in accounts)
        current_value = sum(acc.current_balance for acc in accounts)
        total_interest = sum(acc.total_interest_earned for acc in accounts)

        roi_percentage = ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0

        # Group by account type
        accounts_by_type = {}
        for acc in accounts:
            type_key = acc.account_type.value
            if type_key not in accounts_by_type:
                accounts_by_type[type_key] = {
                    'account_type': type_key,
                    'count': 0,
                    'total_invested': 0,
                    'current_value': 0,
                    'interest_earned': 0
                }
            accounts_by_type[type_key]['count'] += 1
            accounts_by_type[type_key]['total_invested'] += acc.initial_amount
            accounts_by_type[type_key]['current_value'] += acc.current_balance
            accounts_by_type[type_key]['interest_earned'] += acc.total_interest_earned

        # Upcoming maturities (next 60 days)
        upcoming_date = end_date + timedelta(days=60)
        upcoming_query = select(SavingsAccount).where(
            and_(
                SavingsAccount.maturity_date.isnot(None),
                SavingsAccount.maturity_date >= end_date,
                SavingsAccount.maturity_date <= upcoming_date,
                SavingsAccount.status == AccountStatus.ACTIVE
            )
        )
        upcoming_result = await self.db.execute(upcoming_query)
        upcoming = upcoming_result.scalars().all()

        upcoming_maturities = [
            {
                'account_name': acc.account_name,
                'maturity_date': acc.maturity_date.isoformat(),
                'expected_amount': acc.expected_maturity_amount,
                'days_remaining': (acc.maturity_date - end_date).days
            }
            for acc in upcoming
        ]

        return {
            'metadata': {
                'report_type': 'Savings Summary',
                'generated_at': datetime.now().isoformat(),
                'time_period': request.time_period.value,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_records': len(accounts)
            },
            'total_accounts': len(accounts),
            'active_accounts': sum(1 for acc in accounts if acc.status == AccountStatus.ACTIVE),
            'matured_accounts': sum(1 for acc in accounts if acc.status == AccountStatus.MATURED),
            'closed_accounts': sum(1 for acc in accounts if acc.status == AccountStatus.CLOSED),
            'total_invested': round(total_invested, 2),
            'current_value': round(current_value, 2),
            'total_interest_earned': round(total_interest, 2),
            'roi_percentage': round(roi_percentage, 2),
            'accounts_by_type': list(accounts_by_type.values()),
            'upcoming_maturities': upcoming_maturities
        }

    async def generate_precious_metals_summary(
        self, request: PreciousMetalsSummaryRequest
    ) -> Dict[str, Any]:
        """Generate precious metals portfolio report"""
        # Build query
        query = select(PreciousMetalsAccount)
        conditions = [PreciousMetalsAccount.is_active == True]

        if request.metal_types:
            conditions.append(PreciousMetalsAccount.metal_type.in_(request.metal_types))

        if request.market_types:
            conditions.append(PreciousMetalsAccount.market_type.in_(request.market_types))

        query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        accounts = result.scalars().all()

        # Calculate summary
        total_gold = sum(acc.total_quantity_grams for acc in accounts if acc.metal_type.value == "GOLD")
        total_silver = sum(acc.total_quantity_grams for acc in accounts if acc.metal_type.value == "SILVER")
        total_invested = sum(acc.total_invested for acc in accounts)
        current_value = sum(acc.current_market_value for acc in accounts)
        profit_loss = current_value - total_invested
        profit_loss_pct = (profit_loss / total_invested * 100) if total_invested > 0 else 0

        # Group by metal type
        holdings_by_metal = {}
        for acc in accounts:
            metal = acc.metal_type.value
            if metal not in holdings_by_metal:
                holdings_by_metal[metal] = {
                    'metal_type': metal,
                    'total_quantity_grams': 0,
                    'total_invested': 0,
                    'current_value': 0,
                    'profit_loss': 0
                }
            holdings_by_metal[metal]['total_quantity_grams'] += acc.total_quantity_grams
            holdings_by_metal[metal]['total_invested'] += acc.total_invested
            holdings_by_metal[metal]['current_value'] += acc.current_market_value
            holdings_by_metal[metal]['profit_loss'] += acc.profit_loss

        return {
            'metadata': {
                'report_type': 'Precious Metals Portfolio',
                'generated_at': datetime.now().isoformat(),
                'time_period': 'all_time',
                'start_date': None,
                'end_date': None,
                'total_records': len(accounts)
            },
            'total_gold_grams': round(total_gold, 3),
            'total_silver_grams': round(total_silver, 3),
            'total_invested': round(total_invested, 2),
            'current_market_value': round(current_value, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_percentage': round(profit_loss_pct, 2),
            'holdings_by_metal': list(holdings_by_metal.values()),
            'holdings_by_purity': []  # TODO: Implement
        }

    async def generate_expense_summary(
        self, request: ExpenseSummaryRequest
    ) -> Dict[str, Any]:
        """Generate expense summary report"""
        start_date, end_date = self.get_date_range(
            request.time_period, request.start_date, request.end_date
        )

        # Build query
        query = select(Expense)
        conditions = [
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ]

        if request.categories:
            conditions.append(Expense.category.in_(request.categories))

        if request.payment_methods:
            conditions.append(Expense.payment_method.in_(request.payment_methods))

        query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        expenses = result.scalars().all()

        total_expenses = sum(exp.amount for exp in expenses)
        transaction_count = len(expenses)
        average_expense = total_expenses / transaction_count if transaction_count > 0 else 0

        # Group by category
        by_category = {}
        for exp in expenses:
            cat = exp.category.value
            if cat not in by_category:
                by_category[cat] = {'category': cat, 'amount': 0, 'count': 0}
            by_category[cat]['amount'] += exp.amount
            by_category[cat]['count'] += 1

        # Group by payment method
        by_payment = {}
        for exp in expenses:
            pm = exp.payment_method.value
            if pm not in by_payment:
                by_payment[pm] = {'payment_method': pm, 'amount': 0, 'count': 0}
            by_payment[pm]['amount'] += exp.amount
            by_payment[pm]['count'] += 1

        # Top expenses
        sorted_expenses = sorted(expenses, key=lambda x: x.amount, reverse=True)
        top_expenses = [
            {
                'description': exp.description or exp.category.value,
                'amount': exp.amount,
                'date': exp.expense_date.isoformat(),
                'category': exp.category.value
            }
            for exp in sorted_expenses[:10]
        ]

        return {
            'metadata': {
                'report_type': 'Expense Summary',
                'generated_at': datetime.now().isoformat(),
                'time_period': request.time_period.value,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_records': transaction_count
            },
            'total_expenses': round(total_expenses, 2),
            'transaction_count': transaction_count,
            'average_expense': round(average_expense, 2),
            'by_category': list(by_category.values()),
            'by_payment_method': list(by_payment.values()),
            'top_expenses': top_expenses
        }

    async def generate_budget_analysis(
        self, request: BudgetAnalysisRequest
    ) -> Dict[str, Any]:
        """Generate budget analysis report"""
        start_date, end_date = self.get_date_range(
            request.time_period, request.start_date, request.end_date
        )

        # Get budgets
        query = select(ExpenseBudget)
        if request.categories:
            query = query.where(ExpenseBudget.category.in_(request.categories))

        result = await self.db.execute(query)
        budgets = result.scalars().all()

        # For each budget, calculate spent amount from expenses
        budget_details = []
        total_budgeted = 0
        total_spent = 0
        budgets_exceeded = 0
        budgets_on_track = 0

        for budget in budgets:
            # Get expenses for this category in period
            exp_query = select(func.sum(Expense.amount)).where(
                and_(
                    Expense.category == budget.category,
                    Expense.expense_date >= start_date,
                    Expense.expense_date <= end_date
                )
            )
            exp_result = await self.db.execute(exp_query)
            spent = exp_result.scalar() or 0

            remaining = budget.budget_amount - spent
            utilization = (spent / budget.budget_amount * 100) if budget.budget_amount > 0 else 0
            exceeded = spent > budget.budget_amount

            if exceeded:
                budgets_exceeded += 1
            else:
                budgets_on_track += 1

            total_budgeted += budget.budget_amount
            total_spent += spent

            if request.show_exceeded_only and not exceeded:
                continue

            budget_details.append({
                'category': budget.category.value,
                'budgeted': budget.budget_amount,
                'spent': spent,
                'remaining': remaining,
                'utilization_percentage': round(utilization, 2),
                'exceeded': exceeded
            })

        total_remaining = total_budgeted - total_spent
        overall_utilization = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0

        return {
            'metadata': {
                'report_type': 'Budget Analysis',
                'generated_at': datetime.now().isoformat(),
                'time_period': request.time_period.value,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_records': len(budget_details)
            },
            'total_budgeted': round(total_budgeted, 2),
            'total_spent': round(total_spent, 2),
            'total_remaining': round(total_remaining, 2),
            'overall_utilization': round(overall_utilization, 2),
            'budgets_exceeded': budgets_exceeded,
            'budgets_on_track': budgets_on_track,
            'budget_details': budget_details
        }
