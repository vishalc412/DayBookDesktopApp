"""
Precious Metals Module - Pydantic Schemas
Request and response models for precious metals API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from .models import MetalType, MarketType, PurchaseForm, Purity, TransactionType


# ==================== Account Schemas ====================

class PreciousMetalsAccountBase(BaseModel):
    """Base schema for precious metals account"""
    account_name: str = Field(..., min_length=1, max_length=255)
    metal_type: MetalType
    market_type: MarketType
    default_purchase_form: Optional[PurchaseForm] = None
    default_purity: Optional[Purity] = None
    storage_location: Optional[str] = Field(None, max_length=255)
    locker_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PreciousMetalsAccountCreate(PreciousMetalsAccountBase):
    """Schema for creating precious metals account"""
    pass


class PreciousMetalsAccountUpdate(BaseModel):
    """Schema for updating precious metals account"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_location: Optional[str] = Field(None, max_length=255)
    locker_number: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class PreciousMetalsAccountResponse(PreciousMetalsAccountBase):
    """Schema for precious metals account response"""
    id: int
    total_quantity_grams: float
    total_invested: float
    average_purchase_price: float
    current_market_value: float
    profit_loss: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Transaction Schemas ====================

class PreciousMetalsTransactionBase(BaseModel):
    """Base schema for precious metals transaction"""
    transaction_type: TransactionType
    transaction_date: date
    purchase_form: PurchaseForm
    purity: Optional[Purity] = None
    quantity_grams: float = Field(..., gt=0)
    total_cost: float = Field(..., gt=0)


class IndianGoldTransactionCreate(BaseModel):
    """Schema for creating Indian gold transaction"""
    account_id: int
    transaction_type: TransactionType
    transaction_date: date
    purchase_form: PurchaseForm
    purity: Purity

    # Quantity
    quantity_grams: float = Field(..., gt=0)

    # Pricing
    gold_rate_per_10g: float = Field(..., gt=0)

    # Making charges
    making_charges_type: str = Field("percentage", pattern="^(percentage|per_gram)$")
    making_charges_value: float = Field(0, ge=0)

    # Additional charges
    include_gst: bool = True
    include_hallmark: bool = True
    item_count: int = Field(1, ge=1)

    # Vendor details
    vendor_or_buyer: Optional[str] = Field(None, max_length=255)
    bill_number: Optional[str] = Field(None, max_length=100)
    item_description: Optional[str] = None
    notes: Optional[str] = None


class IndianSilverTransactionCreate(BaseModel):
    """Schema for creating Indian silver transaction"""
    account_id: int
    transaction_type: TransactionType
    transaction_date: date
    purchase_form: PurchaseForm

    # Quantity
    quantity_grams: float = Field(..., gt=0)

    # Pricing
    silver_rate_per_kg: float = Field(..., gt=0)

    # Making charges
    making_charges_type: str = Field("percentage", pattern="^(percentage|per_gram)$")
    making_charges_value: float = Field(0, ge=0)

    # Additional charges
    include_gst: bool = True
    include_hallmark: bool = False
    item_count: int = Field(1, ge=1)

    # Vendor details
    vendor_or_buyer: Optional[str] = Field(None, max_length=255)
    bill_number: Optional[str] = Field(None, max_length=100)
    item_description: Optional[str] = None
    notes: Optional[str] = None


class InternationalBullionTransactionCreate(BaseModel):
    """Schema for creating international bullion transaction"""
    account_id: int
    transaction_type: TransactionType
    transaction_date: date
    purchase_form: PurchaseForm

    # Quantity
    quantity_troy_oz: float = Field(..., gt=0)

    # Pricing
    usd_per_troy_oz: float = Field(..., gt=0)
    usd_to_inr_rate: float = Field(..., gt=0)

    # Additional charges
    import_duty_percentage: float = Field(10.75, ge=0, le=100)
    shipping_charges: float = Field(0, ge=0)
    customs_charges: float = Field(0, ge=0)

    # Vendor details
    vendor_or_buyer: Optional[str] = Field(None, max_length=255)
    item_description: Optional[str] = None
    notes: Optional[str] = None


class SGBTransactionCreate(BaseModel):
    """Schema for creating Sovereign Gold Bonds transaction"""
    account_id: int
    transaction_type: TransactionType
    transaction_date: date

    # SGB specific
    quantity_grams: float = Field(..., gt=0)
    sgb_issue_price: float = Field(..., gt=0)
    sgb_issue_date: date
    sgb_certificate_number: Optional[str] = Field(None, max_length=100)

    # Vendor details
    vendor_or_buyer: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class PreciousMetalsTransactionResponse(BaseModel):
    """Schema for precious metals transaction response"""
    id: int
    account_id: int
    transaction_type: TransactionType
    transaction_date: date
    purchase_form: PurchaseForm
    purity: Optional[Purity]
    quantity_grams: float
    quantity_troy_oz: Optional[float]
    total_cost: float
    effective_rate_per_gram: Optional[float]

    # Pricing details
    gold_rate_per_10g: Optional[float]
    silver_rate_per_kg: Optional[float]
    base_metal_cost: Optional[float]
    making_charges: float
    hallmark_charges: float
    gst_amount: float

    # International
    usd_per_troy_oz: Optional[float]
    usd_to_inr_rate: Optional[float]
    import_duty: float

    # SGB
    sgb_issue_price: Optional[float]
    sgb_issue_date: Optional[date]
    sgb_certificate_number: Optional[str]

    # Vendor
    vendor_or_buyer: Optional[str]
    bill_number: Optional[str]
    item_description: Optional[str]
    item_count: int
    notes: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Rate Schemas ====================

class PreciousMetalsRateCreate(BaseModel):
    """Schema for creating precious metals rate"""
    metal_type: MetalType
    market_type: MarketType
    purity: Optional[Purity] = None
    rate_date: date

    # Rates (at least one required)
    rate_per_gram: Optional[float] = Field(None, gt=0)
    rate_per_10g: Optional[float] = Field(None, gt=0)
    rate_per_kg: Optional[float] = Field(None, gt=0)
    rate_per_troy_oz: Optional[float] = Field(None, gt=0)

    # Exchange rate
    usd_to_inr: Optional[float] = Field(None, gt=0)

    # Source
    source: Optional[str] = Field(None, max_length=100)

    @validator('rate_per_gram', 'rate_per_10g', 'rate_per_kg', 'rate_per_troy_oz')
    def at_least_one_rate(cls, v, values):
        """Ensure at least one rate is provided"""
        if not any([
            values.get('rate_per_gram'),
            values.get('rate_per_10g'),
            values.get('rate_per_kg'),
            values.get('rate_per_troy_oz'),
            v
        ]):
            raise ValueError('At least one rate must be provided')
        return v


class PreciousMetalsRateResponse(BaseModel):
    """Schema for precious metals rate response"""
    id: int
    metal_type: MetalType
    market_type: MarketType
    purity: Optional[Purity]
    rate_date: date
    rate_per_gram: Optional[float]
    rate_per_10g: Optional[float]
    rate_per_kg: Optional[float]
    rate_per_troy_oz: Optional[float]
    usd_to_inr: Optional[float]
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Portfolio & Analytics Schemas ====================

class PortfolioSummary(BaseModel):
    """Portfolio summary for dashboard"""
    total_accounts: int
    total_gold_grams: float
    total_silver_grams: float
    total_invested: float
    current_market_value: float
    total_profit_loss: float
    profit_loss_percentage: float


class AccountPortfolioSummary(BaseModel):
    """Portfolio summary for a single account"""
    account_id: int
    account_name: str
    metal_type: MetalType
    market_type: MarketType
    total_quantity_grams: float
    total_invested: float
    average_purchase_price: float
    current_market_price: float
    current_value: float
    profit_loss: float
    profit_loss_percentage: float
    transaction_count: int


class TransactionSummary(BaseModel):
    """Summary of a transaction"""
    id: int
    transaction_date: date
    transaction_type: TransactionType
    purchase_form: PurchaseForm
    quantity_grams: float
    total_cost: float
    effective_rate_per_gram: float


# ==================== Calculation Request Schemas ====================

class IndianGoldCostRequest(BaseModel):
    """Request for Indian gold cost calculation"""
    quantity_grams: float = Field(..., gt=0)
    gold_rate_per_10g: float = Field(..., gt=0)
    purity: Purity = Purity.PURITY_22K
    making_charges_type: str = Field("percentage", pattern="^(percentage|per_gram)$")
    making_charges_value: float = Field(0, ge=0)
    include_gst: bool = True
    include_hallmark: bool = True
    num_items: int = Field(1, ge=1)


class IndianSilverCostRequest(BaseModel):
    """Request for Indian silver cost calculation"""
    quantity_grams: float = Field(..., gt=0)
    silver_rate_per_kg: float = Field(..., gt=0)
    making_charges_type: str = Field("percentage", pattern="^(percentage|per_gram)$")
    making_charges_value: float = Field(0, ge=0)
    include_gst: bool = True
    include_hallmark: bool = False
    num_items: int = Field(1, ge=1)


class InternationalBullionCostRequest(BaseModel):
    """Request for international bullion cost calculation"""
    quantity_troy_oz: float = Field(..., gt=0)
    usd_per_troy_oz: float = Field(..., gt=0)
    usd_to_inr_rate: float = Field(..., gt=0)
    import_duty_percentage: float = Field(10.75, ge=0, le=100)
    shipping_charges: float = Field(0, ge=0)
    customs_charges: float = Field(0, ge=0)


class SGBReturnsRequest(BaseModel):
    """Request for SGB returns calculation"""
    issue_price: float = Field(..., gt=0)
    quantity_grams: float = Field(..., gt=0)
    purchase_date: date
    current_gold_price: Optional[float] = Field(None, gt=0)
    redemption_date: Optional[date] = None
    annual_interest_rate: float = Field(2.5, gt=0, le=100)


class PortfolioValuationRequest(BaseModel):
    """Request for portfolio valuation"""
    account_id: int
    current_market_price_per_gram: float = Field(..., gt=0)
