# -*- coding: utf-8 -*-
"""
Get Free ALGO - Automated Request
"""
import requests
import time

# 실제 계정 주소들
ADMIN_ADDRESS = "HXEHBWEDLO272XOIFFME26D5EAWULT4PGE75V3NKGGBIMQL2JM7S4ZU5PM"
USER_ADDRESS = "F34WKJ6ZZOPJS264UEP6XF4WJZ6UDMXVXIDFX447KKGGVF5XYELHEBRWUI"

def check_balance(address):
    """잔액 확인"""
    try:
        api_url = f"https://testnet-api.algonode.cloud/v2/accounts/{address}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get("amount", 0) / 1000000
            return balance
        return 0
    except:
        return 0

def request_faucet_algo(address):
    """Faucet에 ALGO 요청"""
    try:
        # AWS AlgoNode Faucet
        faucet_url = "https://dispenser.testnet.aws.algodev.network/"

        # POST 요청으로 ALGO 요청
        payload = {"account": address}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(faucet_url, data=payload, headers=headers)

        if response.status_code == 200:
            print(f"SUCCESS: ALGO requested for {address[:10]}...")
            return True
        else:
            print(f"Failed to request ALGO: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error requesting ALGO: {e}")
        return False

def main():
    print("PAM-TALK ESG Chain - Free ALGO Request")
    print("=" * 50)

    # 현재 잔액 확인
    admin_balance = check_balance(ADMIN_ADDRESS)
    user_balance = check_balance(USER_ADDRESS)

    print(f"Current Balances:")
    print(f"Admin: {admin_balance} ALGO")
    print(f"User: {user_balance} ALGO")
    print()

    # ALGO가 없으면 요청
    if admin_balance == 0:
        print("Requesting ALGO for Admin account...")
        if request_faucet_algo(ADMIN_ADDRESS):
            print("Request sent! Waiting for confirmation...")
        else:
            print("Manual request required:")
            print("1. Visit: https://dispenser.testnet.aws.algodev.network/")
            print(f"2. Enter address: {ADMIN_ADDRESS}")
            print("3. Click 'Dispense'")

    # 잔액 변화 모니터링
    print("\nMonitoring balance changes...")
    for i in range(12):  # 6분 동안 모니터링
        time.sleep(30)
        new_balance = check_balance(ADMIN_ADDRESS)

        if new_balance > admin_balance:
            print(f"SUCCESS! Balance updated: {new_balance} ALGO")
            print("Ready to create PAM token!")

            # 토큰 생성 스크립트 생성
            create_token_creation_script()
            break
        else:
            print(f"Waiting... Current balance: {new_balance} ALGO")

    print("Monitoring complete.")

def create_token_creation_script():
    """토큰 생성 스크립트 생성"""
    token_script = '''"""
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

        # 확인 대기
        print("Waiting for confirmation...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id)

        # ASA ID 추출
        asset_id = confirmed_txn["asset-index"]

        print("SUCCESS! PAM-TALK ESG Token Created!")
        print(f"ASA ID: {asset_id}")
        print(f"Transaction: {tx_id}")

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
        f.write(f"ASA ID: {asset_id}\\n")
        f.write(f"Creation TX: {tx_id}\\n")
        f.write(f"Creator: {ADMIN_ADDRESS}\\n")
        f.write(f"Total Supply: 1,000,000,000 PAM\\n")
        f.write(f"Decimals: 3\\n")
        f.write("\\nVerification Links:\\n")
        f.write(f"API: https://testnet-api.algonode.cloud/v2/assets/{asset_id}\\n")
        f.write(f"Transaction: https://testnet-api.algonode.cloud/v2/transactions/{tx_id}\\n")

if __name__ == "__main__":
    asset_id, tx_id = create_pam_token()
    if asset_id:
        print(f"\\nNext step: Run token transfer test")
        print(f"python step3_transfer_tokens.py {asset_id}")
'''

    with open('step2_create_token.py', 'w') as f:
        f.write(token_script)

    print("Token creation script ready: step2_create_token.py")

if __name__ == "__main__":
    main()