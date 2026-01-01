"""
ROI Calculator - Complete Implementation
All investment calculation formulas for savings accounts
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any
import math


class ROICalculator:
    """
    Return on Investment Calculator

    Implements all calculation formulas for:
    - Simple Interest
    - Compound Interest
    - Recurring Deposits
    - PPF (Public Provident Fund)
    - NSC (National Savings Certificate)
    - SGB (Sovereign Gold Bonds)
    - Mutual Fund SIP
    - Fixed Deposit with premature withdrawal
    """

    @staticmethod
    def _to_decimal(value: float) -> Decimal:
        """Convert float to Decimal for precision"""
        return Decimal(str(value))

    @staticmethod
    def _round_currency(value: Decimal) -> Decimal:
        """Round to 2 decimal places (currency)"""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def simple_interest(
        principal: float,
        rate: float,
        time_years: float
    ) -> Dict[str, float]:
        """
        Calculate Simple Interest

        Formula: SI = (P × R × T) / 100
        Maturity = P + SI

        Args:
            principal: Principal amount
            rate: Annual interest rate (%)
            time_years: Time period in years

        Returns:
            {
                'principal': float,
                'interest_rate': float,
                'time_years': float,
                'simple_interest': float,
                'maturity_amount': float,
                'roi_percentage': float
            }
        """
        P = ROICalculator._to_decimal(principal)
        R = ROICalculator._to_decimal(rate)
        T = ROICalculator._to_decimal(time_years)

        # SI = (P × R × T) / 100
        SI = (P * R * T) / Decimal('100')
        SI = ROICalculator._round_currency(SI)

        maturity = P + SI
        maturity = ROICalculator._round_currency(maturity)

        # ROI% = (Interest / Principal) × 100
        roi_percentage = (SI / P) * Decimal('100')
        roi_percentage = roi_percentage.quantize(Decimal('0.01'))

        return {
            'principal': float(P),
            'interest_rate': float(R),
            'time_years': float(T),
            'simple_interest': float(SI),
            'maturity_amount': float(maturity),
            'roi_percentage': float(roi_percentage)
        }

    @staticmethod
    def compound_interest(
        principal: float,
        rate: float,
        time_years: float,
        compounding_frequency: int = 1  # 1=yearly, 2=half-yearly, 4=quarterly, 12=monthly
    ) -> Dict[str, float]:
        """
        Calculate Compound Interest

        Formula: A = P(1 + r/n)^(nt)
        CI = A - P

        Args:
            principal: Principal amount
            rate: Annual interest rate (%)
            time_years: Time period in years
            compounding_frequency: Compounds per year (1=yearly, 4=quarterly, 12=monthly)

        Returns:
            {
                'principal': float,
                'interest_rate': float,
                'time_years': float,
                'compounding_frequency': int,
                'compound_interest': float,
                'maturity_amount': float,
                'roi_percentage': float,
                'annualized_return': float
            }
        """
        P = float(principal)
        r = float(rate) / 100  # Convert to decimal
        t = float(time_years)
        n = int(compounding_frequency)

        # A = P(1 + r/n)^(nt)
        amount = P * math.pow((1 + r/n), n*t)

        CI = amount - P

        # Round
        amount = round(amount, 2)
        CI = round(CI, 2)

        # ROI%
        roi_percentage = (CI / P) * 100
        roi_percentage = round(roi_percentage, 2)

        # Annualized return
        annualized_return = round(rate, 2)  # For compound interest, annualized ~ rate

        return {
            'principal': P,
            'interest_rate': rate,
            'time_years': t,
            'compounding_frequency': n,
            'compound_interest': CI,
            'maturity_amount': amount,
            'roi_percentage': roi_percentage,
            'annualized_return': annualized_return
        }

    @staticmethod
    def recurring_deposit(
        monthly_installment: float,
        rate: float,
        tenure_months: int
    ) -> Dict[str, float]:
        """
        Calculate Recurring Deposit Maturity

        Formula: M = P × n × (n+1) × (r/2400)
        where M = Maturity amount, P = Monthly installment,
        n = tenure in months, r = annual interest rate

        Args:
            monthly_installment: Monthly deposit amount
            rate: Annual interest rate (%)
            tenure_months: Tenure in months

        Returns:
            {
                'monthly_installment': float,
                'tenure_months': int,
                'interest_rate': float,
                'total_invested': float,
                'interest_earned': float,
                'maturity_amount': float,
                'roi_percentage': float
            }
        """
        P = float(monthly_installment)
        n = int(tenure_months)
        r = float(rate)

        # Total invested
        total_invested = P * n

        # Interest calculation: M = P × n(n+1)/2 × (r/1200)
        # This is simplified RD formula
        interest_earned = P * (n * (n + 1) / 2) * (r / (12 * 100))

        maturity_amount = total_invested + interest_earned

        # Round
        interest_earned = round(interest_earned, 2)
        maturity_amount = round(maturity_amount, 2)

        # ROI%
        roi_percentage = (interest_earned / total_invested) * 100
        roi_percentage = round(roi_percentage, 2)

        return {
            'monthly_installment': P,
            'tenure_months': n,
            'interest_rate': r,
            'total_invested': total_invested,
            'interest_earned': interest_earned,
            'maturity_amount': maturity_amount,
            'roi_percentage': roi_percentage
        }

    @staticmethod
    def ppf_maturity(
        annual_deposit: float,
        rate: float = 7.1,  # Current PPF rate (as of 2025)
        years: int = 15
    ) -> Dict[str, float]:
        """
        Calculate PPF (Public Provident Fund) Maturity

        PPF has 15-year lock-in, compounded annually

        Args:
            annual_deposit: Annual deposit (max ₹1.5 lakh)
            rate: Interest rate (default 7.1%)
            years: Tenure (default 15 years, can extend in blocks of 5)

        Returns:
            {
                'annual_deposit': float,
                'tenure_years': int,
                'interest_rate': float,
                'total_invested': float,
                'interest_earned': float,
                'maturity_amount': float
            }
        """
        P = float(annual_deposit)
        r = float(rate) / 100
        n = int(years)

        # Total invested
        total_invested = P * n

        # PPF calculation (future value of annuity)
        # FV = P × [((1 + r)^n - 1) / r]
        if r > 0:
            maturity_amount = P * (((math.pow(1 + r, n) - 1) / r) * (1 + r))
        else:
            maturity_amount = total_invested

        interest_earned = maturity_amount - total_invested

        # Round
        maturity_amount = round(maturity_amount, 2)
        interest_earned = round(interest_earned, 2)

        return {
            'annual_deposit': P,
            'tenure_years': n,
            'interest_rate': rate,
            'total_invested': total_invested,
            'interest_earned': interest_earned,
            'maturity_amount': maturity_amount
        }

    @staticmethod
    def nsc_maturity(
        principal: float,
        rate: float = 7.7,  # Current NSC rate
        tenure_years: int = 5
    ) -> Dict[str, float]:
        """
        Calculate NSC (National Savings Certificate) Maturity

        5-year fixed, quarterly compounding

        Args:
            principal: Investment amount
            rate: Interest rate (default 7.7%)
            tenure_years: Tenure (default 5 years)

        Returns:
            {
                'principal': float,
                'interest_rate': float,
                'tenure_years': int,
                'interest_earned': float,
                'maturity_amount': float
            }
        """
        # NSC uses quarterly compounding
        result = ROICalculator.compound_interest(
            principal=principal,
            rate=rate,
            time_years=tenure_years,
            compounding_frequency=4  # Quarterly
        )

        return {
            'principal': principal,
            'interest_rate': rate,
            'tenure_years': tenure_years,
            'interest_earned': result['compound_interest'],
            'maturity_amount': result['maturity_amount']
        }

    @staticmethod
    def sgb_returns(
        issue_price: float,
        quantity_grams: float,
        purchase_date: datetime,
        annual_interest_rate: float = 2.5,
        current_gold_price: float = None,
        redemption_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Calculate SGB (Sovereign Gold Bonds) Returns

        SGB features:
        - 2.5% annual interest (paid semi-annually)
        - 8-year maturity, exit allowed after 5 years
        - Interest taxable, capital gains tax-free if held till maturity

        Args:
            issue_price: Issue price per gram (₹)
            quantity_grams: Quantity in grams
            purchase_date: Purchase date
            annual_interest_rate: Interest rate (default 2.5%)
            current_gold_price: Current gold price per gram (for valuation)
            redemption_date: Redemption date (default: today)

        Returns:
            {
                'investment': float,
                'quantity_grams': float,
                'years_held': float,
                'interest_earned': float,
                'capital_appreciation': float,
                'total_return': float,
                'current_value': float
            }
        """
        investment = issue_price * quantity_grams

        if redemption_date is None:
            redemption_date = datetime.now()

        # Calculate years held
        years_held = (redemption_date - purchase_date).days / 365.25

        # Interest earned (2.5% per annum on issue price)
        interest_earned = investment * (annual_interest_rate / 100) * years_held

        # Capital appreciation
        if current_gold_price:
            current_value = current_gold_price * quantity_grams
            capital_appreciation = current_value - investment
        else:
            current_value = investment
            capital_appreciation = 0

        total_return = interest_earned + capital_appreciation

        # Round
        investment = round(investment, 2)
        interest_earned = round(interest_earned, 2)
        capital_appreciation = round(capital_appreciation, 2)
        total_return = round(total_return, 2)
        current_value = round(current_value, 2)

        return {
            'investment': investment,
            'quantity_grams': quantity_grams,
            'years_held': round(years_held, 2),
            'interest_earned': interest_earned,
            'capital_appreciation': capital_appreciation,
            'total_return': total_return,
            'current_value': current_value
        }

    @staticmethod
    def mutual_fund_sip(
        monthly_sip: float,
        expected_return_rate: float,
        tenure_months: int,
        step_up_percentage: float = 0
    ) -> Dict[str, float]:
        """
        Calculate Mutual Fund SIP Returns

        Args:
            monthly_sip: Monthly SIP amount
            expected_return_rate: Expected annual return (%)
            tenure_months: Tenure in months
            step_up_percentage: Annual step-up % (default: 0)

        Returns:
            {
                'monthly_sip': float,
                'tenure_months': int,
                'expected_return_rate': float,
                'total_invested': float,
                'expected_maturity': float,
                'expected_returns': float
            }
        """
        P = float(monthly_sip)
        r = float(expected_return_rate) / 100 / 12  # Monthly rate
        n = int(tenure_months)
        step_up = float(step_up_percentage) / 100

        total_invested = 0
        maturity_amount = 0
        current_sip = P

        for month in range(1, n + 1):
            # Annual step-up
            if month > 1 and (month - 1) % 12 == 0 and step_up > 0:
                current_sip = current_sip * (1 + step_up)

            total_invested += current_sip

            # Future value of this installment
            remaining_months = n - month + 1
            fv = current_sip * math.pow(1 + r, remaining_months - 1)
            maturity_amount += fv

        expected_returns = maturity_amount - total_invested

        # Round
        total_invested = round(total_invested, 2)
        maturity_amount = round(maturity_amount, 2)
        expected_returns = round(expected_returns, 2)

        return {
            'monthly_sip': P,
            'tenure_months': n,
            'expected_return_rate': expected_return_rate,
            'total_invested': total_invested,
            'expected_maturity': maturity_amount,
            'expected_returns': expected_returns
        }

    @staticmethod
    def fd_with_premature_withdrawal(
        principal: float,
        rate: float,
        tenure_months: int,
        withdrawal_after_months: int,
        penalty_rate: float = 1.0  # Penalty % (typically 0.5-1%)
    ) -> Dict[str, float]:
        """
        Calculate FD amount with premature withdrawal

        Args:
            principal: Principal amount
            rate: Interest rate (%)
            tenure_months: Original tenure
            withdrawal_after_months: Actual months held
            penalty_rate: Penalty % on interest rate

        Returns:
            {
                'principal': float,
                'original_tenure_months': int,
                'withdrawn_after_months': int,
                'original_rate': float,
                'applicable_rate': float,
                'interest_earned': float,
                'withdrawal_amount': float,
                'penalty_amount': float
            }
        """
        # Calculate with reduced rate (original - penalty)
        applicable_rate = rate - penalty_rate

        # Calculate compound interest for actual duration
        result = ROICalculator.compound_interest(
            principal=principal,
            rate=applicable_rate,
            time_years=withdrawal_after_months / 12,
            compounding_frequency=4  # Quarterly
        )

        # Calculate what it would have been without penalty
        no_penalty_result = ROICalculator.compound_interest(
            principal=principal,
            rate=rate,
            time_years=withdrawal_after_months / 12,
            compounding_frequency=4
        )

        penalty_amount = no_penalty_result['compound_interest'] - result['compound_interest']

        return {
            'principal': principal,
            'original_tenure_months': tenure_months,
            'withdrawn_after_months': withdrawal_after_months,
            'original_rate': rate,
            'applicable_rate': applicable_rate,
            'interest_earned': result['compound_interest'],
            'withdrawal_amount': result['maturity_amount'],
            'penalty_amount': round(penalty_amount, 2)
        }

    @staticmethod
    def calculate_maturity_date(
        start_date: datetime,
        tenure_months: int
    ) -> datetime:
        """
        Calculate maturity date from start date and tenure

        Args:
            start_date: Start/deposit date
            tenure_months: Tenure in months

        Returns:
            Maturity date
        """
        return start_date + relativedelta(months=tenure_months)

    @staticmethod
    def annualized_return(
        total_return: float,
        investment: float,
        years: float
    ) -> float:
        """
        Calculate annualized return percentage

        Formula: Annualized Return = ((Final Value / Initial Value)^(1/years) - 1) × 100

        Args:
            total_return: Total return amount
            investment: Initial investment
            years: Time period in years

        Returns:
            Annualized return percentage
        """
        if investment <= 0 or years <= 0:
            return 0.0

        final_value = investment + total_return

        annualized = (math.pow(final_value / investment, 1 / years) - 1) * 100

        return round(annualized, 2)

    @staticmethod
    def effective_interest_rate(
        nominal_rate: float,
        compounding_frequency: int
    ) -> float:
        """
        Calculate effective annual interest rate

        Formula: Effective Rate = (1 + r/n)^n - 1

        Args:
            nominal_rate: Nominal annual rate (%)
            compounding_frequency: Compounds per year

        Returns:
            Effective annual rate (%)
        """
        r = nominal_rate / 100
        n = compounding_frequency

        effective = (math.pow(1 + r/n, n) - 1) * 100

        return round(effective, 2)


# Create global instance
roi_calculator = ROICalculator()
