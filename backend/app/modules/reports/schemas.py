"""
Reports Module - Pydantic Schemas
Request and response models for reports API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# ==================== Enums ====================

class ReportType(str, Enum):
    """Report types"""
    SAVINGS_SUMMARY = "Savings Summary"
    PRECIOUS_METALS_PORTFOLIO = "Precious Metals Portfolio"
    EXPENSE_SUMMARY = "Expense Summary"
    BUDGET_ANALYSIS = "Budget Analysis"
    INCOME_EXPENSE = "Income vs Expense"
    PORTFOLIO_VALUATION = "Portfolio Valuation"
    TAX_SUMMARY = "Tax Summary"
    COMPLETE_FINANCIAL = "Complete Financial Report"


class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"


class TimePeriod(str, Enum):
    """Time period for reports"""
    CURRENT_MONTH = "current_month"
    LAST_MONTH = "last_month"
    CURRENT_QUARTER = "current_quarter"
    LAST_QUARTER = "last_quarter"
    CURRENT_YEAR = "current_year"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"
    ALL_TIME = "all_time"


# ==================== Report Request Schemas ====================

class ReportRequest(BaseModel):
    """Base report request"""
    report_type: ReportType
    report_format: ReportFormat = ReportFormat.JSON
    time_period: TimePeriod = TimePeriod.CURRENT_MONTH
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_charts: bool = False


class SavingsSummaryRequest(BaseModel):
    """Savings summary report request"""
    time_period: TimePeriod = TimePeriod.ALL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    account_types: Optional[List[str]] = None
    include_matured: bool = True
    include_closed: bool = False


class PreciousMetalsSummaryRequest(BaseModel):
    """Precious metals portfolio report request"""
    metal_types: Optional[List[str]] = None  # Gold, Silver, etc.
    market_types: Optional[List[str]] = None  # Indian, International
    include_transactions: bool = True
    current_market_prices: Optional[Dict[str, float]] = None


class ExpenseSummaryRequest(BaseModel):
    """Expense summary report request"""
    time_period: TimePeriod = TimePeriod.CURRENT_MONTH
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    categories: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    group_by: str = "category"  # category, payment_method, month


class BudgetAnalysisRequest(BaseModel):
    """Budget analysis report request"""
    time_period: TimePeriod = TimePeriod.CURRENT_MONTH
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    categories: Optional[List[str]] = None
    show_exceeded_only: bool = False


class TaxSummaryRequest(BaseModel):
    """Tax summary report request"""
    financial_year: str  # e.g., "2025-26"
    include_tds: bool = True
    include_capital_gains: bool = True
    include_interest_income: bool = True


class CompleteFinancialRequest(BaseModel):
    """Complete financial report request"""
    time_period: TimePeriod = TimePeriod.CURRENT_YEAR
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_savings: bool = True
    include_precious_metals: bool = True
    include_expenses: bool = True
    include_tax_summary: bool = True


# ==================== Report Response Schemas ====================

class ReportMetadata(BaseModel):
    """Report metadata"""
    report_type: str
    generated_at: datetime
    time_period: str
    start_date: Optional[date]
    end_date: Optional[date]
    total_records: int


class SavingsSummaryReport(BaseModel):
    """Savings summary report response"""
    metadata: ReportMetadata
    total_accounts: int
    active_accounts: int
    matured_accounts: int
    closed_accounts: int
    total_invested: float
    current_value: float
    total_interest_earned: float
    roi_percentage: float
    accounts_by_type: List[Dict[str, Any]]
    upcoming_maturities: List[Dict[str, Any]]


class PreciousMetalsReport(BaseModel):
    """Precious metals portfolio report response"""
    metadata: ReportMetadata
    total_gold_grams: float
    total_silver_grams: float
    total_invested: float
    current_market_value: float
    profit_loss: float
    profit_loss_percentage: float
    holdings_by_metal: List[Dict[str, Any]]
    holdings_by_purity: List[Dict[str, Any]]
    transactions_summary: Optional[List[Dict[str, Any]]] = None


class ExpenseSummaryReport(BaseModel):
    """Expense summary report response"""
    metadata: ReportMetadata
    total_expenses: float
    transaction_count: int
    average_expense: float
    by_category: List[Dict[str, Any]]
    by_payment_method: List[Dict[str, Any]]
    by_month: Optional[List[Dict[str, Any]]] = None
    top_expenses: List[Dict[str, Any]]


class BudgetAnalysisReport(BaseModel):
    """Budget analysis report response"""
    metadata: ReportMetadata
    total_budgeted: float
    total_spent: float
    total_remaining: float
    overall_utilization: float
    budgets_exceeded: int
    budgets_on_track: int
    budget_details: List[Dict[str, Any]]


class TaxSummaryReport(BaseModel):
    """Tax summary report response"""
    metadata: ReportMetadata
    financial_year: str
    total_interest_income: float
    tds_on_interest: float
    short_term_capital_gains: float
    long_term_capital_gains: float
    total_tax_liability: float
    sgb_tax_free_gains: float
    taxable_income_summary: Dict[str, Any]


class CompleteFinancialReport(BaseModel):
    """Complete financial report response"""
    metadata: ReportMetadata
    savings_summary: Optional[Dict[str, Any]] = None
    precious_metals_summary: Optional[Dict[str, Any]] = None
    expense_summary: Optional[Dict[str, Any]] = None
    tax_summary: Optional[Dict[str, Any]] = None
    net_worth: float
    total_assets: float
    total_liabilities: float
    financial_health_score: float


# ==================== Excel Export Schemas ====================

class ExcelExportRequest(BaseModel):
    """Excel export request"""
    export_type: str  # savings, precious_metals, expenses, complete
    time_period: TimePeriod = TimePeriod.ALL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_summary: bool = True
    include_details: bool = True
    include_charts: bool = True
    file_name: Optional[str] = None


class ExcelExportResponse(BaseModel):
    """Excel export response"""
    file_name: str
    file_size: int
    download_url: str
    sheets_included: List[str]
    generated_at: datetime
