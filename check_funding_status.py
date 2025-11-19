#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알고랜드 계정 펀딩 상태 실시간 확인 도구
"""

import requests
import time
from datetime import datetime

class AlgorandFundingChecker:
    def __init__(self):
        self.testnet_api = "https://testnet-api.algonode.cloud"

    def check_account_balance(self, address: str):
        """계정 잔액 확인"""
        try:
            url = f"{self.testnet_api}/v2/accounts/{address}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                balance_microalgos = data.get('amount', 0)
                balance_algos = balance_microalgos / 1_000_000

                return {
                    "success": True,
                    "balance_algos": balance_algos,
                    "balance_microalgos": balance_microalgos,
                    "address": address,
                    "status": "active" if balance_algos > 0 else "unfunded"
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "address": address
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }

    def monitor_funding(self, address: str, target_balance: float = 10.0, timeout: int = 300):
        """펀딩 완료까지 모니터링"""

        print(f"📊 계정 펀딩 모니터링 시작")
        print(f"주소: {address}")
        print(f"목표 잔액: {target_balance} ALGO")
        print(f"최대 대기시간: {timeout}초")
        print("=" * 60)

        start_time = time.time()
        check_count = 0

        while time.time() - start_time < timeout:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            result = self.check_account_balance(address)

            if result["success"]:
                balance = result["balance_algos"]
                status = result["status"]

                print(f"[{current_time}] 체크 #{check_count} - 잔액: {balance:.6f} ALGO ({status})")

                if balance >= target_balance:
                    print()
                    print("🎉 펀딩 완료!")
                    print(f"✅ 최종 잔액: {balance:.6f} ALGO")
                    print(f"⏰ 소요시간: {time.time() - start_time:.1f}초")
                    return True

            else:
                print(f"[{current_time}] 체크 #{check_count} - 오류: {result['error']}")

            # 5초 대기
            time.sleep(5)

        print()
        print("⏰ 타임아웃: 지정된 시간 내에 펀딩이 완료되지 않았습니다")
        return False

def check_pam_accounts():
    """PAM-TALK 계정들 상태 확인"""

    checker = AlgorandFundingChecker()

    accounts = {
        "원래 계정": "JMSZGMCCMM3B6WK6B2X56AKWZWZQXNMM64S22LJW66XQOQGKOPWCBFTYXE",
        "새 계정": "NZJPXRBNMZHPSDSQH3XBSOGFZTWN6TR4HHGPVLR4DLGQOKIJJCVNFQ4RHM"
    }

    print("PAM-TALK Account Funding Status Check")
    print("=" * 50)

    total_balance = 0

    for name, address in accounts.items():
        result = checker.check_account_balance(address)

        if result["success"]:
            balance = result["balance_algos"]
            status = result["status"]
            total_balance += balance

            status_mark = "[OK]" if balance > 0 else "[NO]"
            print(f"{status_mark} {name}: {balance:.6f} ALGO ({status})")
        else:
            print(f"[ERR] {name}: Check failed - {result['error']}")

    print()
    print(f"Total Balance: {total_balance:.6f} ALGO")

    if total_balance >= 20:  # 토큰 생성에 필요한 최소 금액
        print("[OK] Token creation possible (sufficient balance)")
    else:
        needed = 20 - total_balance
        print(f"[WARN] Token creation not possible (need additional: {needed:.6f} ALGO)")

    return total_balance

if __name__ == "__main__":
    # 현재 상태 확인
    balance = check_pam_accounts()

    if balance < 20:
        print()
        print("Funding Instructions:")
        print("1. Visit: https://bank.testnet.algorand.network/")
        print("2. Enter address: NZJPXRBNMZHPSDSQH3XBSOGFZTWN6TR4HHGPVLR4DLGQOKIJJCVNFQ4RHM")
        print("3. Click 'Dispense'")
        print("4. Run this script again to verify")

        print()
        input("Press Enter after funding to check again...")

        # 펀딩 모니터링 시작
        checker = AlgorandFundingChecker()
        checker.monitor_funding(
            "NZJPXRBNMZHPSDSQH3XBSOGFZTWN6TR4HHGPVLR4DLGQOKIJJCVNFQ4RHM",
            target_balance=10.0,
            timeout=300
        )