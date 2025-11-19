#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹사이트용 디지털 쿠폰 토큰 생성 API
사용자가 웹에서 요청하면 자동으로 토큰 생성/지급
"""

import sys
import json
import requests
import base64
from datetime import datetime
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 직접 API 호출용 설정
API_BASE = "https://mainnet-api.algonode.cloud/v2"
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
ALGOD_TOKEN = ""

class AlgorandTokenAPI:
    """웹사이트에서 사용할 토큰 생성/지급 API"""

    def __init__(self, master_mnemonic):
        """
        마스터 계정으로 초기화
        Args:
            master_mnemonic: 토큰 발행용 마스터 계정의 25단어 니모닉
        """
        self.private_key = mnemonic.to_private_key(master_mnemonic)
        self.address = account.address_from_private_key(self.private_key)
        self.algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

        print(f"Master Account: {self.address}")
        self._check_balance()

    def _check_balance(self):
        """마스터 계정 잔액 확인 (direct API)"""
        try:
            url = f"{API_BASE}/accounts/{self.address}"
            headers = {'User-Agent': 'PAM-Token-API/1.0'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                balance = data.get('amount', 0) / 1000000
                print(f"Master Balance: {balance:.6f} ALGO")
                return balance
            else:
                print(f"Warning: Cannot check balance (HTTP {response.status_code})")
                return None
        except Exception as e:
            print(f"Warning: Balance check failed: {e}")
            return None

    def create_token(self, token_name, unit_name, total_supply, decimals=0, url=""):
        """
        새로운 토큰 생성

        Args:
            token_name: 토큰 이름 (예: "PAM-POINT")
            unit_name: 토큰 단위 (예: "PAMP", 최대 8자)
            total_supply: 총 발행량
            decimals: 소수점 자리수 (0~6)
            url: 토큰 정보 URL

        Returns:
            dict: {'success': bool, 'asset_id': int, 'txid': str, ...}
        """
        try:
            print(f"\n토큰 생성 중: {token_name}")

            # 트랜잭션 파라미터 가져오기
            params = self.algod_client.suggested_params()

            # Asset Configuration Transaction 생성
            txn = transaction.AssetConfigTxn(
                sender=self.address,
                sp=params,
                total=total_supply,
                default_frozen=False,
                unit_name=unit_name[:8],  # 최대 8자
                asset_name=token_name[:32],  # 최대 32자
                manager=self.address,
                reserve=self.address,
                freeze=self.address,
                clawback=self.address,
                url=url[:96],  # 최대 96자
                decimals=decimals
            )

            # 서명
            signed_txn = txn.sign(self.private_key)

            # 전송
            txid = self.algod_client.send_transaction(signed_txn)
            print(f"Transaction ID: {txid}")

            # 확인 대기
            print("Waiting for confirmation...")
            confirmed_txn = transaction.wait_for_confirmation(self.algod_client, txid, 4)

            asset_id = confirmed_txn.get("asset-index")

            print(f"✅ 토큰 생성 성공!")
            print(f"   Asset ID: {asset_id}")
            print(f"   Explorer: https://algoexplorer.io/asset/{asset_id}")

            return {
                'success': True,
                'asset_id': asset_id,
                'asset_name': token_name,
                'unit_name': unit_name,
                'total_supply': total_supply,
                'txid': txid,
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ 토큰 생성 실패: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e),
                'asset_name': token_name
            }

    def transfer_token(self, asset_id, recipient_address, amount):
        """
        토큰 전송 (사용자에게 쿠폰 지급)

        Args:
            asset_id: 토큰 Asset ID
            recipient_address: 받는 사람 알고랜드 주소
            amount: 전송할 수량

        Returns:
            dict: {'success': bool, 'txid': str, ...}
        """
        try:
            print(f"\n토큰 전송 중...")
            print(f"  Asset ID: {asset_id}")
            print(f"  To: {recipient_address}")
            print(f"  Amount: {amount}")

            params = self.algod_client.suggested_params()

            # Asset Transfer Transaction
            txn = transaction.AssetTransferTxn(
                sender=self.address,
                sp=params,
                receiver=recipient_address,
                amt=amount,
                index=asset_id
            )

            signed_txn = txn.sign(self.private_key)
            txid = self.algod_client.send_transaction(signed_txn)

            print(f"Transaction ID: {txid}")
            print("Waiting for confirmation...")

            transaction.wait_for_confirmation(self.algod_client, txid, 4)

            print(f"✅ 전송 성공!")

            return {
                'success': True,
                'txid': txid,
                'asset_id': asset_id,
                'recipient': recipient_address,
                'amount': amount
            }

        except Exception as e:
            print(f"❌ 전송 실패: {e}")

            return {
                'success': False,
                'error': str(e)
            }


def main():
    """테스트용 메인 함수"""
    print("=" * 70)
    print("PAM 디지털 쿠폰 토큰 생성 API")
    print("=" * 70)
    print()

    # 마스터 계정 로드
    with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
        account_data = json.load(f)

    master_mnemonic = account_data['mnemonic']

    # API 초기화
    api = AlgorandTokenAPI(master_mnemonic)
    print()

    # PAM-POINT 토큰 생성
    print("=" * 70)
    print("1. PAM-POINT 토큰 생성")
    print("=" * 70)

    result = api.create_token(
        token_name="PAM-POINT",
        unit_name="PAMP",
        total_supply=1000000000,  # 10억 포인트
        decimals=2,  # 0.01 단위
        url="https://pam-talk.com/point"
    )

    if result['success']:
        # 결과 저장
        with open('pam_point_token_info.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print()
        print(f"✅ 토큰 정보 저장: pam_point_token_info.json")
        print()
        print("=" * 70)
        print("다음 단계:")
        print("1. Asset ID를 웹사이트 설정에 저장")
        print("2. 사용자에게 토큰 지급 시 transfer_token() 함수 사용")
        print("=" * 70)
    else:
        print()
        print("❌ 토큰 생성 실패")
        print("상세 정보:", result)


if __name__ == "__main__":
    main()
