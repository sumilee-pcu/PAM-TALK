#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM 디지털 쿠폰 토큰 생성 (메인넷)
포인트 + 교환권 결합 시스템
"""

import sys
import json
from datetime import datetime
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 메인넷 설정
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
ALGOD_TOKEN = ""

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
                print("Warning: Low balance. Need at least 0.1 ALGO for token creation.")
                return False
            return True
        except Exception as e:
            print(f"Error checking balance: {e}")
            return False

    def create_point_token(self,
                          token_name="PAM-POINT",
                          unit_name="PAMP",
                          total_supply=1000000000,
                          decimals=2,
                          url="https://pam-talk.com/point"):
        """
        포인트 토큰 생성

        Args:
            token_name: 토큰 이름
            unit_name: 토큰 단위 (6자 이하)
            total_supply: 총 발행량 (소수점 포함)
            decimals: 소수점 자리수 (0=정수, 2=0.01단위)
            url: 토큰 정보 URL
        """
        return self._create_asset(
            asset_name=token_name,
            unit_name=unit_name,
            total=total_supply,
            decimals=decimals,
            url=url,
            note="PAM Point Token - Earnable and Redeemable Points"
        )

    def create_voucher_token(self,
                            voucher_name="PAM-VOUCHER",
                            unit_name="PAMV",
                            total_supply=100000,
                            voucher_type="PRODUCT",
                            value=10000,
                            url="https://pam-talk.com/voucher"):
        """
        교환권 토큰 생성

        Args:
            voucher_name: 교환권 이름
            unit_name: 교환권 단위
            total_supply: 총 발행량
            voucher_type: 교환권 타입 (PRODUCT, SERVICE, DISCOUNT)
            value: 교환 가치 (포인트 또는 원화)
            url: 교환권 정보 URL
        """
        note_data = {
            "type": "voucher",
            "voucher_type": voucher_type,
            "value": value,
            "redeemable": True
        }

        return self._create_asset(
            asset_name=voucher_name,
            unit_name=unit_name,
            total=total_supply,
            decimals=0,  # 교환권은 정수 단위
            url=url,
            note=json.dumps(note_data)
        )

    def _create_asset(self, asset_name, unit_name, total, decimals, url, note):
        """ASA 토큰 생성 (내부 메서드)"""
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

            print(f"Success! Asset ID: {asset_id}")
            print(f"Explorer: https://algoexplorer.io/asset/{asset_id}")

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
            print(f"Error creating asset: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    print("=" * 70)
    print("PAM 디지털 쿠폰 토큰 생성기 (메인넷)")
    print("포인트 + 교환권 결합 시스템")
    print("=" * 70)
    print()

    # 니모닉 파일 로드
    try:
        with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
            account_data = json.load(f)

        account_mnemonic = account_data.get('mnemonic')

        if not account_mnemonic:
            print("Error: No mnemonic found in account file")
            return
    except FileNotFoundError:
        print("Error: pam_mainnet_account_20251116_181939.json not found")
        return

    # 토큰 생성기 초기화
    creator = DigitalCouponCreator(account_mnemonic)
    print()

    # 생성할 토큰 선택
    print("Which token would you like to create?")
    print("1. PAM-POINT (포인트 토큰)")
    print("2. PAM-VOUCHER (교환권 토큰)")
    print("3. Both (둘 다)")
    print()

    choice = input("Select (1/2/3): ").strip()

    results = []

    if choice in ['1', '3']:
        print("\n" + "=" * 70)
        print("Creating PAM-POINT Token...")
        print("=" * 70)
        result = creator.create_point_token(
            token_name="PAM-POINT",
            unit_name="PAMP",
            total_supply=1000000000,  # 10억 포인트
            decimals=2,  # 0.01 포인트 단위
            url="https://pam-talk.com/point"
        )
        results.append(result)

    if choice in ['2', '3']:
        print("\n" + "=" * 70)
        print("Creating PAM-VOUCHER Token...")
        print("=" * 70)
        result = creator.create_voucher_token(
            voucher_name="PAM-VOUCHER",
            unit_name="PAMV",
            total_supply=100000,  # 10만 개
            voucher_type="PRODUCT",
            value=10000,  # 10,000 포인트 교환 가치
            url="https://pam-talk.com/voucher"
        )
        results.append(result)

    # 결과 저장
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pam_tokens_created_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'creator_address': creator.address,
                'network': 'mainnet',
                'tokens': results,
                'created_at': datetime.now().isoformat()
            }, f, indent=2)

        print("\n" + "=" * 70)
        print(f"Token information saved to: {filename}")
        print("=" * 70)

if __name__ == "__main__":
    main()
