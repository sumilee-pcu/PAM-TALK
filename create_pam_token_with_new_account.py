#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 계정으로 PAM 토큰 생성
10 ALGO로 토큰 생성 시도
"""

import json
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation
import time

def create_pam_token():
    """새 계정으로 PAM 토큰 생성"""

    print("Creating PAM Token with New Account")
    print("=" * 40)

    # 알고드 클라이언트 설정
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient("", algod_address)

    # 계정 정보 로드
    with open('pam_algorand_account_20250928_074901.json', 'r') as f:
        account_data = json.load(f)

    creator_address = account_data['address']
    creator_private_key = account_data['private_key']

    print(f"Creator: {creator_address}")

    # 계정 정보 확인
    try:
        account_info = algod_client.account_info(creator_address)
        balance = account_info.get('amount', 0) / 1_000_000
        print(f"Balance: {balance:.6f} ALGO")

        if balance < 5:  # 토큰 생성에 최소 필요한 금액
            print("[ERROR] Insufficient balance for token creation")
            return None

    except Exception as e:
        print(f"[ERROR] Account check failed: {e}")
        return None

    # 토큰 생성 파라미터
    token_params = {
        "total": 1000000000,  # 10억 토큰
        "decimals": 3,
        "asset_name": "PAM-TALK ESG Token",
        "unit_name": "PAM",
        "url": "https://pam-talk.com",
        "metadata_hash": None,
        "default_frozen": False,
        "manager": creator_address,
        "reserve": creator_address,
        "freeze": creator_address,
        "clawback": creator_address
    }

    print("\nToken Parameters:")
    print(f"Name: {token_params['asset_name']}")
    print(f"Symbol: {token_params['unit_name']}")
    print(f"Total Supply: {token_params['total']:,}")
    print(f"Decimals: {token_params['decimals']}")

    try:
        # 네트워크 파라미터 가져오기
        params = algod_client.suggested_params()

        # 토큰 생성 트랜잭션
        txn = AssetConfigTxn(
            sender=creator_address,
            sp=params,
            total=token_params['total'],
            decimals=token_params['decimals'],
            asset_name=token_params['asset_name'],
            unit_name=token_params['unit_name'],
            url=token_params['url'],
            metadata_hash=token_params['metadata_hash'],
            default_frozen=token_params['default_frozen'],
            manager=token_params['manager'],
            reserve=token_params['reserve'],
            freeze=token_params['freeze'],
            clawback=token_params['clawback']
        )

        # 트랜잭션 서명
        signed_txn = txn.sign(creator_private_key)

        print("\nSubmitting token creation transaction...")

        # 트랜잭션 전송
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Transaction ID: {tx_id}")

        # 확인 대기
        print("Waiting for confirmation...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)

        print(f"[SUCCESS] Token created in round {confirmed_txn['confirmed-round']}")

        # 토큰 ID 가져오기
        try:
            asset_id = confirmed_txn["asset-index"]
            print(f"[SUCCESS] PAM Token ID: {asset_id}")

            # 토큰 정보 저장
            token_info = {
                "asset_id": asset_id,
                "creator": creator_address,
                "tx_id": tx_id,
                "confirmed_round": confirmed_txn['confirmed-round'],
                "created_at": time.time(),
                **token_params
            }

            filename = f"pam_token_created_{asset_id}.json"
            with open(filename, 'w') as f:
                json.dump(token_info, f, indent=2)

            print(f"\nToken info saved to: {filename}")

            # 성공 요약
            print("\n" + "=" * 50)
            print("PAM TOKEN CREATION SUCCESSFUL!")
            print("=" * 50)
            print(f"Token ID: {asset_id}")
            print(f"Name: {token_params['asset_name']}")
            print(f"Symbol: {token_params['unit_name']}")
            print(f"Total Supply: {token_params['total']:,}")
            print(f"Creator: {creator_address}")
            print(f"Transaction: {tx_id}")
            print("=" * 50)

            return asset_id

        except KeyError:
            print("[ERROR] Could not extract asset ID from transaction")
            return None

    except Exception as e:
        print(f"[ERROR] Token creation failed: {e}")
        return None

if __name__ == "__main__":
    asset_id = create_pam_token()

    if asset_id:
        print(f"\nNext Steps:")
        print(f"1. Update PAM-TALK platform with token ID: {asset_id}")
        print(f"2. Test token operations")
        print(f"3. Initialize token distribution")
    else:
        print(f"\nToken creation failed. Check errors above.")