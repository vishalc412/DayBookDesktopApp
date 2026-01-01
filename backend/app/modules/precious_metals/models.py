"""
Precious Metals Module - Database Models
Gold and Silver portfolio tracking (Indian & International markets)
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MetalType(str, enum.Enum):
    """Types of precious metals"""
    GOLD = "Gold"
    SILVER = "Silver"
    PLATINUM = "Platinum"
    PALLADIUM = "Palladium"


class MarketType(str, enum.Enum):
    """Market types"""
    INDIAN = "Indian"
    INTERNATIONAL = "International"


class PurchaseForm(str, enum.Enum):
    """Form of precious metal purchase"""
    PHYSICAL_JEWELRY = "Physical Jewelry"
    PHYSICAL_COINS = "Physical Coins"
    PHYSICAL_BARS = "Physical Bars"
    SOVEREIGN_GOLD_BONDS = "Sovereign Gold Bonds (SGB)"
    DIGITAL_GOLD = "Digital Gold"
    GOLD_ETF = "Gold ETF"
    GOLD_MUTUAL_FUND = "Gold Mutual Fund"
    SILVER_ETF = "Silver ETF"


class Purity(str, enum.Enum):
    """Metal purity"""
    PURITY_24K = "24K"  # 99.99%
    PURITY_22K = "22K"  # 91.67%
    PURITY_18K = "18K"  # 75.00%
    PURITY_14K = "14K"  # 58.33%
    PURITY_999 = "999"  # 99.9% (Silver/Platinum)
    PURITY_925 = "925"  # 92.5% (Sterling Silver)


class TransactionType(str, enum.Enum):
    """Transaction types"""
    BUY = "Buy"
    SELL = "Sell"
    GIFT_RECEIVED = "Gift Received"
    GIFT_GIVEN = "Gift Given"
    TRANSFER_IN = "Transfer In"
    TRANSFER_OUT = "Transfer Out"


class PreciousMetalsAccount(Base):
    """
    Precious Metals Account Model

    Represents a portfolio of gold/silver holdings
    """
    __tablename__ = "precious_metals_accounts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Account Details
    account_name = Column(String(255), nullable=False, index=True)
    metal_type = Column(SQLEnum(MetalType), nullable=False, index=True)
    market_type = Column(SQLEnum(MarketType), nullable=False, index=True)

    # Default purchase form for this account
    default_purchase_form = Column(SQLEnum(PurchaseForm), nullable=True)
    default_purity = Column(SQLEnum(Purity), nullable=True)

    # Portfolio Summary (calculated from transactions)
    total_quantity_grams = Column(Float, default=0.0)  # Total holdings in grams
    total_invested = Column(Float, default=0.0)  # Total money invested
    average_purchase_price = Column(Float, default=0.0)  # Average price per gram
    current_market_value = Column(Float, default=0.0)  # Current portfolio value
    profit_loss = Column(Float, default=0.0)  # Unrealized profit/loss

    # Storage Details
    storage_location = Column(String(255), nullable=True)  # Bank locker, home safe, etc.
    locker_number = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    transactions = relationship("PreciousMetalsTransaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PreciousMetalsAccount(id={self.id}, name='{self.account_name}', metal='{self.metal_type}', quantity={self.total_quantity_grams}g)>"


class PreciousMetalsTransaction(Base):
    """
    Precious Metals Transaction Model

    Represents individual buy/sell transactions
    """
    __tablename__ = "precious_metals_transactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key
    account_id = Column(Integer, ForeignKey("precious_metals_accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Transaction Details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)

    # Metal Details
    purchase_form = Column(SQLEnum(PurchaseForm), nullable=False)
    purity = Column(SQLEnum(Purity), nullable=True)

    # Quantity
    quantity_grams = Column(Float, nullable=False)  # Always store in grams
    quantity_troy_oz = Column(Float, nullable=True)  # Optional troy ounces

    # Pricing (Indian Market)
    gold_rate_per_10g = Column(Float, nullable=True)  # For Indian gold
    silver_rate_per_kg = Column(Float, nullable=True)  # For Indian silver
    base_metal_cost = Column(Float, nullable=True)  # Base cost of metal

    # Additional Costs (Indian Market)
    making_charges = Column(Float, default=0.0)
    making_charges_type = Column(String(50), nullable=True)  # "percentage" or "per_gram"
    hallmark_charges = Column(Float, default=0.0)
    gst_amount = Column(Float, default=0.0)

    # International Market
    usd_per_troy_oz = Column(Float, nullable=True)  # International price
    usd_to_inr_rate = Column(Float, nullable=True)  # Exchange rate
    import_duty = Column(Float, default=0.0)
    shipping_charges = Column(Float, default=0.0)
    customs_charges = Column(Float, default=0.0)

    # Total Cost
    total_cost = Column(Float, nullable=False)  # Total amount paid/received
    effective_rate_per_gram = Column(Float, nullable=True)  # Effective price per gram

    # Vendor/Buyer Details
    vendor_or_buyer = Column(String(255), nullable=True)  # Jeweller name, platform, etc.
    bill_number = Column(String(100), nullable=True)
    bill_image_path = Column(String(500), nullable=True)  # Path to scanned bill

    # Item Details (for jewelry)
    item_description = Column(Text, nullable=True)  # "Gold necklace", "Silver coins", etc.
    item_count = Column(Integer, default=1)  # Number of items

    # SGB Specific
    sgb_issue_price = Column(Float, nullable=True)  # Issue price for SGB
    sgb_issue_date = Column(Date, nullable=True)
    sgb_certificate_number = Column(String(100), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("PreciousMetalsAccount", back_populates="transactions")

    def __repr__(self):
        return f"<PreciousMetalsTransaction(id={self.id}, type='{self.transaction_type}', quantity={self.quantity_grams}g, cost={self.total_cost})>"


class PreciousMetalsRate(Base):
    """
    Precious Metals Rate Model

    Stores historical and current gold/silver rates
    """
    __tablename__ = "precious_metals_rates"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Metal & Market
    metal_type = Column(SQLEnum(MetalType), nullable=False, index=True)
    market_type = Column(SQLEnum(MarketType), nullable=False, index=True)
    purity = Column(SQLEnum(Purity), nullable=True)

    # Date
    rate_date = Column(Date, nullable=False, index=True)

    # Rates
    rate_per_gram = Column(Float, nullable=True)  # ₹ per gram (Indian) or $ per gram (International)
    rate_per_10g = Column(Float, nullable=True)  # ₹ per 10 grams (common in India)
    rate_per_kg = Column(Float, nullable=True)  # ₹ per kg (for silver)
    rate_per_troy_oz = Column(Float, nullable=True)  # $ per troy oz (International)

    # Exchange Rate (if applicable)
    usd_to_inr = Column(Float, nullable=True)

    # Source
    source = Column(String(100), nullable=True)  # "Manual", "API", "IBJA", "MCX", etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PreciousMetalsRate(id={self.id}, metal='{self.metal_type}', market='{self.market_type}', date={self.rate_date}, rate={self.rate_per_gram})>"
