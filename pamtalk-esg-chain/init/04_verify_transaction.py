# -*- coding: utf-8 -*-
import os
from algosdk.v2client import algod
import json

# 설정
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
TX_ID = "GLHDBOH6ZUDGKGXJHBIXZGCKEDGO4SRVQXZN6LO4WJDE3ZFFIIIA"

HEADERS = {
    "User-Agent": "pamtalk-esg-chain"
}

def verify_tx(tx_id):
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

    try:
        print(f"[트랜잭션 조회 중] TXID: {tx_id}")
        tx_info = algod_client.pending_transaction_info(tx_id)

        print("\n[원시 트랜잭션 정보]")
        print(json.dumps(tx_info, indent=2))

        # 블록 포함 여부 확인
        if 'confirmed-round' in tx_info and tx_info['confirmed-round'] > 0:
            print(f"\n[블록 포함] Round: {tx_info['confirmed-round']}")

            # 중첩된 트랜잭션 정보 꺼내기
            inner_tx = tx_info.get("txn", {}).get("txn", {})

            sender = inner_tx.get("snd")
            receiver = inner_tx.get("arcv")
            asset_id = inner_tx.get("xaid")
            amount = inner_tx.get("aamt")

            print(f"  ▶ 송신자 지갑: {sender}")
            print(f"  ▶ 수신자 지갑: {receiver}")
            print(f"  ▶ ASA ID: {asset_id}")
            print(f"  ▶ 전송 수량: {amount}")
        else:
            print("[아직 블록에 포함되지 않음 또는 실패한 트랜잭션입니다.]")

    except Exception as e:
        print(f"[오류 발생] {str(e)}")

if __name__ == "__main__":
    verify_tx(TX_ID)
