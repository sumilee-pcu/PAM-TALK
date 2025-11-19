#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 잔액 확인 도구 (입력 대기 없음)
"""

import requests

def quick_balance_check():
    """빠른 잔액 확인"""

    testnet_api = "https://testnet-api.algonode.cloud"
    addresses = {
        "Original": "JMSZGMCCMM3B6WK6B2X56AKWZWZQXNMM64S22LJW66XQOQGKOPWCBFTYXE",
        "Second": "NZJPXRBNMZHPSDSQH3XBSOGFZTWN6TR4HHGPVLR4DLGQOKIJJCVNFQ4RHM",
        "New_Valid": "3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4"
    }

    print("Quick Balance Check")
    print("=" * 30)

    total = 0

    for name, addr in addresses.items():
        try:
            response = requests.get(f"{testnet_api}/v2/accounts/{addr}", timeout=10)
            if response.status_code == 200:
                balance = response.json().get('amount', 0) / 1_000_000
                total += balance
                status = "FUNDED" if balance > 0 else "EMPTY"
                print(f"{name}: {balance:.6f} ALGO [{status}]")
            else:
                print(f"{name}: API Error {response.status_code}")

        except Exception as e:
            print(f"{name}: Network Error - {str(e)[:50]}")

    print(f"\nTotal: {total:.6f} ALGO")

    if total >= 20:
        print("STATUS: Ready for token creation")
    elif total >= 10:
        print("STATUS: Partially funded, need more")
    else:
        print("STATUS: Funding required")
        print("\nNEXT STEP:")
        print("1. Go to: https://bank.testnet.algorand.network/")
        print("2. Paste: 3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4")
        print("3. Click Dispense")
        print("4. Run this script again")

    return total

if __name__ == "__main__":
    quick_balance_check()