#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM 디지털 쿠폰 토큰 자동 생성 (메인넷)
포인트 + 교환권 둘 다 자동 생성
"""

import sys
import json
from datetime import datetime
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 메인넷 설정 - Alternative API endpoints
ALGOD_ENDPOINTS = [
    ("https://mainnet-api.algonode.cloud", ""),
    ("https://mainnet-idx.algonode.cloud", ""),
]

# 첫 번째 엔드포인트로 시작
ALGOD_ADDRESS = ALGOD_ENDPOINTS[0][0]
ALGOD_TOKEN = ALGOD_ENDPOINTS[0][1]

class DigitalCouponCreator:
    def __init__(self, account_mnemonic):
        """디지털 쿠폰 생성기 초기화"""
        self.algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        self.private_key = mnemonic.to_private_key(account_mnemonic)
        self.address = account.address_from_private_key(self.private_key)

        print(f"Creator Address: {self.address}")
        self._check_balance()

    def _check_balance(self):
        """계정 잔액 확인"""
        try:
            account_info = self.algod_client.account_info(self.address)
            balance = account_info.get('amount', 0) / 1000000
            print(f"Balance: {balance:.6f} ALGO")

            if balance < 0.1:
                print("⚠️  Warning: Low balance. Need at least 0.1 ALGO for token creation.")
                return False
            return True
        except Exception as e:
            print(f"Error checking balance: {e}")
            return False

    def create_asset(self, asset_name, unit_name, total, decimals, url, note):
        """ASA 토큰 생성"""
        try:
            params = self.algod_client.suggested_params()

            txn = AssetConfigTxn(
                sender=self.address,
                sp=params,
                total=total,
                default_frozen=False,
                unit_name=unit_name,
                asset_name=asset_name,
                manager=self.address,
                reserve=self.address,
                freeze=self.address,
                clawback=self.address,
                url=url,
                decimals=decimals,
                note=note.encode()
            )

            # 서명 및 전송
            signed_txn = txn.sign(self.private_key)
            txid = self.algod_client.send_transaction(signed_txn)

            print(f"\nCreating {asset_name}...")
            print(f"Transaction ID: {txid}")
            print("Waiting for confirmation...")

            # 확인 대기
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            asset_id = confirmed_txn["asset-index"]

            print(f"✅ Success! Asset ID: {asset_id}")
            print(f"🔗 Explorer: https://algoexplorer.io/asset/{asset_id}")

            return {
                'success': True,
                'asset_id': asset_id,
                'asset_name': asset_name,
                'unit_name': unit_name,
                'total_supply': total,
                'decimals': decimals,
                'txid': txid,
                'url': url,
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error creating asset: {e}")
            return {
                'success': False,
                'error': str(e),
                'asset_name': asset_name
            }

def main():
    print("=" * 70)
    print("PAM 디지털 쿠폰 토큰 자동 생성기 (메인넷)")
    print("포인트 + 교환권 결합 시스템")
    print("=" * 70)
    print()

    # 니모닉 파일 로드
    try:
        with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
            account_data = json.load(f)

        account_mnemonic = account_data.get('mnemonic')

        if not account_mnemonic:
            print("❌ Error: No mnemonic found in account file")
            return
    except FileNotFoundError:
        print("❌ Error: pam_mainnet_account_20251116_181939.json not found")
        return

    # 토큰 생성기 초기화
    creator = DigitalCouponCreator(account_mnemonic)
    print()

    results = []

    # PAM-POINT 토큰 생성
    print("=" * 70)
    print("1/2: Creating PAM-POINT Token...")
    print("=" * 70)
    result = creator.create_asset(
        asset_name="PAM-POINT",
        unit_name="PAMP",
        total=1000000000,  # 10억 포인트
        decimals=2,  # 0.01 포인트 단위
        url="https://pam-talk.com/point",
        note="PAM Point Token - Earnable and Redeemable Points"
    )
    results.append(result)

    if not result.get('success'):
        print("\n⚠️  PAM-POINT 생성 실패. 계속하시겠습니까?")
        print("계속하려면 Enter, 중단하려면 Ctrl+C")
        # 자동 진행
        print("자동으로 계속 진행합니다...")

    # PAM-VOUCHER 토큰 생성
    print("\n" + "=" * 70)
    print("2/2: Creating PAM-VOUCHER Token...")
    print("=" * 70)

    voucher_note = json.dumps({
        "type": "voucher",
        "voucher_type": "PRODUCT",
        "value": 10000,
        "redeemable": True
    })

    result = creator.create_asset(
        asset_name="PAM-VOUCHER",
        unit_name="PAMV",
        total=100000,  # 10만 개
        decimals=0,  # 교환권은 정수 단위
        url="https://pam-talk.com/voucher",
        note=voucher_note
    )
    results.append(result)

    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pam_tokens_created_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'creator_address': creator.address,
            'network': 'mainnet',
            'tokens': results,
            'created_at': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("토큰 생성 완료!")
    print("=" * 70)
    print(f"\n📄 Token information saved to: {filename}")

    # 성공한 토큰 요약
    successful_tokens = [r for r in results if r.get('success')]
    failed_tokens = [r for r in results if not r.get('success')]

    if successful_tokens:
        print(f"\n✅ 성공적으로 생성된 토큰: {len(successful_tokens)}개")
        for token in successful_tokens:
            print(f"   - {token['asset_name']} (ID: {token['asset_id']})")

    if failed_tokens:
        print(f"\n❌ 실패한 토큰: {len(failed_tokens)}개")
        for token in failed_tokens:
            print(f"   - {token['asset_name']}: {token.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
