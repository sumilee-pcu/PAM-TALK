#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인넷 토큰 검증 스크립트
AlgoExplorer가 다운된 경우 API로 직접 확인
"""

import sys
import json
from algosdk.v2client import algod, indexer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 메인넷 설정
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
ALGOD_TOKEN = ""
INDEXER_ADDRESS = "https://mainnet-idx.algonode.cloud"
INDEXER_TOKEN = ""

def verify_asset(asset_id):
    """토큰 정보 확인"""
    try:
        # Algod 클라이언트로 에셋 정보 조회
        algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        asset_info = algod_client.asset_info(asset_id)

        params = asset_info['params']

        print("=" * 70)
        print(f"토큰 정보 확인 - Asset ID: {asset_id}")
        print("=" * 70)
        print()
        print(f"✅ 토큰명: {params.get('name', 'N/A')}")
        print(f"✅ 단위명: {params.get('unit-name', 'N/A')}")
        print(f"✅ 총 발행량: {params.get('total', 0):,}")
        print(f"✅ 소수점: {params.get('decimals', 0)}")
        print(f"✅ 생성자: {params.get('creator', 'N/A')}")
        print(f"✅ URL: {params.get('url', 'N/A')}")
        print()

        # Indexer로 추가 정보 조회
        try:
            indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ADDRESS)
            txns = indexer_client.search_asset_transactions(
                asset_id=asset_id,
                limit=1,
                txn_type='acfg'
            )

            if txns.get('transactions'):
                first_txn = txns['transactions'][0]
                print(f"✅ 생성 트랜잭션 ID: {first_txn.get('id', 'N/A')}")
                print(f"✅ 생성 시각: Round {first_txn.get('confirmed-round', 'N/A')}")
                print()
        except Exception as e:
            print(f"⚠️  Indexer 정보 조회 실패: {e}")
            print()

        print("=" * 70)
        print("✅ 토큰이 메인넷에 정상적으로 존재합니다!")
        print(f"탐색기 (복구 시): https://algoexplorer.io/asset/{asset_id}")
        print(f"대체 탐색기: https://allo.info/asset/{asset_id}")
        print(f"PeraExplorer: https://explorer.perawallet.app/asset/{asset_id}")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False

def verify_account_assets(address):
    """계정이 보유한 에셋 목록 확인"""
    try:
        algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        account_info = algod_client.account_info(address)

        created_assets = account_info.get('created-assets', [])

        print("\n" + "=" * 70)
        print(f"계정이 생성한 토큰 목록: {address}")
        print("=" * 70)
        print()

        if not created_assets:
            print("생성한 토큰이 없습니다.")
            return

        for idx, asset in enumerate(created_assets, 1):
            asset_id = asset.get('index')
            params = asset.get('params', {})
            print(f"{idx}. Asset ID: {asset_id}")
            print(f"   이름: {params.get('name', 'N/A')}")
            print(f"   단위: {params.get('unit-name', 'N/A')}")
            print(f"   총량: {params.get('total', 0):,}")
            print()

        print("=" * 70)

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    # PAM-POINT 토큰 검증
    print("\n🔍 PAM-POINT 토큰 검증 중...\n")
    verify_asset(3330375002)

    # 계정의 모든 생성 토큰 확인
    creator_address = "PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE"
    verify_account_assets(creator_address)
