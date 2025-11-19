#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 알고랜드 계정 생성 및 테스트 ALGO 요청
"""

from algosdk import account, mnemonic
import requests

def create_new_account():
    """새로운 알고랜드 계정 생성"""
    private_key, address = account.generate_account()
    mn = mnemonic.from_private_key(private_key)

    return {
        'address': address,
        'private_key': private_key,
        'mnemonic': mn
    }

def check_balance(address):
    """계정 잔액 확인"""
    api_url = f'https://testnet-api.algonode.cloud/v2/accounts/{address}'

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get('account', {}).get('amount', 0)
            return balance / 1000000
        else:
            return 0
    except:
        return 0

def main():
    print("NEW ALGORAND ACCOUNT GENERATOR")
    print("="*50)

    # 새 계정 생성
    account_info = create_new_account()

    print(f"New Account Address: {account_info['address']}")
    print(f"Mnemonic: {account_info['mnemonic']}")
    print()
    print("SECURITY WARNING: Keep the mnemonic phrase safe!")
    print("="*50)
    print()

    # 테스트넷 디스펜서 안내
    print("To get test ALGOs:")
    print(f"1. Go to: https://testnet.algoexplorer.io/dispenser")
    print(f"2. Enter address: {account_info['address']}")
    print(f"3. Click 'Send me ALGOs'")
    print()

    # 현재 잔액 확인
    balance = check_balance(account_info['address'])
    print(f"Current Balance: {balance:.6f} ALGO")

    # 계정 정보 파일 저장
    with open('new_account_info.txt', 'w') as f:
        f.write(f"PAM-TALK New Account Information\n")
        f.write(f"===============================\n\n")
        f.write(f"Address: {account_info['address']}\n")
        f.write(f"Mnemonic: {account_info['mnemonic']}\n")
        f.write(f"Created: $(date)\n\n")
        f.write(f"Test ALGO Dispenser:\n")
        f.write(f"https://testnet.algoexplorer.io/dispenser\n\n")
        f.write(f"Account Explorer:\n")
        f.write(f"https://testnet.algoexplorer.io/address/{account_info['address']}\n")

    print("Account info saved to: new_account_info.txt")

if __name__ == "__main__":
    main()