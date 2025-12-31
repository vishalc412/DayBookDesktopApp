"""
Reports Module - API Endpoints
REST API for report generation and Excel export
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import os

from app.core.database import get_db
from .service import ReportsService
from .excel_export import ExcelExportService
from .schemas import (
    ReportType, ReportFormat, TimePeriod,
    SavingsSummaryRequest, PreciousMetalsSummaryRequest,
    ExpenseSummaryRequest, BudgetAnalysisRequest,
    ExcelExportRequest, ExcelExportResponse
)


router = APIRouter(prefix="/reports", tags=["Reports"])


# ==================== Report Generation ====================

@router.post("/savings/summary")
async def generate_savings_summary(
    request: SavingsSummaryRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate savings summary report

    Returns summary statistics, breakdown by account type, and upcoming maturities
    """
    try:
        service = ReportsService(db)
        report = await service.generate_savings_summary(request)
        return report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/precious-metals/summary")
async def generate_precious_metals_summary(
    request: PreciousMetalsSummaryRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate precious metals portfolio report

    Returns portfolio value, holdings breakdown, and profit/loss analysis
    """
    try:
        service = ReportsService(db)
        report = await service.generate_precious_metals_summary(request)
        return report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/expenses/summary")
async def generate_expense_summary(
    request: ExpenseSummaryRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate expense summary report

    Returns total expenses, category breakdown, payment method analysis, and top expenses
    """
    try:
        service = ReportsService(db)
        report = await service.generate_expense_summary(request)
        return report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/budgets/analysis")
async def generate_budget_analysis(
    request: BudgetAnalysisRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate budget analysis report

    Returns budget utilization, exceeded budgets, and detailed breakdown
    """
    try:
        service = ReportsService(db)
        report = await service.generate_budget_analysis(request)
        return report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# ==================== Excel Export ====================

@router.post("/export/savings/excel")
async def export_savings_to_excel(
    request: SavingsSummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export savings report to Excel

    Generates a multi-sheet Excel file with summary, breakdown, and upcoming maturities
    """
    try:
        # Generate report data
        service = ReportsService(db)
        report_data = await service.generate_savings_summary(request)

        # Generate Excel file
        excel_service = ExcelExportService()
        filename = excel_service.generate_savings_excel(report_data)

        # Return file
        filepath = excel_service.output_dir / filename
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}"
        )


@router.post("/export/precious-metals/excel")
async def export_precious_metals_to_excel(
    request: PreciousMetalsSummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export precious metals portfolio to Excel

    Generates a multi-sheet Excel file with portfolio summary and holdings breakdown
    """
    try:
        # Generate report data
        service = ReportsService(db)
        report_data = await service.generate_precious_metals_summary(request)

        # Generate Excel file
        excel_service = ExcelExportService()
        filename = excel_service.generate_precious_metals_excel(report_data)

        # Return file
        filepath = excel_service.output_dir / filename
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}"
        )


@router.post("/export/expenses/excel")
async def export_expenses_to_excel(
    request: ExpenseSummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export expense summary to Excel

    Generates a multi-sheet Excel file with summary, category breakdown, and top expenses
    """
    try:
        # Generate report data
        service = ReportsService(db)
        report_data = await service.generate_expense_summary(request)

        # Generate Excel file
        excel_service = ExcelExportService()
        filename = excel_service.generate_expense_excel(report_data)

        # Return file
        filepath = excel_service.output_dir / filename
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}"
        )


@router.post("/export/budgets/excel")
async def export_budget_analysis_to_excel(
    request: BudgetAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export budget analysis to Excel

    Generates a multi-sheet Excel file with budget summary and detailed breakdown
    """
    try:
        # Generate report data
        service = ReportsService(db)
        report_data = await service.generate_budget_analysis(request)

        # Generate Excel file
        excel_service = ExcelExportService()
        filename = excel_service.generate_budget_analysis_excel(report_data)

        # Return file
        filepath = excel_service.output_dir / filename
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}"
        )


# ==================== Utility Endpoints ====================

@router.get("/available-periods")
async def get_available_periods():
    """
    Get list of available time periods for reports
    """
    return {
        "periods": [
            {"value": "current_month", "label": "Current Month"},
            {"value": "last_month", "label": "Last Month"},
            {"value": "current_quarter", "label": "Current Quarter"},
            {"value": "last_quarter", "label": "Last Quarter"},
            {"value": "current_year", "label": "Current Year"},
            {"value": "last_year", "label": "Last Year"},
            {"value": "custom", "label": "Custom Date Range"},
            {"value": "all_time", "label": "All Time"}
        ]
    }


@router.get("/export-formats")
async def get_export_formats():
    """
    Get list of available export formats
    """
    return {
        "formats": [
            {"value": "json", "label": "JSON", "extension": ".json"},
            {"value": "excel", "label": "Excel", "extension": ".xlsx"},
            {"value": "csv", "label": "CSV", "extension": ".csv"}
        ]
    }
