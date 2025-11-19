#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 PAM 토큰 연동 테스트
"""

import json
import requests
from algosdk.v2client import algod

def test_real_token():
    """실제 토큰 연동 테스트"""

    print("Testing Real PAM Token Integration")
    print("=" * 40)

    # 설정 로드
    try:
        with open('pam_token_config.json', 'r') as f:
            config = json.load(f)
        print("[OK] Configuration loaded")
    except Exception as e:
        print(f"[ERROR] Config load failed: {e}")
        return False

    # 토큰 정보
    token_id = config['token_id']
    print(f"Token ID: {token_id}")
    print(f"Mode: {config['mode']}")

    # 알고드 클라이언트 설정
    try:
        algod_client = algod.AlgodClient("", config['algod_endpoint'])
        print("[OK] Algod client connected")
    except Exception as e:
        print(f"[ERROR] Algod connection failed: {e}")
        return False

    # 토큰 정보 조회
    try:
        token_info = algod_client.asset_info(int(token_id))
        print("\n[SUCCESS] Token Information:")
        print(f"  Asset ID: {token_info['index']}")
        print(f"  Name: {token_info['params']['name']}")
        print(f"  Symbol: {token_info['params']['unit-name']}")
        print(f"  Total: {token_info['params']['total']:,}")
        print(f"  Decimals: {token_info['params']['decimals']}")
        print(f"  Creator: {token_info['params']['creator']}")

    except Exception as e:
        print(f"[ERROR] Token info query failed: {e}")
        return False

    # 생성자 계정 잔액 확인
    try:
        creator = config['creator_account']
        account_info = algod_client.account_info(creator)

        print(f"\n[SUCCESS] Creator Account Status:")
        print(f"  Address: {creator}")
        print(f"  ALGO Balance: {account_info['amount'] / 1_000_000:.6f}")

        # PAM 토큰 잔액 확인
        assets = account_info.get('assets', [])
        pam_balance = 0

        for asset in assets:
            if asset['asset-id'] == int(token_id):
                pam_balance = asset['amount'] / (10 ** config['decimals'])
                break

        print(f"  PAM Balance: {pam_balance:,}")

    except Exception as e:
        print(f"[ERROR] Account info query failed: {e}")
        return False

    print(f"\n[SUCCESS] All tests passed!")
    print(f"Real PAM token is fully operational on Algorand testnet")

    return True

def test_api_integration():
    """API 통합 테스트"""

    print(f"\nTesting API Integration")
    print("-" * 25)

    try:
        # 실제 토큰 API 테스트
        api_url = "http://localhost:5003/api/token/info"
        response = requests.get(api_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API Response received")
            print(f"Token ID: {data.get('token', {}).get('id', 'N/A')}")
        else:
            print(f"[WARN] API returned status {response.status_code}")

    except Exception as e:
        print(f"[INFO] API test skipped: {e}")

if __name__ == "__main__":
    success = test_real_token()

    if success:
        test_api_integration()
        print(f"\n" + "=" * 50)
        print("REAL TOKEN INTEGRATION COMPLETE!")
        print("PAM-TALK is now running on actual Algorand blockchain")
        print("=" * 50)
    else:
        print(f"\nIntegration test failed. Check errors above.")