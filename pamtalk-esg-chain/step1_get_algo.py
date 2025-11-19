# -*- coding: utf-8 -*-
"""
Step 1: 무료 테스트넷 ALGO 받기
실제 PAM 토큰 생성을 위한 준비 단계
"""
import requests
import time

# 생성된 실제 계정 정보
ADMIN_ADDRESS = "HXEHBWEDLO272XOIFFME26D5EAWULT4PGE75V3NKGGBIMQL2JM7S4ZU5PM"
USER_ADDRESS = "F34WKJ6ZZOPJS264UEP6XF4WJZ6UDMXVXIDFX447KKGGVF5XYELHEBRWUI"

def check_balance(address):
    """계정 잔액 확인"""
    try:
        api_url = f"https://testnet-api.algonode.cloud/v2/accounts/{address}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get("amount", 0) / 1000000  # microAlgos to Algos
            return balance, data.get("round", 0)
        else:
            print(f"API Error: {response.status_code}")
            return 0, 0
    except Exception as e:
        print(f"Error checking balance: {e}")
        return 0, 0

def monitor_balance_changes():
    """잔액 변화 모니터링"""
    print("PAM-TALK ESG Chain - ALGO Balance Monitor")
    print("=" * 60)
    print()
    print("ACCOUNT ADDRESSES:")
    print(f"Admin: {ADMIN_ADDRESS}")
    print(f"User:  {USER_ADDRESS}")
    print()

    # 현재 잔액 확인
    admin_balance, admin_round = check_balance(ADMIN_ADDRESS)
    user_balance, user_round = check_balance(USER_ADDRESS)

    print("CURRENT BALANCES:")
    print(f"Admin: {admin_balance} ALGO (Round: {admin_round})")
    print(f"User:  {user_balance} ALGO (Round: {user_round})")
    print()

    # Faucet 안내
    print("STEP 1: GET FREE TEST ALGO")
    print("=" * 40)
    print("Visit these faucets and request test ALGO:")
    print()

    faucets = [
        {
            "name": "AWS Algorand Faucet",
            "url": "https://dispenser.testnet.aws.algodev.network/",
            "status": "Primary - Most Reliable"
        },
        {
            "name": "AlgoDev Faucet",
            "url": "https://bank.testnet.algorand.network/",
            "status": "Alternative"
        },
        {
            "name": "Testnet Dispenser",
            "url": "https://testnet.algoexplorer.io/dispenser",
            "status": "Backup"
        }
    ]

    for i, faucet in enumerate(faucets, 1):
        print(f"{i}. {faucet['name']} ({faucet['status']})")
        print(f"   URL: {faucet['url']}")
        print(f"   Admin Address: {ADMIN_ADDRESS}")
        print(f"   User Address: {USER_ADDRESS}")
        print()

    print("INSTRUCTIONS:")
    print("1. Copy the Admin address above")
    print("2. Visit the AWS Algorand Faucet (most reliable)")
    print("3. Paste the address and request ALGO")
    print("4. Wait 1-2 minutes for confirmation")
    print("5. Run this script again to check balance")
    print()

    # 자동 모니터링 모드
    print("AUTO MONITORING MODE:")
    print("This script will check balances every 30 seconds...")
    print("Press Ctrl+C to stop")
    print("=" * 40)

    try:
        while True:
            time.sleep(30)
            new_admin_balance, new_admin_round = check_balance(ADMIN_ADDRESS)
            new_user_balance, new_user_round = check_balance(USER_ADDRESS)

            # 변화 감지
            admin_changed = new_admin_balance != admin_balance
            user_changed = new_user_balance != user_balance

            if admin_changed or user_changed:
                print(f"\n[{time.strftime('%H:%M:%S')}] BALANCE UPDATE!")
                print(f"Admin: {admin_balance} -> {new_admin_balance} ALGO")
                print(f"User:  {user_balance} -> {new_user_balance} ALGO")

                admin_balance, admin_round = new_admin_balance, new_admin_round
                user_balance, user_round = new_user_balance, new_user_round

                # ALGO를 받았으면 다음 단계 안내
                if new_admin_balance > 0:
                    print("\nSUCCESS! Admin account funded!")
                    print("Ready to create PAM-TALK ESG Token!")
                    print("Run: python step2_create_token.py")
                    break

            else:
                print(f"[{time.strftime('%H:%M:%S')}] Waiting... Admin: {admin_balance} ALGO, User: {user_balance} ALGO")

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        print(f"Final balances - Admin: {admin_balance} ALGO, User: {user_balance} ALGO")

def quick_balance_check():
    """빠른 잔액 확인"""
    admin_balance, _ = check_balance(ADMIN_ADDRESS)
    user_balance, _ = check_balance(USER_ADDRESS)

    print("Quick Balance Check:")
    print(f"Admin: {admin_balance} ALGO")
    print(f"User: {user_balance} ALGO")

    if admin_balance > 0:
        print("✅ Ready to create PAM token!")
        return True
    else:
        print("❌ Need ALGO to create token")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        ready = quick_balance_check()
        if ready:
            print("Run: python step2_create_token.py")
    else:
        monitor_balance_changes()