# -*- coding: utf-8 -*-
from algosdk import mnemonic
from algosdk.account import address_from_private_key
from algosdk.transaction import ApplicationCreateTxn
from algosdk.v2client import algod
import base64
import time
from app.config import HCF_MNEMONIC

# 알고랜드 클라이언트 설정
def get_algod_client():
    algod_address = "https://testnet-api.algonode.network"  # 테스트넷 API 주소
    algod_token = "<your_algod_token>"  # 여기에 API 토큰을 입력하세요.
    return algod.AlgodClient(algod_token, algod_address)

# 스마트 계약 배포 함수
def deploy_smart_contract():
    # 지갑 로드 (Mnemonic 사용)
    private_key = mnemonic.to_private_key(HCF_MNEMONIC)  # Mnemonic 값
    sender_address = address_from_private_key(private_key)

    # 알고랜드 클라이언트 생성
    algod_client = get_algod_client()

    # 스마트 계약 코드 (ASC1) 작성
    contract_source = '''  
    #pragma version 2

    txn TypeEnum
    int AssetTransfer
    ==
    txn Sender
    addr 0x<your_sender_address>  // 발신자 주소
    ==
    txn Amount
    int 1000000
    ==
    &&
    '''

    # 스마트 계약 배포를 위한 트랜잭션 생성
    suggested_params = algod_client.suggested_params()

    # 스마트 계약 배포 트랜잭션 생성
    txn = ApplicationCreateTxn(
        sender=sender_address,
        sp=suggested_params,
        approval_program=base64.b64encode(contract_source.encode()).decode(),  # 스마트 계약 코드
        clear_program=base64.b64encode(b'')  # 상태 초기화 프로그램을 빈 값으로 설정
    )

    # 서명
    signed_txn = txn.sign(private_key)

    # 트랜잭션 전송
    tx_id = algod_client.send_transaction(signed_txn)

    # 트랜잭션 확인
    wait_for_confirmation(algod_client, tx_id)

    # 배포된 스마트 계약 ID 가져오기
    tx_info = algod_client.pending_transaction_info(tx_id)
    app_id = tx_info["txn"]["txn"]["application-index"]
    print(f"배포된 스마트 계약 ID: {app_id}")
    return app_id

# 트랜잭션 확인 함수
def wait_for_confirmation(algod_client, tx_id):
    while True:
        tx_info = algod_client.pending_transaction_info(tx_id)
        if tx_info.get('confirmed-round') is not None:
            print(f"Transaction confirmed in round {tx_info['confirmed-round']}")
            break
        else:
            print("Waiting for confirmation...")
            time.sleep(1)

# 스마트 계약 배포
deploy_smart_contract()
