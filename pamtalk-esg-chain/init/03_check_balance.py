# -*- coding: utf-8 -*-
import os
from algosdk.v2client import algod

# Algorand 테스트넷 API 설정 (변경 가능)
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # 공용 API이므로 토큰 없음
ASA_ID = 742923555  # <- 여기에 고정된 ASA ID 입력

# 지갑 주소 예시 (바꿔서 테스트)
TARGET_ADDRESS = "LYFTWC7AFPROJBZBY3Z6XMLE7IRLWY6B7ICHUS4FA5RPCQMVXTUKT2CS6M"

# 클라이언트 생성
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def get_token_balance(address: str, asset_id: int):
    try:
        account_info = algod_client.account_info(address)
        for asset in account_info.get("assets", []):
            if asset["asset-id"] == asset_id:
                return asset["amount"]
        return 0  # 해당 자산 없음
    except Exception as e:
        print(f"잔액 조회 실패: {e}")
        return None

if __name__ == "__main__":
    balance = get_token_balance(TARGET_ADDRESS, ASA_ID)
    if balance is not None:
        print(f"[조회 성공] 지갑 주소: {TARGET_ADDRESS}")
        print(f"→ ASA({ASA_ID}) 보유 수량: {balance}")
    else:
        print("잔액 조회 실패")
