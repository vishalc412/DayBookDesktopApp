"""
Precious Metals Calculator
Indian and International gold/silver cost calculations
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
import math


class PreciousMetalsCalculator:
    """
    Precious Metals Cost Calculator

    Supports:
    - Indian gold/silver with making charges, GST, hallmark
    - International bullion with import duty
    - Unit conversions (grams ↔ troy ounces)
    - Portfolio valuation
    - SGB calculations
    """

    # Constants
    GRAMS_PER_TROY_OZ = 31.1035
    INDIAN_GOLD_GST_RATE = 3.0  # 3% GST on gold in India
    INDIAN_SILVER_GST_RATE = 3.0  # 3% GST on silver
    INDIAN_GOLD_IMPORT_DUTY = 10.75  # 10.75% import duty
    HALLMARK_CHARGE_PER_ITEM = 40.0  # BIS hallmark charges (₹35-45)

    # Purity factors
    PURITY_24K = 0.9999  # 99.99%
    PURITY_22K = 0.9167  # 91.67%
    PURITY_18K = 0.7500  # 75.00%
    PURITY_14K = 0.5833  # 58.33%

    @staticmethod
    def _round_currency(value: float) -> float:
        """Round to 2 decimal places"""
        return round(value, 2)

    @staticmethod
    def _round_quantity(value: float) -> float:
        """Round to 4 decimal places (for grams)"""
        return round(value, 4)

    @staticmethod
    def grams_to_troy_oz(grams: float) -> float:
        """
        Convert grams to troy ounces

        Args:
            grams: Weight in grams

        Returns:
            Weight in troy ounces
        """
        return PreciousMetalsCalculator._round_quantity(
            grams / PreciousMetalsCalculator.GRAMS_PER_TROY_OZ
        )

    @staticmethod
    def troy_oz_to_grams(troy_oz: float) -> float:
        """
        Convert troy ounces to grams

        Args:
            troy_oz: Weight in troy ounces

        Returns:
            Weight in grams
        """
        return PreciousMetalsCalculator._round_quantity(
            troy_oz * PreciousMetalsCalculator.GRAMS_PER_TROY_OZ
        )

    @staticmethod
    def get_purity_factor(purity: str) -> float:
        """
        Get purity factor from purity string

        Args:
            purity: "24K", "22K", "18K", or "14K"

        Returns:
            Purity factor (0-1)
        """
        purity_map = {
            "24K": PreciousMetalsCalculator.PURITY_24K,
            "22K": PreciousMetalsCalculator.PURITY_22K,
            "18K": PreciousMetalsCalculator.PURITY_18K,
            "14K": PreciousMetalsCalculator.PURITY_14K,
        }
        return purity_map.get(purity.upper(), 1.0)

    @staticmethod
    def indian_gold_cost(
        quantity_grams: float,
        gold_rate_per_10g: float,
        purity: str = "22K",
        making_charges_type: str = "percentage",  # "percentage" or "per_gram"
        making_charges_value: float = 0,
        include_gst: bool = True,
        include_hallmark: bool = True,
        num_items: int = 1
    ) -> Dict[str, float]:
        """
        Calculate Indian gold jewelry/coin cost

        Args:
            quantity_grams: Weight in grams
            gold_rate_per_10g: Gold rate per 10 grams (₹)
            purity: "24K", "22K", "18K", or "14K"
            making_charges_type: "percentage" or "per_gram"
            making_charges_value: Making charges (% or ₹/gram)
            include_gst: Include GST (3%)
            include_hallmark: Include hallmark charges
            num_items: Number of items (for hallmark charges)

        Returns:
            {
                'quantity_grams': float,
                'gold_rate_per_10g': float,
                'purity': str,
                'purity_factor': float,
                'base_gold_cost': float,
                'making_charges': float,
                'subtotal': float,
                'hallmark_charges': float,
                'gst_amount': float,
                'total_cost': float,
                'effective_rate_per_gram': float
            }
        """
        # Calculate base gold cost
        purity_factor = PreciousMetalsCalculator.get_purity_factor(purity)

        # Adjust for purity
        effective_rate_per_gram = (gold_rate_per_10g / 10) * purity_factor
        base_gold_cost = effective_rate_per_gram * quantity_grams

        # Calculate making charges
        if making_charges_type == "percentage":
            making_charges = base_gold_cost * (making_charges_value / 100)
        else:  # per_gram
            making_charges = making_charges_value * quantity_grams

        subtotal = base_gold_cost + making_charges

        # Hallmark charges
        hallmark_charges = 0
        if include_hallmark:
            hallmark_charges = PreciousMetalsCalculator.HALLMARK_CHARGE_PER_ITEM * num_items

        subtotal += hallmark_charges

        # GST
        gst_amount = 0
        if include_gst:
            gst_amount = subtotal * (PreciousMetalsCalculator.INDIAN_GOLD_GST_RATE / 100)

        total_cost = subtotal + gst_amount

        # Effective rate per gram (total cost / quantity)
        effective_rate = total_cost / quantity_grams if quantity_grams > 0 else 0

        return {
            'quantity_grams': PreciousMetalsCalculator._round_quantity(quantity_grams),
            'gold_rate_per_10g': PreciousMetalsCalculator._round_currency(gold_rate_per_10g),
            'purity': purity,
            'purity_factor': purity_factor,
            'base_gold_cost': PreciousMetalsCalculator._round_currency(base_gold_cost),
            'making_charges': PreciousMetalsCalculator._round_currency(making_charges),
            'subtotal_before_tax': PreciousMetalsCalculator._round_currency(subtotal),
            'hallmark_charges': PreciousMetalsCalculator._round_currency(hallmark_charges),
            'gst_amount': PreciousMetalsCalculator._round_currency(gst_amount),
            'total_cost': PreciousMetalsCalculator._round_currency(total_cost),
            'effective_rate_per_gram': PreciousMetalsCalculator._round_currency(effective_rate)
        }

    @staticmethod
    def indian_silver_cost(
        quantity_grams: float,
        silver_rate_per_kg: float,
        making_charges_type: str = "percentage",
        making_charges_value: float = 0,
        include_gst: bool = True,
        include_hallmark: bool = True,
        num_items: int = 1
    ) -> Dict[str, float]:
        """
        Calculate Indian silver jewelry/coin cost

        Args:
            quantity_grams: Weight in grams
            silver_rate_per_kg: Silver rate per kg (₹)
            making_charges_type: "percentage" or "per_gram"
            making_charges_value: Making charges (% or ₹/gram)
            include_gst: Include GST (3%)
            include_hallmark: Include hallmark charges
            num_items: Number of items

        Returns:
            Similar to indian_gold_cost
        """
        # Base silver cost
        silver_rate_per_gram = silver_rate_per_kg / 1000
        base_silver_cost = silver_rate_per_gram * quantity_grams

        # Making charges
        if making_charges_type == "percentage":
            making_charges = base_silver_cost * (making_charges_value / 100)
        else:
            making_charges = making_charges_value * quantity_grams

        subtotal = base_silver_cost + making_charges

        # Hallmark
        hallmark_charges = 0
        if include_hallmark:
            hallmark_charges = PreciousMetalsCalculator.HALLMARK_CHARGE_PER_ITEM * num_items

        subtotal += hallmark_charges

        # GST
        gst_amount = 0
        if include_gst:
            gst_amount = subtotal * (PreciousMetalsCalculator.INDIAN_SILVER_GST_RATE / 100)

        total_cost = subtotal + gst_amount

        effective_rate = total_cost / quantity_grams if quantity_grams > 0 else 0

        return {
            'quantity_grams': PreciousMetalsCalculator._round_quantity(quantity_grams),
            'silver_rate_per_kg': PreciousMetalsCalculator._round_currency(silver_rate_per_kg),
            'silver_rate_per_gram': PreciousMetalsCalculator._round_currency(silver_rate_per_gram),
            'base_silver_cost': PreciousMetalsCalculator._round_currency(base_silver_cost),
            'making_charges': PreciousMetalsCalculator._round_currency(making_charges),
            'subtotal_before_tax': PreciousMetalsCalculator._round_currency(subtotal),
            'hallmark_charges': PreciousMetalsCalculator._round_currency(hallmark_charges),
            'gst_amount': PreciousMetalsCalculator._round_currency(gst_amount),
            'total_cost': PreciousMetalsCalculator._round_currency(total_cost),
            'effective_rate_per_gram': PreciousMetalsCalculator._round_currency(effective_rate)
        }

    @staticmethod
    def international_bullion_cost(
        quantity_troy_oz: float,
        usd_per_troy_oz: float,
        usd_to_inr_rate: float,
        import_duty_percentage: float = 10.75,
        shipping_charges: float = 0,
        customs_charges: float = 0
    ) -> Dict[str, float]:
        """
        Calculate international bullion cost (imported gold/silver)

        Args:
            quantity_troy_oz: Quantity in troy ounces
            usd_per_troy_oz: Price per troy oz in USD
            usd_to_inr_rate: USD to INR conversion rate
            import_duty_percentage: Import duty % (default 10.75% for gold)
            shipping_charges: Shipping in INR
            customs_charges: Additional customs in INR

        Returns:
            {
                'quantity_troy_oz': float,
                'quantity_grams': float,
                'usd_per_troy_oz': float,
                'cost_usd': float,
                'cost_inr_before_duty': float,
                'import_duty': float,
                'shipping_charges': float,
                'customs_charges': float,
                'total_cost_inr': float,
                'effective_rate_per_gram': float
            }
        """
        # Cost in USD
        cost_usd = quantity_troy_oz * usd_per_troy_oz

        # Convert to INR
        cost_inr_before_duty = cost_usd * usd_to_inr_rate

        # Import duty
        import_duty = cost_inr_before_duty * (import_duty_percentage / 100)

        # Total cost
        total_cost = cost_inr_before_duty + import_duty + shipping_charges + customs_charges

        # Convert quantity to grams
        quantity_grams = PreciousMetalsCalculator.troy_oz_to_grams(quantity_troy_oz)

        # Effective rate per gram
        effective_rate = total_cost / quantity_grams if quantity_grams > 0 else 0

        return {
            'quantity_troy_oz': PreciousMetalsCalculator._round_quantity(quantity_troy_oz),
            'quantity_grams': PreciousMetalsCalculator._round_quantity(quantity_grams),
            'usd_per_troy_oz': PreciousMetalsCalculator._round_currency(usd_per_troy_oz),
            'cost_usd': PreciousMetalsCalculator._round_currency(cost_usd),
            'usd_to_inr_rate': PreciousMetalsCalculator._round_currency(usd_to_inr_rate),
            'cost_inr_before_duty': PreciousMetalsCalculator._round_currency(cost_inr_before_duty),
            'import_duty': PreciousMetalsCalculator._round_currency(import_duty),
            'shipping_charges': PreciousMetalsCalculator._round_currency(shipping_charges),
            'customs_charges': PreciousMetalsCalculator._round_currency(customs_charges),
            'total_cost_inr': PreciousMetalsCalculator._round_currency(total_cost),
            'effective_rate_per_gram': PreciousMetalsCalculator._round_currency(effective_rate)
        }

    @staticmethod
    def current_portfolio_value(
        total_quantity_grams: float,
        average_purchase_price_per_gram: float,
        current_market_price_per_gram: float
    ) -> Dict[str, float]:
        """
        Calculate current portfolio value and profit/loss

        Args:
            total_quantity_grams: Total holdings in grams
            average_purchase_price_per_gram: Average buy price per gram
            current_market_price_per_gram: Current market price per gram

        Returns:
            {
                'total_quantity_grams': float,
                'average_purchase_price': float,
                'total_invested': float,
                'current_market_price': float,
                'current_value': float,
                'profit_loss': float,
                'profit_loss_percentage': float
            }
        """
        total_invested = total_quantity_grams * average_purchase_price_per_gram
        current_value = total_quantity_grams * current_market_price_per_gram

        profit_loss = current_value - total_invested

        profit_loss_percentage = 0
        if total_invested > 0:
            profit_loss_percentage = (profit_loss / total_invested) * 100

        return {
            'total_quantity_grams': PreciousMetalsCalculator._round_quantity(total_quantity_grams),
            'average_purchase_price': PreciousMetalsCalculator._round_currency(average_purchase_price_per_gram),
            'total_invested': PreciousMetalsCalculator._round_currency(total_invested),
            'current_market_price': PreciousMetalsCalculator._round_currency(current_market_price_per_gram),
            'current_value': PreciousMetalsCalculator._round_currency(current_value),
            'profit_loss': PreciousMetalsCalculator._round_currency(profit_loss),
            'profit_loss_percentage': PreciousMetalsCalculator._round_currency(profit_loss_percentage)
        }

    @staticmethod
    def estimate_making_charges(
        jewelry_type: str,
        weight_grams: float,
        purity: str = "22K"
    ) -> Dict[str, float]:
        """
        Estimate making charges based on jewelry type

        Args:
            jewelry_type: "plain", "studded", "coins", "bars"
            weight_grams: Weight in grams
            purity: Purity (affects base price)

        Returns:
            {
                'type': str,
                'weight_grams': float,
                'estimated_percentage': float,
                'estimated_per_gram': float,
                'recommendation': str
            }
        """
        estimates = {
            "plain": {
                "percentage": 10,
                "per_gram_min": 300,
                "per_gram_max": 800,
                "recommendation": "Plain gold jewelry typically 6-14% or ₹300-800/gram"
            },
            "studded": {
                "percentage": 20,
                "per_gram_min": 500,
                "per_gram_max": 1500,
                "recommendation": "Diamond/stone jewelry typically 15-25%"
            },
            "coins": {
                "percentage": 3,
                "per_gram_min": 100,
                "per_gram_max": 200,
                "recommendation": "Gold coins typically ₹100-200 per gram"
            },
            "bars": {
                "percentage": 2,
                "per_gram_min": 50,
                "per_gram_max": 100,
                "recommendation": "Gold bars typically 2-3% or flat ₹50-100"
            }
        }

        estimate = estimates.get(jewelry_type.lower(), estimates["plain"])

        return {
            'type': jewelry_type,
            'weight_grams': PreciousMetalsCalculator._round_quantity(weight_grams),
            'estimated_percentage': estimate["percentage"],
            'estimated_per_gram_min': estimate["per_gram_min"],
            'estimated_per_gram_max': estimate["per_gram_max"],
            'recommendation': estimate["recommendation"]
        }


# Global instance
precious_metals_calculator = PreciousMetalsCalculator()
