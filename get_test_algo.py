#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알고랜드 테스트 ALGO 자동 충전 스크립트
"""

import requests
import time

def check_balance(address):
    """계정 잔액 확인"""
    api_url = f'https://testnet-api.algonode.cloud/v2/accounts/{address}'

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get('account', {}).get('amount', 0)
            return balance / 1000000  # microALGO to ALGO
        else:
            print(f"API 오류: {response.status_code}")
            return 0
    except Exception as e:
        print(f"연결 오류: {e}")
        return 0

def request_test_algo(address):
    """테스트 ALGO 요청 (자동화 시도)"""
    dispenser_urls = [
        'https://bank.testnet.algorand.network/',
        'https://testnet.algoexplorer.io/dispenser'
    ]

    print(f"계정 주소: {address}")
    print("\n테스트 ALGO 충전 방법:")
    print("="*50)

    for i, url in enumerate(dispenser_urls, 1):
        print(f"{i}. {url}")
        print(f"   위 사이트에서 다음 주소로 테스트 ALGO를 요청하세요:")
        print(f"   {address}")
        print()

    print("충전 후 잔액 확인을 위해 아무 키나 누르세요...")
    input()

    return check_balance(address)

def main():
    # PAM-TALK 관리자 계정
    admin_address = "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM"

    print("PAM-TALK 알고랜드 테스트 ALGO 충전 도구")
    print("="*50)

    # 현재 잔액 확인
    print("1. 현재 잔액 확인 중...")
    current_balance = check_balance(admin_address)
    print(f"   현재 잔액: {current_balance:.6f} ALGO")

    if current_balance >= 1.0:
        print("✅ 충분한 ALGO가 있습니다! (1 ALGO 이상)")
        return

    print(f"⚠️  ALGO 부족 ({current_balance:.6f} ALGO < 1.0 ALGO)")
    print("2. 테스트 ALGO 충전이 필요합니다.")

    # 테스트 ALGO 요청
    new_balance = request_test_algo(admin_address)
    print(f"충전 후 잔액: {new_balance:.6f} ALGO")

    if new_balance > current_balance:
        print("✅ 테스트 ALGO 충전 성공!")
        print(f"충전량: {new_balance - current_balance:.6f} ALGO")
    else:
        print("❌ 충전이 확인되지 않았습니다.")
        print("몇 분 후 다시 시도해보세요.")

if __name__ == "__main__":
    main()