#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 빠른 종합 상태 확인
한 번에 모든 정보를 확인할 수 있는 간단한 대시보드
"""

import requests
import time
from datetime import datetime

def check_all_status():
    """모든 PAM-TALK 구성요소 상태를 한 번에 확인"""

    print("PAM-TALK QUICK STATUS DASHBOARD")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 메인 플랫폼 상태
    print("1. MAIN PLATFORM STATUS")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:5003/api/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("Status: ONLINE")
            print(f"Platform: {data.get('platform', 'N/A')}")
            print(f"Version: {data.get('version', 'N/A')}")
            print(f"Features: {len(data.get('features', []))}")
        else:
            print(f"Status: ERROR (HTTP {response.status_code})")
    except:
        print("Status: OFFLINE")
    print()

    # 2. 계정 상태들
    accounts = {
        "ORIGINAL": {
            "addr": "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM",
            "tx": "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
        },
        "NEW": {
            "addr": "HFRJPS4VWQEQMWVPKKDYDTVAJQH2MHNIR37HRNQIPXFMI4BCEKK4OX4ZFI",
            "tx": "AHMIHQW44N5BFYR6CQJO63GBHUJRE7X3H5ORVHPZ3WWLBYYUTBHQ"
        }
    }

    print("2. ALGORAND ACCOUNTS")
    print("-" * 30)

    funded_count = 0
    for name, info in accounts.items():
        try:
            url = f"https://testnet-api.algonode.cloud/v2/accounts/{info['addr']}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                balance = data.get('account', {}).get('amount', 0) / 1000000
                status = data.get('account', {}).get('status', 'Unknown')

                funding_status = "FUNDED" if balance >= 1.0 else "WAITING"
                if balance >= 1.0:
                    funded_count += 1

                print(f"{name} Account: {funding_status}")
                print(f"  Balance: {balance:.6f} ALGO")
                print(f"  Status: {status}")
                print(f"  Address: {info['addr'][:25]}...")
            else:
                print(f"{name} Account: ERROR (API)")
        except:
            print(f"{name} Account: ERROR (Network)")
        print()

    # 3. PAM 토큰 상태
    print("3. PAM TOKEN")
    print("-" * 15)
    try:
        token_id = "746418487"
        url = f"https://testnet-api.algonode.cloud/v2/assets/{token_id}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            params = data.get('asset', {}).get('params', {})
            total = params.get('total', 0)

            if total > 0:
                print("Status: ACTIVE")
                print(f"Name: {params.get('name', 'N/A')}")
                print(f"Total: {total:,}")
            else:
                print("Status: INACTIVE (No supply)")
        else:
            print("Status: NOT FOUND")
    except:
        print("Status: ERROR (Network)")
    print()

    # 4. 실행 중인 프로세스
    print("4. BACKGROUND PROCESSES")
    print("-" * 25)

    # 포트 체크로 실행 중인 서비스 확인
    services = [
        ("PAM-TALK Main", 5003),
        ("ESG Chain", 5004)
    ]

    running_services = 0
    for name, port in services:
        try:
            response = requests.get(f"http://localhost:{port}/api/health", timeout=1)
            if response.status_code == 200:
                print(f"{name}: RUNNING (Port {port})")
                running_services += 1
            else:
                print(f"{name}: ERROR (Port {port})")
        except:
            print(f"{name}: STOPPED (Port {port})")
    print()

    # 5. 전체 요약
    print("5. SYSTEM SUMMARY")
    print("-" * 20)
    print(f"Funded Accounts: {funded_count}/2")
    print(f"Running Services: {running_services}/2")

    # 전체 상태 판단
    if funded_count > 0 and running_services > 0:
        overall = "OPERATIONAL"
        next_action = "Ready for PAM token operations"
    elif funded_count > 0:
        overall = "READY"
        next_action = "Start ESG chain service"
    elif running_services > 0:
        overall = "WAITING"
        next_action = "Wait for account funding"
    else:
        overall = "DOWN"
        next_action = "Start services and check funding"

    print(f"Overall Status: {overall}")
    print(f"Next Action: {next_action}")
    print()

    # 6. 빠른 명령어
    print("6. QUICK COMMANDS")
    print("-" * 20)
    print("Check again: python quick_dashboard.py")
    print("Full monitor: python realtime_dashboard.py")
    print("Account monitor: python monitor_new_account.py")
    print("Create token: cd pamtalk-esg-chain && python step2_create_token.py")

if __name__ == "__main__":
    check_all_status()