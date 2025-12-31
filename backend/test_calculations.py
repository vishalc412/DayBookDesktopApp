"""
Functional Test - Calculations Module
Tests core calculation logic without requiring database or server
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.modules.calculations.roi_calculator import roi_calculator
from app.modules.calculations.precious_metals_calculator import precious_metals_calculator
from app.modules.calculations.tax_calculator import tax_calculator
from datetime import date, timedelta

def test_roi_calculations():
    """Test ROI calculator functions"""
    print("\n" + "=" * 60)
    print("TESTING ROI CALCULATOR")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Simple Interest
    print("\n1. Simple Interest (₹100,000 @ 8% for 1 year)")
    result = roi_calculator.simple_interest(100000, 8, 1)
    expected_interest = 8000
    if abs(result['simple_interest'] - expected_interest) < 0.01:
        print(f"   ✓ Interest: ₹{result['simple_interest']} (Expected: ₹{expected_interest})")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Got ₹{result['simple_interest']}, Expected ₹{expected_interest}")
        tests_failed += 1

    # Test 2: Compound Interest (Quarterly)
    print("\n2. Compound Interest (₹100,000 @ 7.5% for 1 year, Quarterly)")
    result = roi_calculator.compound_interest(100000, 7.5, 1, 4)
    if result['maturity_amount'] > 107000 and result['maturity_amount'] < 108000:
        print(f"   ✓ Maturity: ₹{result['maturity_amount']:.2f}")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Maturity out of expected range")
        tests_failed += 1

    # Test 3: Recurring Deposit
    print("\n3. Recurring Deposit (₹5,000/month @ 7% for 12 months)")
    result = roi_calculator.recurring_deposit(5000, 7, 12)
    if result['maturity_amount'] > 62000 and result['maturity_amount'] < 63000:
        print(f"   ✓ Maturity: ₹{result['maturity_amount']:.2f}")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Maturity out of expected range")
        tests_failed += 1

    # Test 4: PPF
    print("\n4. PPF (₹150,000/year @ 7.1% for 15 years)")
    result = roi_calculator.ppf_maturity(150000, 7.1, 15)
    if result['maturity_amount'] > 4000000 and result['maturity_amount'] < 4100000:
        print(f"   ✓ Maturity: ₹{result['maturity_amount']:.2f}")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Maturity out of expected range")
        tests_failed += 1

    return tests_passed, tests_failed

def test_precious_metals_calculations():
    """Test precious metals calculator"""
    print("\n" + "=" * 60)
    print("TESTING PRECIOUS METALS CALCULATOR")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Indian Gold (22K, 10g, ₹72,000/10g)
    print("\n1. Indian Gold Cost (10g, 22K @ ₹72,000/10g, 12% making, GST, 2 items)")
    result = precious_metals_calculator.indian_gold_cost(
        quantity_grams=10,
        gold_rate_per_10g=72000,
        purity="PURITY_22K",
        making_charges_type="percentage",
        making_charges_value=12,
        include_gst=True,
        include_hallmark=True,
        num_items=2
    )

    if result['total_cost'] > 80000 and result['total_cost'] < 90000:
        print(f"   ✓ Total Cost: ₹{result['total_cost']:.2f} (includes base + making + GST + hallmark)")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Total cost out of expected range: ₹{result['total_cost']:.2f}")
        tests_failed += 1

    # Test 2: International Bullion (1 troy oz @ $2,000, ₹83/USD)
    print("\n2. International Bullion (1 troy oz @ $2,000, ₹83/$)")
    result = precious_metals_calculator.international_bullion_cost(
        quantity_troy_oz=1,
        usd_per_troy_oz=2000,
        usd_to_inr_rate=83,
        import_duty_percentage=10.75,
        shipping_charges=500,
        customs_charges=300
    )

    if result['total_cost_inr'] > 180000 and result['total_cost_inr'] < 190000:
        print(f"   ✓ Total Cost (INR): ₹{result['total_cost_inr']:.2f} (includes base + duty + shipping + customs)")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Total cost out of expected range: ₹{result['total_cost_inr']:.2f}")
        tests_failed += 1

    # Test 3: Troy Ounce Conversion
    print("\n3. Troy Ounce Conversion (1 troy oz = 31.1035g)")
    grams = precious_metals_calculator.troy_oz_to_grams(1)
    if abs(grams - 31.1035) < 0.0001:
        print(f"   ✓ 1 troy oz = {grams}g")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Got {grams}g, Expected 31.1035g")
        tests_failed += 1

    return tests_passed, tests_failed

def test_tax_calculations():
    """Test tax calculator"""
    print("\n" + "=" * 60)
    print("TESTING TAX CALCULATOR")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: STCG (Short-term Capital Gains)
    print("\n1. STCG (Equity sold within 12 months)")
    result = tax_calculator.calculate_stcg(
        sale_price=150000,
        purchase_price=100000,
        holding_period_days=300,
        asset_type="equity"
    )

    if result['capital_gain'] == 50000 and result['is_short_term']:
        print(f"   ✓ Capital Gain: ₹{result['capital_gain']}")
        print(f"   ✓ Is Short-Term: {result['is_short_term']}")
        print(f"   ✓ Treatment: {result['tax_treatment']}")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Expected ₹50,000 STCG")
        tests_failed += 1

    # Test 2: LTCG (Long-term Capital Gains - Equity)
    print("\n2. LTCG (Equity @ 10% above ₹1 lakh exemption)")
    result = tax_calculator.calculate_ltcg(
        sale_price=300000,
        purchase_price=100000,
        holding_period_days=400,
        asset_type="equity"
    )

    expected_tax = 10000  # (200000 - 100000) * 10%
    if abs(result['tax_amount'] - expected_tax) < 0.01:
        print(f"   ✓ Capital Gain: ₹{result['capital_gain']}")
        print(f"   ✓ Taxable Gain: ₹{result['taxable_gain']}")
        print(f"   ✓ Tax Amount: ₹{result['tax_amount']} (Expected: ₹{expected_tax})")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: Got ₹{result['tax_amount']}, Expected ₹{expected_tax}")
        tests_failed += 1

    # Test 3: TDS on Interest
    print("\n3. TDS on Interest (₹60,000 interest, general citizen)")
    result = tax_calculator.tds_on_interest(60000, is_senior_citizen=False)

    expected_tds = 6000  # 10% of 60000
    if result['tds_applicable'] and abs(result['tds_amount'] - expected_tds) < 0.01:
        print(f"   ✓ Interest: ₹{result['interest_amount']}")
        print(f"   ✓ Threshold: ₹{result['threshold']}")
        print(f"   ✓ TDS Applicable: {result['tds_applicable']}")
        print(f"   ✓ TDS Amount: ₹{result['tds_amount']} (Expected: ₹{expected_tds})")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: TDS calculation incorrect")
        tests_failed += 1

    # Test 4: SGB Tax Treatment
    print("\n4. SGB Tax Treatment (held 8+ years = tax-free)")
    result = tax_calculator.sgb_tax_treatment(
        interest_earned=5000,
        capital_gains=50000,
        holding_years=8
    )

    if not result['capital_gains_taxable'] and "tax-free" in result['tax_treatment']:
        print(f"   ✓ Interest Taxable: ₹{result['interest_taxable']}")
        print(f"   ✓ Capital Gains Taxable: {result['capital_gains_taxable']}")
        print(f"   ✓ Treatment: {result['tax_treatment']}")
        tests_passed += 1
    else:
        print(f"   ✗ FAILED: SGB tax treatment incorrect")
        tests_failed += 1

    return tests_passed, tests_failed

def main():
    print("=" * 60)
    print("DAYBOOK V2.0 - FUNCTIONAL TESTING")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    # Run all tests
    passed, failed = test_roi_calculations()
    total_passed += passed
    total_failed += failed

    passed, failed = test_precious_metals_calculations()
    total_passed += passed
    total_failed += failed

    passed, failed = test_tax_calculations()
    total_passed += passed
    total_failed += failed

    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")

    if total_failed == 0:
        print("\n✓ ALL FUNCTIONAL TESTS PASSED!")
        print("✓ Calculations are accurate and working correctly")
        sys.exit(0)
    else:
        print(f"\n⚠ {total_failed} TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
