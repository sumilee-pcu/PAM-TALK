#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API 테스트 스크립트"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    print("1. Health Check")
    r = requests.get(f"{BASE_URL}/api/health")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    print()

def test_token_info():
    print("2. Token Info")
    r = requests.get(f"{BASE_URL}/api/token-info")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
    print()

def test_balance():
    print("3. Master Account Balance")
    r = requests.get(f"{BASE_URL}/api/balance")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    print()

def test_check_opt_in(address):
    print(f"4. Check Opt-in for {address}")
    r = requests.post(
        f"{BASE_URL}/api/check-opt-in",
        json={"user_address": address}
    )
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    print()

def test_give_coupon(address, amount):
    print(f"5. Give Coupon: {amount} to {address}")
    r = requests.post(
        f"{BASE_URL}/api/give-coupon",
        json={
            "user_address": address,
            "amount": amount
        }
    )
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 70)
    print("PAM API Test")
    print("=" * 70)
    print()
    
    test_health()
    test_token_info()
    test_balance()
    
    # 테스트용 주소 (본인의 다른 주소로 변경하세요)
    test_address = input("Enter test address (or press Enter to skip): ").strip()
    
    if test_address:
        test_check_opt_in(test_address)
        
        confirm = input("Send 100.00 PAMP to this address? (y/n): ").strip().lower()
        if confirm == 'y':
            test_give_coupon(test_address, 10000)  # 100.00 PAMP
    
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)
