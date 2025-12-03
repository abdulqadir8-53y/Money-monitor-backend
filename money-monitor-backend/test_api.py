#!/usr/bin/env python3
"""
Test Script for Money Monitor API
Run this after starting the server to verify all endpoints work
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

# ============================================================================
# TEST 1: Health Check
# ============================================================================

def test_health_check():
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy: {data['service']} v{data['version']}")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        print_info("Make sure to run: python main.py")
        return False

# ============================================================================
# TEST 2: Add Expense
# ============================================================================

def test_add_expense():
    print_header("TEST 2: Add Expense")
    
    expense_data = {
        "item": "Fuel",
        "amount": 150.50,
        "type": "personal",
        "category": "transport",
        "note": "Filled up petrol tank",
        "source": "manual"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/expenses/add?userId={TEST_USER_ID}",
            json=expense_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Expense added: {data['message']}")
            print_info(f"Expense ID: {data['expenseId']}")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to add expense: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 3: Get Expense Totals
# ============================================================================

def test_get_totals():
    print_header("TEST 3: Get Expense Totals")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses/totals/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Expense totals retrieved")
            totals = data['totals']
            print_info(f"Total Expenses: Rs. {totals['total']}")
            print_info(f"Personal: Rs. {totals['personal']}")
            print_info(f"Business: Rs. {totals['business']}")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to get totals: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 4: Get All Expenses
# ============================================================================

def test_get_expenses():
    print_header("TEST 4: Get All Expenses")
    
    try:
        response = requests.get(f"{BASE_URL}/expenses/{TEST_USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data['count']} expense(s)")
            
            if data['count'] > 0:
                print_info("First expense:")
                print(json.dumps(data['expenses'][0], indent=2))
            
            return True
        else:
            print_error(f"Failed to get expenses: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 5: Save Merchant
# ============================================================================

def test_save_merchant():
    print_header("TEST 5: Save Merchant")
    
    try:
        response = requests.post(
            f"{BASE_URL}/merchants/save?userId={TEST_USER_ID}&merchant=Shell%20Petrol&category=transport&type=personal"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Merchant saved: {data['message']}")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to save merchant: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 6: Lookup Merchant
# ============================================================================

def test_lookup_merchant():
    print_header("TEST 6: Lookup Merchant")
    
    try:
        response = requests.get(
            f"{BASE_URL}/merchants/lookup/{TEST_USER_ID}/Shell%20Petrol"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['found']:
                print_success(f"Merchant found!")
                print_info(f"Category: {data['category']}")
                print_info(f"Type: {data['type']}")
            else:
                print_info("Merchant not found in database")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to lookup merchant: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 7: Category Summary
# ============================================================================

def test_category_summary():
    print_header("TEST 7: Category Summary")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/category-summary?userId={TEST_USER_ID}&type=personal"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Category summary retrieved")
            print_info(f"Total Spent: Rs. {data['totalSpent']}")
            
            if data['categories']:
                print_info("Breakdown by category:")
                for category, info in data['categories'].items():
                    print(f"  - {category}: Rs. {info['total']} ({info['percentage']}%)")
            
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to get category summary: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 8: Monthly Trend
# ============================================================================

def test_monthly_trend():
    print_header("TEST 8: Monthly Trend")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/monthly-trend?userId={TEST_USER_ID}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Monthly trend retrieved")
            
            if data['trend']:
                print_info("Spending by month:")
                for month, info in data['trend'].items():
                    print(f"  - {month}: Rs. {info['total']} ({info['count']} transactions)")
            
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to get monthly trend: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# TEST 9: Merchant Spend Query (AI)
# ============================================================================

def test_merchant_spend():
    print_header("TEST 9: Merchant Spend Query (AI)")
    
    query_data = {
        "merchant": "Fuel",
        "userId": TEST_USER_ID,
        "startDate": "2025-01-01",
        "endDate": "2025-12-31"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/merchant-spend",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Merchant spend query successful")
            print_info(f"Merchant: {data['merchant']}")
            print_info(f"Total Spent: Rs. {data['totalSpent']}")
            print_info(f"Transactions: {data['transactionCount']}")
            
            if data['byCategory']:
                print_info("Breakdown:")
                for cat, amount in data['byCategory'].items():
                    print(f"  - {cat}: Rs. {amount}")
            
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Failed to query merchant spend: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     Money Monitor API - Verification Test Suite       ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test User ID: {TEST_USER_ID}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Add Expense", test_add_expense),
        ("Get Totals", test_get_totals),
        ("Get Expenses", test_get_expenses),
        ("Save Merchant", test_save_merchant),
        ("Lookup Merchant", test_lookup_merchant),
        ("Category Summary", test_category_summary),
        ("Monthly Trend", test_monthly_trend),
        ("Merchant Spend (AI)", test_merchant_spend),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_success("All tests passed! Your API is working correctly. 🎉")
    else:
        print_error(f"{total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    run_all_tests()
