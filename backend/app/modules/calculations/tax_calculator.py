"""
Tax Calculator
Capital gains and interest tax calculations
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class TaxCalculator:
    """
    Tax Calculations for Indian Context

    Implements:
    - Short-term capital gains (STCG)
    - Long-term capital gains (LTCG)
    - TDS on interest
    - SGB tax treatment
    """

    # Tax rates (as of 2025)
    LTCG_EQUITY_RATE = 10.0  # 10% above ₹1 lakh
    LTCG_DEBT_RATE = 20.0  # 20% with indexation
    TDS_RATE = 10.0  # 10% TDS on interest
    TDS_THRESHOLD_GENERAL = 40000  # ₹40,000 for general
    TDS_THRESHOLD_SENIOR = 50000  # ₹50,000 for senior citizens

    @staticmethod
    def calculate_stcg(
        sale_price: float,
        purchase_price: float,
        holding_period_days: int,
        asset_type: str = "equity"
    ) -> Dict[str, float]:
        """
        Calculate Short-Term Capital Gains

        STCG periods:
        - Equity: < 12 months
        - Debt/Gold: < 36 months

        Args:
            sale_price: Sale price
            purchase_price: Purchase price
            holding_period_days: Days held
            asset_type: "equity" or "debt"

        Returns:
            {
                'capital_gain': float,
                'is_short_term': bool,
                'holding_period_days': int,
                'tax_treatment': str
            }
        """
        capital_gain = sale_price - purchase_price

        # Determine if short-term
        threshold_days = 365 if asset_type == "equity" else 1095  # 3 years for debt
        is_short_term = holding_period_days < threshold_days

        return {
            'capital_gain': round(capital_gain, 2),
            'is_short_term': is_short_term,
            'holding_period_days': holding_period_days,
            'tax_treatment': 'Taxed as per income slab' if is_short_term else 'LTCG rates apply'
        }

    @staticmethod
    def calculate_ltcg(
        sale_price: float,
        purchase_price: float,
        holding_period_days: int,
        asset_type: str = "equity",
        indexation_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate Long-Term Capital Gains

        Args:
            sale_price: Sale price
            purchase_price: Purchase price
            holding_period_days: Days held
            asset_type: "equity" or "debt"
            indexation_factor: CII indexation (for debt)

        Returns:
            {
                'capital_gain': float,
                'indexed_cost': float,
                'taxable_gain': float,
                'tax_rate': float,
                'tax_amount': float
            }
        """
        # For equity: no indexation
        # For debt: with indexation
        indexed_cost = purchase_price * indexation_factor if asset_type == "debt" else purchase_price

        capital_gain = sale_price - purchase_price
        taxable_gain = sale_price - indexed_cost

        if asset_type == "equity":
            # 10% above ₹1 lakh exemption
            exempt_amount = 100000
            taxable_amount = max(0, taxable_gain - exempt_amount)
            tax_rate = TaxCalculator.LTCG_EQUITY_RATE
        else:
            # 20% with indexation
            taxable_amount = taxable_gain
            tax_rate = TaxCalculator.LTCG_DEBT_RATE

        tax_amount = taxable_amount * (tax_rate / 100)

        return {
            'capital_gain': round(capital_gain, 2),
            'indexed_cost': round(indexed_cost, 2),
            'taxable_gain': round(taxable_gain, 2),
            'tax_rate': tax_rate,
            'tax_amount': round(tax_amount, 2)
        }

    @staticmethod
    def tds_on_interest(
        interest_amount: float,
        is_senior_citizen: bool = False
    ) -> Dict[str, float]:
        """
        Calculate TDS on interest income

        Args:
            interest_amount: Annual interest
            is_senior_citizen: Senior citizen status

        Returns:
            {
                'interest_amount': float,
                'threshold': float,
                'tds_applicable': bool,
                'tds_amount': float
            }
        """
        threshold = TaxCalculator.TDS_THRESHOLD_SENIOR if is_senior_citizen else TaxCalculator.TDS_THRESHOLD_GENERAL

        tds_applicable = interest_amount > threshold

        tds_amount = 0
        if tds_applicable:
            tds_amount = interest_amount * (TaxCalculator.TDS_RATE / 100)

        return {
            'interest_amount': round(interest_amount, 2),
            'threshold': threshold,
            'tds_applicable': tds_applicable,
            'tds_amount': round(tds_amount, 2)
        }

    @staticmethod
    def sgb_tax_treatment(
        interest_earned: float,
        capital_gains: float,
        holding_years: int
    ) -> Dict[str, Any]:
        """
        Calculate tax treatment for Sovereign Gold Bonds

        SGB Tax Rules:
        - Interest: Taxable as income
        - Capital gains: Tax-free if held till maturity (8 years)
        - Premature redemption (after 5 years): LTCG with indexation

        Args:
            interest_earned: Interest earned
            capital_gains: Capital appreciation
            holding_years: Years held

        Returns:
            {
                'interest_taxable': float,
                'capital_gains': float,
                'capital_gains_taxable': bool,
                'tax_treatment': str
            }
        """
        # Interest is always taxable
        interest_taxable = interest_earned

        # Capital gains tax-free if held 8+ years
        capital_gains_taxable = holding_years < 8

        if holding_years >= 8:
            treatment = "Capital gains tax-free (held till maturity)"
        elif holding_years >= 5:
            treatment = "LTCG @ 20% with indexation (premature redemption)"
        else:
            treatment = "Cannot redeem before 5 years"

        return {
            'interest_taxable': round(interest_taxable, 2),
            'capital_gains': round(capital_gains, 2),
            'capital_gains_taxable': capital_gains_taxable,
            'tax_treatment': treatment
        }


# Global instance
tax_calculator = TaxCalculator()
