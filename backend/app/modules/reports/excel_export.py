"""
Excel Export Service
Generate Excel files from report data
"""

import io
import xlsxwriter
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class ExcelExportService:
    """Service for exporting data to Excel"""

    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_savings_excel(self, report_data: Dict[str, Any]) -> str:
        """Generate Excel file for savings summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"savings_report_{timestamp}.xlsx"
        filepath = self.output_dir / filename

        workbook = xlsxwriter.Workbook(str(filepath))

        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00%'})
        date_format = workbook.add_format({'num_format': 'dd-mmm-yyyy'})

        # Summary Sheet
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.write('A1', 'Savings Summary Report', header_format)
        summary_sheet.write('A3', 'Total Accounts:', header_format)
        summary_sheet.write('B3', report_data.get('total_accounts', 0))
        summary_sheet.write('A4', 'Active Accounts:', header_format)
        summary_sheet.write('B4', report_data.get('active_accounts', 0))
        summary_sheet.write('A5', 'Total Invested:', header_format)
        summary_sheet.write('B5', report_data.get('total_invested', 0), currency_format)
        summary_sheet.write('A6', 'Current Value:', header_format)
        summary_sheet.write('B6', report_data.get('current_value', 0), currency_format)
        summary_sheet.write('A7', 'Interest Earned:', header_format)
        summary_sheet.write('B7', report_data.get('total_interest_earned', 0), currency_format)
        summary_sheet.write('A8', 'ROI:', header_format)
        summary_sheet.write('B8', report_data.get('roi_percentage', 0) / 100, percent_format)

        # By Account Type Sheet
        if 'accounts_by_type' in report_data:
            type_sheet = workbook.add_worksheet('By Account Type')
            type_sheet.write_row('A1', ['Account Type', 'Count', 'Invested', 'Current Value', 'Interest'], header_format)

            row = 1
            for acc_type in report_data['accounts_by_type']:
                type_sheet.write(row, 0, acc_type.get('account_type', ''))
                type_sheet.write(row, 1, acc_type.get('count', 0))
                type_sheet.write(row, 2, acc_type.get('total_invested', 0), currency_format)
                type_sheet.write(row, 3, acc_type.get('current_value', 0), currency_format)
                type_sheet.write(row, 4, acc_type.get('interest_earned', 0), currency_format)
                row += 1

        # Upcoming Maturities Sheet
        if 'upcoming_maturities' in report_data:
            maturity_sheet = workbook.add_worksheet('Upcoming Maturities')
            maturity_sheet.write_row('A1', ['Account', 'Maturity Date', 'Expected Amount', 'Days Remaining'], header_format)

            row = 1
            for maturity in report_data['upcoming_maturities']:
                maturity_sheet.write(row, 0, maturity.get('account_name', ''))
                maturity_sheet.write(row, 1, maturity.get('maturity_date', ''))
                maturity_sheet.write(row, 2, maturity.get('expected_amount', 0), currency_format)
                maturity_sheet.write(row, 3, maturity.get('days_remaining', 0))
                row += 1

        workbook.close()
        return filename

    def generate_precious_metals_excel(self, report_data: Dict[str, Any]) -> str:
        """Generate Excel file for precious metals portfolio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"precious_metals_report_{timestamp}.xlsx"
        filepath = self.output_dir / filename

        workbook = xlsxwriter.Workbook(str(filepath))

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFD700',
            'font_color': 'black',
            'border': 1
        })

        currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
        weight_format = workbook.add_format({'num_format': '#,##0.000'})
        percent_format = workbook.add_format({'num_format': '0.00%'})

        # Summary Sheet
        summary_sheet = workbook.add_worksheet('Portfolio Summary')
        summary_sheet.write('A1', 'Precious Metals Portfolio Report', header_format)
        summary_sheet.write('A3', 'Total Gold (grams):', header_format)
        summary_sheet.write('B3', report_data.get('total_gold_grams', 0), weight_format)
        summary_sheet.write('A4', 'Total Silver (grams):', header_format)
        summary_sheet.write('B4', report_data.get('total_silver_grams', 0), weight_format)
        summary_sheet.write('A5', 'Total Invested:', header_format)
        summary_sheet.write('B5', report_data.get('total_invested', 0), currency_format)
        summary_sheet.write('A6', 'Current Value:', header_format)
        summary_sheet.write('B6', report_data.get('current_market_value', 0), currency_format)
        summary_sheet.write('A7', 'Profit/Loss:', header_format)
        summary_sheet.write('B7', report_data.get('profit_loss', 0), currency_format)
        summary_sheet.write('A8', 'P/L %:', header_format)
        summary_sheet.write('B8', report_data.get('profit_loss_percentage', 0) / 100, percent_format)

        # By Metal Type Sheet
        if 'holdings_by_metal' in report_data:
            metal_sheet = workbook.add_worksheet('By Metal Type')
            metal_sheet.write_row('A1', ['Metal', 'Quantity (g)', 'Invested', 'Current Value', 'P/L'], header_format)

            row = 1
            for holding in report_data['holdings_by_metal']:
                metal_sheet.write(row, 0, holding.get('metal_type', ''))
                metal_sheet.write(row, 1, holding.get('total_quantity_grams', 0), weight_format)
                metal_sheet.write(row, 2, holding.get('total_invested', 0), currency_format)
                metal_sheet.write(row, 3, holding.get('current_value', 0), currency_format)
                metal_sheet.write(row, 4, holding.get('profit_loss', 0), currency_format)
                row += 1

        workbook.close()
        return filename

    def generate_expense_excel(self, report_data: Dict[str, Any]) -> str:
        """Generate Excel file for expense summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expense_report_{timestamp}.xlsx"
        filepath = self.output_dir / filename

        workbook = xlsxwriter.Workbook(str(filepath))

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FF6B6B',
            'font_color': 'white',
            'border': 1
        })

        currency_format = workbook.add_format({'num_format': '₹#,##0.00'})

        # Summary Sheet
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.write('A1', 'Expense Summary Report', header_format)
        summary_sheet.write('A3', 'Total Expenses:', header_format)
        summary_sheet.write('B3', report_data.get('total_expenses', 0), currency_format)
        summary_sheet.write('A4', 'Transaction Count:', header_format)
        summary_sheet.write('B4', report_data.get('transaction_count', 0))
        summary_sheet.write('A5', 'Average Expense:', header_format)
        summary_sheet.write('B5', report_data.get('average_expense', 0), currency_format)

        # By Category Sheet
        if 'by_category' in report_data:
            category_sheet = workbook.add_worksheet('By Category')
            category_sheet.write_row('A1', ['Category', 'Amount', 'Count'], header_format)

            row = 1
            for category in report_data['by_category']:
                category_sheet.write(row, 0, category.get('category', ''))
                category_sheet.write(row, 1, category.get('amount', 0), currency_format)
                category_sheet.write(row, 2, category.get('count', 0))
                row += 1

        # By Payment Method Sheet
        if 'by_payment_method' in report_data:
            payment_sheet = workbook.add_worksheet('By Payment Method')
            payment_sheet.write_row('A1', ['Payment Method', 'Amount', 'Count'], header_format)

            row = 1
            for payment in report_data['by_payment_method']:
                payment_sheet.write(row, 0, payment.get('payment_method', ''))
                payment_sheet.write(row, 1, payment.get('amount', 0), currency_format)
                payment_sheet.write(row, 2, payment.get('count', 0))
                row += 1

        # Top Expenses Sheet
        if 'top_expenses' in report_data:
            top_sheet = workbook.add_worksheet('Top Expenses')
            top_sheet.write_row('A1', ['Description', 'Amount', 'Date', 'Category'], header_format)

            row = 1
            for expense in report_data['top_expenses']:
                top_sheet.write(row, 0, expense.get('description', ''))
                top_sheet.write(row, 1, expense.get('amount', 0), currency_format)
                top_sheet.write(row, 2, expense.get('date', ''))
                top_sheet.write(row, 3, expense.get('category', ''))
                row += 1

        workbook.close()
        return filename

    def generate_budget_analysis_excel(self, report_data: Dict[str, Any]) -> str:
        """Generate Excel file for budget analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"budget_analysis_{timestamp}.xlsx"
        filepath = self.output_dir / filename

        workbook = xlsxwriter.Workbook(str(filepath))

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4ECDC4',
            'font_color': 'white',
            'border': 1
        })

        currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00%'})

        exceeded_format = workbook.add_format({
            'bg_color': '#FFE5E5',
            'num_format': '₹#,##0.00'
        })

        # Summary Sheet
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.write('A1', 'Budget Analysis Report', header_format)
        summary_sheet.write('A3', 'Total Budgeted:', header_format)
        summary_sheet.write('B3', report_data.get('total_budgeted', 0), currency_format)
        summary_sheet.write('A4', 'Total Spent:', header_format)
        summary_sheet.write('B4', report_data.get('total_spent', 0), currency_format)
        summary_sheet.write('A5', 'Total Remaining:', header_format)
        summary_sheet.write('B5', report_data.get('total_remaining', 0), currency_format)
        summary_sheet.write('A6', 'Overall Utilization:', header_format)
        summary_sheet.write('B6', report_data.get('overall_utilization', 0) / 100, percent_format)
        summary_sheet.write('A7', 'Budgets Exceeded:', header_format)
        summary_sheet.write('B7', report_data.get('budgets_exceeded', 0))

        # Budget Details Sheet
        if 'budget_details' in report_data:
            details_sheet = workbook.add_worksheet('Budget Details')
            details_sheet.write_row('A1', ['Category', 'Budgeted', 'Spent', 'Remaining', 'Utilization %'], header_format)

            row = 1
            for budget in report_data['budget_details']:
                details_sheet.write(row, 0, budget.get('category', ''))
                details_sheet.write(row, 1, budget.get('budgeted', 0), currency_format)

                # Highlight exceeded budgets in red
                if budget.get('exceeded', False):
                    details_sheet.write(row, 2, budget.get('spent', 0), exceeded_format)
                else:
                    details_sheet.write(row, 2, budget.get('spent', 0), currency_format)

                details_sheet.write(row, 3, budget.get('remaining', 0), currency_format)
                details_sheet.write(row, 4, budget.get('utilization_percentage', 0) / 100, percent_format)
                row += 1

        workbook.close()
        return filename
