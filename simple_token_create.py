#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""간단한 토큰 생성 - 재시도 로직 포함"""

import sys
import json
import time
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def try_create_client():
    """다양한 엔드포인트로 클라이언트 생성 시도"""
    endpoints = [
        "https://mainnet-api.algonode.cloud",
        "https://mainnet-api.4160.nodely.io",
    ]

    for endpoint in endpoints:
        try:
            print(f"Trying endpoint: {endpoint}")
            client = algod.AlgodClient("", endpoint)
            # 연결 테스트
            status = client.status()
            print(f"✅ Connected! Network: {status.get('last-round', 'unknown')}")
            return client
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue

    return None

def check_balance(client, address):
    """잔액 확인 with retry"""
    for attempt in range(3):
        try:
            print(f"Checking balance (attempt {attempt + 1}/3)...")
            account_info = client.account_info(address)
            balance = account_info.get('amount', 0) / 1000000
            print(f"💰 Balance: {balance:.6f} ALGO")
            return balance
        except Exception as e:
            print(f"Error: {e}")
            if attempt < 2:
                time.sleep(2)
            continue
    return None

def create_token(client, private_key, asset_name, unit_name, total, decimals):
    """토큰 생성"""
    try:
        address = account.address_from_private_key(private_key)
        params = client.suggested_params()

        txn = AssetConfigTxn(
            sender=address,
            sp=params,
            total=total,
            default_frozen=False,
            unit_name=unit_name,
            asset_name=asset_name,
            manager=address,
            reserve=address,
            freeze=address,
            clawback=address,
            url="https://pam-talk.com",
            decimals=decimals
        )

        signed_txn = txn.sign(private_key)
        txid = client.send_transaction(signed_txn)

        print(f"✅ Transaction sent! ID: {txid}")
        print("Waiting for confirmation...")

        confirmed = wait_for_confirmation(client, txid, 4)
        asset_id = confirmed["asset-index"]

        print(f"🎉 Token created! Asset ID: {asset_id}")
        print(f"🔗 https://algoexplorer.io/asset/{asset_id}")

        return asset_id
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 70)
    print("PAM 토큰 생성기 (간단 버전)")
    print("=" * 70)
    print()

    # 계정 로드
    with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
        account_data = json.load(f)

    mn = account_data['mnemonic']
    private_key = mnemonic.to_private_key(mn)
    address = account.address_from_private_key(private_key)

    print(f"Address: {address}")
    print()

    # 클라이언트 생성
    client = try_create_client()
    if not client:
        print("❌ 모든 엔드포인트 연결 실패")
        return

    print()

    # 잔액 확인
    balance = check_balance(client, address)
    if balance is None:
        print("⚠️  잔액 확인 실패했지만 계속 진행합니다...")
    elif balance < 0.1:
        print(f"❌ 잔액 부족: {balance:.6f} ALGO (최소 0.1 필요)")
        return

    print()
    print("=" * 70)
    print("Creating PAM-POINT token...")
    print("=" * 70)

    asset_id = create_token(
        client,
        private_key,
        "PAM-POINT",
        "PAMP",
        1000000000,  # 10억
        2  # 소수점 2자리
    )

    if asset_id:
        result = {
            'asset_id': asset_id,
            'asset_name': 'PAM-POINT',
            'unit_name': 'PAMP',
            'creator': address
        }

        with open('pam_point_token.json', 'w') as f:
            json.dump(result, f, indent=2)

        print()
        print("✅ 정보 저장됨: pam_point_token.json")

if __name__ == "__main__":
    main()
