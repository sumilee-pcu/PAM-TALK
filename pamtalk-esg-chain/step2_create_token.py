# -*- coding: utf-8 -*-
"""
Step 2: Create PAM-TALK ESG Token
실제 ASA 토큰 생성
"""
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn
import time

# 관리자 계정 정보
ADMIN_ADDRESS = "HXEHBWEDLO272XOIFFME26D5EAWULT4PGE75V3NKGGBIMQL2JM7S4ZU5PM"
ADMIN_MNEMONIC = "address midnight rotate brush convince east exact shallow eager dignity promote object sea casual fantasy sleep soup display cover security sadness mosquito clarify abandon help"
ADMIN_PRIVATE_KEY = mnemonic.to_private_key(ADMIN_MNEMONIC)

def create_pam_token():
    """PAM-TALK ESG 토큰 생성"""
    try:
        # Algorand 테스트넷 클라이언트
        algod_address = "https://testnet-api.algonode.cloud"
        algod_client = algod.AlgodClient("", algod_address)

        print("Creating PAM-TALK ESG Token...")
        print(f"Creator: {ADMIN_ADDRESS}")

        # 잔액 확인
        account_info = algod_client.account_info(ADMIN_ADDRESS)
        balance = account_info['amount'] / 1000000
        print(f"Current balance: {balance} ALGO")

        if balance < 0.1:
            print("Insufficient balance! Need at least 0.1 ALGO")
            print("Get ALGO from: https://dispenser.testnet.aws.algodev.network/")
            return None, None

        # 네트워크 파라미터
        params = algod_client.suggested_params()

        # ASA 생성 트랜잭션
        txn = AssetConfigTxn(
            sender=ADMIN_ADDRESS,
            sp=params,
            total=1000000000,  # 10억 개 (소수점 3자리)
            default_frozen=False,
            unit_name="PAM",
            asset_name="PAM-TALK ESG Token",
            manager=ADMIN_ADDRESS,
            reserve=ADMIN_ADDRESS,
            freeze=ADMIN_ADDRESS,
            clawback=ADMIN_ADDRESS,
            url="https://pam-talk.io/esg-token",
            decimals=3,
            note="Agricultural ESG Activity Reward Token".encode()
        )

        # 트랜잭션 서명
        stxn = txn.sign(ADMIN_PRIVATE_KEY)

        # 블록체인에 전송
        tx_id = algod_client.send_transaction(stxn)
        print(f"Transaction sent: {tx_id}")
        print("This is your REAL transaction hash!")

        # 확인 대기
        print("Waiting for confirmation...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id)

        # ASA ID 추출
        asset_id = confirmed_txn["asset-index"]

        print("SUCCESS! PAM-TALK ESG Token Created!")
        print(f"Real ASA ID: {asset_id}")
        print(f"Real Transaction Hash: {tx_id}")

        # 결과 저장
        save_token_info(asset_id, tx_id)

        return asset_id, tx_id

    except Exception as e:
        print(f"Error creating token: {e}")
        return None, None

def wait_for_confirmation(client, tx_id):
    """트랜잭션 확인 대기"""
    confirmed_txn = client.pending_transaction_info(tx_id)
    while confirmed_txn.get("confirmed-round", 0) == 0:
        print("Confirming...")
        time.sleep(2)
        confirmed_txn = client.pending_transaction_info(tx_id)

    print(f"Confirmed in round: {confirmed_txn['confirmed-round']}")
    return confirmed_txn

def save_token_info(asset_id, tx_id):
    """토큰 정보 저장"""
    with open('pam_token_created.txt', 'w') as f:
        f.write("PAM-TALK ESG Token Successfully Created!\\n")
        f.write("=" * 40 + "\\n\\n")
        f.write(f"REAL ASA ID: {asset_id}\\n")
        f.write(f"REAL Creation TX: {tx_id}\\n")
        f.write(f"Creator: {ADMIN_ADDRESS}\\n")
        f.write(f"Total Supply: 1,000,000,000 PAM\\n")
        f.write(f"Decimals: 3\\n")
        f.write("\\nREAL Verification Links:\\n")
        f.write(f"API Asset Info: https://testnet-api.algonode.cloud/v2/assets/{asset_id}\\n")
        f.write(f"API Transaction: https://testnet-api.algonode.cloud/v2/transactions/{tx_id}\\n")

    print("Token info saved to: pam_token_created.txt")

if __name__ == "__main__":
    asset_id, tx_id = create_pam_token()
    if asset_id:
        print(f"\\nNext step: Token transfer test")
        print(f"python step3_transfer_tokens.py {asset_id}")
    else:
        print("\\nFirst get ALGO, then run this script again")
        print("Check balance: python check_balance_simple.py")