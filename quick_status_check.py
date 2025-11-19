#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 상태 확인 스크립트 - PAM-TALK 전용
"""

import requests
import json
from datetime import datetime

def quick_check():
    """PAM-TALK 관련 주요 상태를 빠르게 확인"""

    print("PAM-TALK Quick Status Check")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # PAM-TALK 설정
    tx_id = "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
    admin_addr = "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM"
    pam_token_id = "746418487"

    # 1. 관리자 계정 잔액 확인
    print("1. Admin Account Status")
    print("-" * 25)
    try:
        url = f"https://testnet-api.algonode.cloud/v2/accounts/{admin_addr}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            balance = data.get('account', {}).get('amount', 0) / 1000000
            status = data.get('account', {}).get('status', 'Unknown')
            assets = data.get('account', {}).get('assets', [])

            print(f"Address: {admin_addr[:20]}...")
            print(f"Balance: {balance:.6f} ALGO")
            print(f"Status: {status}")
            print(f"Assets: {len(assets)} items")

            if balance > 0:
                print("✅ Account has ALGO - ready for transactions!")
            else:
                print("⚠️  Account needs ALGO funding")

        else:
            print(f"❌ Account API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Account check failed: {e}")

    print()

    # 2. 충전 트랜잭션 상태 확인
    print("2. Funding Transaction Status")
    print("-" * 30)
    try:
        url = f"https://testnet-api.algonode.cloud/v2/transactions/{tx_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            tx_data = data.get('transaction', {})
            round_num = tx_data.get('confirmed-round')
            tx_type = tx_data.get('tx-type')

            print(f"TX ID: {tx_id[:20]}...")
            print(f"Status: ✅ CONFIRMED")
            print(f"Round: {round_num}")
            print(f"Type: {tx_type}")

            # 결제 정보
            if 'payment-transaction' in tx_data:
                payment = tx_data['payment-transaction']
                amount = payment.get('amount', 0) / 1000000
                receiver = payment.get('receiver', '')
                print(f"Amount: {amount:.6f} ALGO")
                print(f"To: {receiver[:20]}...")

        elif response.status_code == 404:
            print(f"TX ID: {tx_id[:20]}...")
            print("Status: ⏳ PENDING (not yet on blockchain)")
            print("Note: Transaction may still be processing")

        else:
            print(f"❌ Transaction API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Transaction check failed: {e}")

    print()

    # 3. PAM 토큰 상태 확인
    print("3. PAM Token Status")
    print("-" * 20)
    try:
        url = f"https://testnet-api.algonode.cloud/v2/assets/{pam_token_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            asset_data = data.get('asset', {})
            params = asset_data.get('params', {})

            print(f"Token ID: {pam_token_id}")
            print(f"Name: {params.get('name', 'N/A')}")
            print(f"Total: {params.get('total', 0):,}")
            print(f"Decimals: {params.get('decimals', 0)}")
            print(f"Creator: {params.get('creator', 'N/A')[:20]}...")

            if params.get('total', 0) > 0:
                print("✅ PAM Token exists and active")
            else:
                print("⚠️  PAM Token data incomplete")

        else:
            print(f"Token ID: {pam_token_id}")
            print("Status: ❌ Token not found or inactive")
            print("Action needed: Re-create PAM token")
    except Exception as e:
        print(f"❌ Token check failed: {e}")

    print()

    # 4. 다음 단계 추천
    print("4. Recommended Next Steps")
    print("-" * 26)

    # 계정 잔액 다시 확인
    try:
        url = f"https://testnet-api.algonode.cloud/v2/accounts/{admin_addr}"
        response = requests.get(url, timeout=5)
        balance = 0
        if response.status_code == 200:
            data = response.json()
            balance = data.get('account', {}).get('amount', 0) / 1000000
    except:
        balance = 0

    if balance >= 1.0:
        print("🚀 Ready to create PAM token!")
        print("   Command: python pamtalk-esg-chain/step2_create_token.py")
    elif balance > 0:
        print("⚠️  Low ALGO balance, but might be enough")
        print("   Try: python pamtalk-esg-chain/step2_create_token.py")
    else:
        print("💰 Need more ALGO funding")
        print("   Action: Visit https://bank.testnet.algorand.network/")
        print("   Or try: Triangle Platform faucet")

    print()
    print("=" * 40)
    print("✅ Quick status check completed")

if __name__ == "__main__":
    quick_check()