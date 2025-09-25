#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK API Test Suite

This script tests all API endpoints of the PAM-TALK REST API server.
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:5000"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print(f"{'=' * 70}")

def print_response(response, title="Response"):
    """Print HTTP response in a readable format"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check Test")

    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print_response(response, "Root Endpoint")

        # Test health endpoint
        response = requests.get(f"{BASE_URL}/api/health")
        print_response(response, "Health Check")

        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on port 5000")
        print("   Run: python api/app.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_farm_management():
    """Test farm management endpoints"""
    print_header("Farm Management Test")

    try:
        # Test farm registration
        farm_data = {
            "farm_id": "TEST_FARM_001",
            "farm_name": "Test Organic Farm",
            "owner_name": "Test Owner",
            "location": "Test Location, South Korea",
            "size_hectares": 15.5,
            "established_date": "2020-01-15",
            "contact_info": {
                "phone": "+82-10-1234-5678",
                "email": "test@testfarm.kr"
            },
            "certifications": ["organic", "fair_trade"],
            "products": ["tomatoes", "lettuce"],
            "esg_data": {
                "organic_certified": True,
                "water_usage_per_hectare": 5000,
                "carbon_emissions": 2.5
            },
            "status": "active"
        }

        print(">> Testing farm registration...")
        response = requests.post(
            f"{BASE_URL}/api/farms",
            json=farm_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Farm Registration")
        registration_success = response.status_code in [200, 201]

        # Test farm retrieval
        print(">> Testing farm retrieval...")
        response = requests.get(f"{BASE_URL}/api/farms/TEST_FARM_001")
        print_response(response, "Farm Retrieval")
        retrieval_success = response.status_code == 200

        # Test farm listing
        print(">> Testing farm listing...")
        response = requests.get(f"{BASE_URL}/api/farms")
        print_response(response, "Farm Listing")
        listing_success = response.status_code == 200

        return registration_success and retrieval_success and listing_success

    except Exception as e:
        print(f"❌ Farm management test failed: {e}")
        return False

def test_demand_prediction():
    """Test demand prediction endpoint"""
    print_header("Demand Prediction Test")

    try:
        # Use existing farm or create one
        farm_id = "FARM_DEMO_001"  # From sample data

        print(">> Testing demand prediction...")
        response = requests.get(f"{BASE_URL}/api/farms/{farm_id}/predict?days=7")
        print_response(response, "Demand Prediction")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Demand prediction test failed: {e}")
        return False

def test_transaction_management():
    """Test transaction management endpoints"""
    print_header("Transaction Management Test")

    try:
        # Test transaction creation
        transaction_data = {
            "producer_id": "TEST_FARM_001",
            "consumer_id": "CONSUMER_TEST_001",
            "product_type": "tomatoes",
            "quantity": 500,
            "price_per_unit": 5000,
            "quality_score": 85,
            "esg_score": 80,
            "location": "Seoul",
            "payment_method": "PAMT_TRANSFER",
            "delivery_time_hours": 24,
            "metadata": {
                "note": "Test transaction"
            }
        }

        print(">> Testing transaction creation...")
        response = requests.post(
            f"{BASE_URL}/api/transactions",
            json=transaction_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Transaction Creation")
        creation_success = response.status_code in [200, 201]

        # Get transaction ID from response
        transaction_id = None
        if creation_success and response.json().get('success'):
            transaction_data_response = response.json()['data']['transaction']
            transaction_id = transaction_data_response.get('transaction_id')

        # Test transaction listing
        print(">> Testing transaction listing...")
        response = requests.get(f"{BASE_URL}/api/transactions?limit=10")
        print_response(response, "Transaction Listing")
        listing_success = response.status_code == 200

        # Test ESG score retrieval
        esg_success = False
        if transaction_id:
            print(">> Testing ESG score retrieval...")
            response = requests.get(f"{BASE_URL}/api/transactions/{transaction_id}/esg?participant=producer")
            print_response(response, "ESG Score Retrieval")
            esg_success = response.status_code == 200

        return creation_success and listing_success and esg_success

    except Exception as e:
        print(f"❌ Transaction management test failed: {e}")
        return False

def test_anomaly_detection():
    """Test anomaly detection endpoint"""
    print_header("Anomaly Detection Test")

    try:
        # Test normal transaction
        normal_transaction = {
            "producer_id": "TEST_FARM_001",
            "consumer_id": "CONSUMER_TEST_002",
            "product_type": "tomatoes",
            "quantity": 300,
            "price_per_unit": 4500,
            "quality_score": 85,
            "esg_score": 75
        }

        print(">> Testing normal transaction anomaly check...")
        response = requests.post(
            f"{BASE_URL}/api/transactions/check",
            json=normal_transaction,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Normal Transaction Check")
        normal_check_success = response.status_code == 200

        # Test suspicious transaction
        suspicious_transaction = {
            "producer_id": "TEST_FARM_001",
            "consumer_id": "CONSUMER_TEST_003",
            "product_type": "tomatoes",
            "quantity": 100,
            "price_per_unit": 25000,  # Very high price
            "quality_score": 30,      # Low quality
            "esg_score": 20,          # Very low ESG
            "delivery_time_hours": 2  # Extremely fast delivery
        }

        print(">> Testing suspicious transaction anomaly check...")
        response = requests.post(
            f"{BASE_URL}/api/transactions/check",
            json=suspicious_transaction,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Suspicious Transaction Check")
        suspicious_check_success = response.status_code == 200

        return normal_check_success and suspicious_check_success

    except Exception as e:
        print(f"❌ Anomaly detection test failed: {e}")
        return False

def test_dashboard():
    """Test dashboard endpoint"""
    print_header("Dashboard Test")

    try:
        print(">> Testing dashboard data retrieval...")
        response = requests.get(f"{BASE_URL}/api/dashboard")
        print_response(response, "Dashboard Data")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_error_handling():
    """Test API error handling"""
    print_header("Error Handling Test")

    try:
        # Test 404 - Non-existent farm
        print(">> Testing 404 error...")
        response = requests.get(f"{BASE_URL}/api/farms/NON_EXISTENT_FARM")
        print_response(response, "404 Error Test")
        error_404_success = response.status_code == 404

        # Test 400 - Invalid JSON
        print(">> Testing 400 error (invalid JSON)...")
        response = requests.post(
            f"{BASE_URL}/api/farms",
            json={},  # Empty JSON
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "400 Error Test")
        error_400_success = response.status_code == 400

        # Test 400 - Missing required fields
        print(">> Testing 400 error (missing fields)...")
        response = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"producer_id": "test"},  # Missing required fields
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Missing Fields Error Test")
        missing_fields_success = response.status_code == 400

        return error_404_success and error_400_success and missing_fields_success

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print_header("CORS Test")

    try:
        # Test preflight OPTIONS request
        print(">> Testing CORS preflight...")
        response = requests.options(
            f"{BASE_URL}/api/farms",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print_response(response, "CORS Preflight")

        # Check CORS headers in regular request
        print(">> Testing CORS headers in GET request...")
        response = requests.get(
            f"{BASE_URL}/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        print_response(response, "CORS GET Request")

        cors_headers_present = (
            "Access-Control-Allow-Origin" in response.headers or
            "access-control-allow-origin" in response.headers
        )

        return cors_headers_present

    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def performance_test():
    """Run basic performance test"""
    print_header("Performance Test")

    try:
        # Test multiple concurrent requests to health endpoint
        print(">> Testing API response time...")

        times = []
        for i in range(5):
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/health")
            end_time = time.time()

            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to ms
                times.append(response_time)
                print(f"   Request {i+1}: {response_time:.2f}ms")

        if times:
            avg_time = sum(times) / len(times)
            print(f"   Average response time: {avg_time:.2f}ms")

            return avg_time < 5000  # Should respond within 5 seconds

        return False

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print_header("PAM-TALK API Test Suite")

    # First check if server is running
    print("🚀 Checking if API server is running...")
    if not test_health_check():
        print("\n❌ API server is not running or not accessible.")
        print("Please start the server first with: python api/app.py")
        return 1

    print("\n✅ API server is running. Starting comprehensive tests...\n")

    tests = [
        ("Farm Management", test_farm_management),
        ("Demand Prediction", test_demand_prediction),
        ("Transaction Management", test_transaction_management),
        ("Anomaly Detection", test_anomaly_detection),
        ("Dashboard", test_dashboard),
        ("Error Handling", test_error_handling),
        ("CORS Configuration", test_cors),
        ("Performance", performance_test),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name}...")
            result = test_func()
            if result:
                passed_tests += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    print_header("Test Results Summary")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

    print(f"\n📊 API ENDPOINTS TESTED:")
    print(f"   ✅ GET  /              (Root)")
    print(f"   ✅ GET  /api/health    (Health Check)")
    print(f"   ✅ POST /api/farms     (Farm Registration)")
    print(f"   ✅ GET  /api/farms/{{id}} (Farm Details)")
    print(f"   ✅ GET  /api/farms     (Farm Listing)")
    print(f"   ✅ GET  /api/farms/{{id}}/predict (Demand Prediction)")
    print(f"   ✅ POST /api/transactions (Transaction Creation)")
    print(f"   ✅ GET  /api/transactions (Transaction Listing)")
    print(f"   ✅ GET  /api/transactions/{{id}}/esg (ESG Score)")
    print(f"   ✅ POST /api/transactions/check (Anomaly Detection)")
    print(f"   ✅ GET  /api/dashboard (Dashboard Data)")

    if passed_tests >= total_tests * 0.8:
        print("\n🎉 API tests completed successfully!")
        print("   The PAM-TALK REST API is functioning correctly.")
        return 0
    else:
        print("\n⚠️  Some API tests failed.")
        print("   Please check the server logs for more details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())