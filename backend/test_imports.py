"""
Comprehensive Import and Syntax Test
Tests all modules to ensure no import errors or syntax issues
"""

import sys
import traceback

def test_module(module_name, description):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✓ {description}")
        return True
    except Exception as e:
        print(f"✗ {description}")
        print(f"  Error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("DAYBOOK V2.0 - COMPREHENSIVE IMPORT TEST")
    print("=" * 60)
    print()

    results = []

    # Test Security Module
    print("SECURITY MODULE:")
    results.append(test_module("app.modules.security.encryption", "Encryption module"))
    results.append(test_module("app.modules.security.master_password", "Master password module"))
    results.append(test_module("app.modules.security.session_manager", "Session manager"))
    results.append(test_module("app.modules.security.config_manager", "Config manager"))
    results.append(test_module("app.modules.security.models", "Security models"))
    results.append(test_module("app.modules.security.api", "Security API"))
    print()

    # Test Calculations Module
    print("CALCULATIONS MODULE:")
    results.append(test_module("app.modules.calculations.roi_calculator", "ROI calculator"))
    results.append(test_module("app.modules.calculations.precious_metals_calculator", "Precious metals calculator"))
    results.append(test_module("app.modules.calculations.tax_calculator", "Tax calculator"))
    print()

    # Test Savings Module
    print("SAVINGS MODULE:")
    results.append(test_module("app.modules.savings.models", "Savings models"))
    results.append(test_module("app.modules.savings.schemas", "Savings schemas"))
    results.append(test_module("app.modules.savings.api", "Savings API"))
    print()

    # Test Precious Metals Module
    print("PRECIOUS METALS MODULE:")
    results.append(test_module("app.modules.precious_metals.models", "Precious metals models"))
    results.append(test_module("app.modules.precious_metals.schemas", "Precious metals schemas"))
    results.append(test_module("app.modules.precious_metals.api", "Precious metals API"))
    print()

    # Test Expenses Module
    print("EXPENSES MODULE:")
    results.append(test_module("app.modules.expenses.models", "Expenses models"))
    results.append(test_module("app.modules.expenses.schemas", "Expenses schemas"))
    results.append(test_module("app.modules.expenses.api", "Expenses API"))
    print()

    # Test Main Application
    print("MAIN APPLICATION:")
    results.append(test_module("app.models_registry", "Models registry"))
    results.append(test_module("app.api_v2", "Main API v2"))
    print()

    # Summary
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"SUMMARY: {passed}/{total} tests passed")
    if failed > 0:
        print(f"⚠ {failed} tests FAILED")
        sys.exit(1)
    else:
        print("✓ ALL TESTS PASSED - No import errors!")
        sys.exit(0)

if __name__ == "__main__":
    main()
