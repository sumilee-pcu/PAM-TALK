#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
올바른 체크섬을 가진 새로운 알고랜드 계정 생성
"""

from algosdk import account, mnemonic

def create_new_algorand_account():
    """새로운 알고랜드 계정 생성 (올바른 체크섬 포함)"""

    print("Creating New Algorand Account...")
    print("=" * 40)

    # 새 계정 생성
    private_key, address = account.generate_account()

    # 니모닉 생성
    account_mnemonic = mnemonic.from_private_key(private_key)

    print("[OK] Account Created Successfully!")
    print()
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")
    print()
    print("Mnemonic (25 words):")
    print("-" * 20)
    print(account_mnemonic)
    print()

    # 검증
    recovered_private_key = mnemonic.to_private_key(account_mnemonic)
    recovered_address = account.address_from_private_key(recovered_private_key)

    if recovered_address == address:
        print("[OK] Account verification successful!")
    else:
        print("[ERROR] Account verification failed!")
        return None

    # 계정 정보 저장
    account_info = {
        "address": address,
        "private_key": private_key,
        "mnemonic": account_mnemonic,
        "created_for": "PAM-TALK Token Creation",
        "purpose": "Algorand testnet funding and token operations"
    }

    return account_info

def save_account_info(account_info):
    """계정 정보를 파일에 저장"""

    import json
    from datetime import datetime

    filename = f"pam_algorand_account_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump({
            **account_info,
            "created_at": datetime.now().isoformat(),
            "network": "testnet"
        }, f, indent=2)

    print(f"Account info saved to: {filename}")
    print()
    print("IMPORTANT SECURITY NOTES:")
    print("- Keep the private key and mnemonic secure")
    print("- Never share private key in production")
    print("- This is for testnet only")

    return filename

if __name__ == "__main__":
    account_info = create_new_algorand_account()

    if account_info:
        save_account_info(account_info)

        print()
        print("Next Steps:")
        print("1. Use this address for funding:")
        print(f"   {account_info['address']}")
        print("2. Go to: https://bank.testnet.algorand.network/")
        print("3. Paste the address above")
        print("4. Click 'Dispense'")
        print("5. Run balance check script")