# -*- coding: utf-8 -*-
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn
from app.config import ALGOD_ADDRESS, ALGOD_TOKEN, ALGOD_HEADERS
from app.config import HCF_ADDRESS, HCF_MNEMONIC

# Algorand 클라이언트 생성
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, ALGOD_HEADERS)

# HCF 니모닉을 통해 개인키 생성
HCF_PRIVATE_KEY = mnemonic.to_private_key(HCF_MNEMONIC)

# 트랜잭션이 블록에 포함될 때까지 대기하는 함수
def wait_for_confirmation(client, txid, timeout=10):
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get("confirmed-round", 0) > 0:
                print("블록 포함 완료 - 라운드:", pending_txn["confirmed-round"])
                return pending_txn
            else:
                print("⏳ 블록에 포함될 때까지 대기 중...")
                client.status_after_block(current_round)
                current_round += 1
        except Exception as e:
            raise Exception(f"블록 확인 중 오류 발생: {str(e)}")
    raise Exception("트랜잭션이 시간 내에 확인되지 않았습니다.")

# ESG 토큰 생성 함수
def create_hcf_token():
    print("HCF ESG 토큰을 생성합니다...")

    # 네트워크 파라미터 조회
    params = algod_client.suggested_params()

    # ASA(Algorand Standard Asset) 생성 트랜잭션 구성
    txn = AssetConfigTxn(
        sender=HCF_ADDRESS,            # 발행자 주소
        sp=params,
        total=1_000_000,               # 총 발행량: 100만 개
        decimals=0,                    # 소수점 없음
        default_frozen=False,          # 기본 잠금 상태 아님
        unit_name="ESG",               # 단위 이름
        asset_name="HCF ESG Token",    # 자산 전체 이름
        manager=HCF_ADDRESS,           # 매니저 권한 (HCF)
        reserve=HCF_ADDRESS,           # 리저브 주소
        freeze=HCF_ADDRESS,            # 프리즈 권한 없음
        clawback=HCF_ADDRESS           # 클로백 권한 없음
    )

    # 트랜잭션 서명
    signed_txn = txn.sign(HCF_PRIVATE_KEY)

    # 블록체인에 트랜잭션 전송
    txid = algod_client.send_transaction(signed_txn)
    print("트랜잭션 전송 완료. txID:", txid)

    # 블록 포함 대기 및 결과 조회
    confirmed_txn = wait_for_confirmation(algod_client, txid)
    asa_id = confirmed_txn["asset-index"]
    print("발행된 ASA ID (HCF ESG Token):", asa_id)

    return asa_id

# 스크립트 실행 시 바로 토큰 발행 수행
if __name__ == "__main__":
    create_hcf_token()
