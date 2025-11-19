#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 종합 실시간 대시보드
모든 서비스와 블록체인 상태를 한 화면에서 실시간 모니터링
"""

import requests
import time
import json
import os
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SystemStatus:
    service_name: str
    status: str  # "running", "stopped", "error"
    port: Optional[int] = None
    last_check: str = ""
    details: Dict = None

@dataclass
class BlockchainStatus:
    address: str
    balance: float
    status: str
    tx_id: Optional[str] = None
    tx_status: str = ""
    last_update: str = ""

class PAMTalkDashboard:
    def __init__(self):
        self.running = False

        # 계정 정보
        self.accounts = {
            "original": {
                "address": "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM",
                "tx_id": "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
            },
            "new": {
                "address": "HFRJPS4VWQEQMWVPKKDYDTVAJQH2MHNIR37HRNQIPXFMI4BCEKK4OX4ZFI",
                "tx_id": "AHMIHQW44N5BFYR6CQJO63GBHUJRE7X3H5ORVHPZ3WWLBYYUTBHQ"
            }
        }

        # 서비스 정보
        self.services = {
            "main_platform": {"name": "PAM-TALK Main", "port": 5003, "path": "/api/health"},
            "esg_chain": {"name": "ESG Chain", "port": 5004, "path": "/api/health"}
        }

    def clear_screen(self):
        """화면 클리어 (크로스 플랫폼)"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_service_status(self, service_name: str, config: Dict) -> SystemStatus:
        """서비스 상태 확인"""
        try:
            url = f"http://localhost:{config['port']}{config['path']}"
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                return SystemStatus(
                    service_name=config['name'],
                    status="running",
                    port=config['port'],
                    last_check=datetime.now().strftime("%H:%M:%S"),
                    details=response.json() if response.content else {}
                )
            else:
                return SystemStatus(
                    service_name=config['name'],
                    status="error",
                    port=config['port'],
                    last_check=datetime.now().strftime("%H:%M:%S"),
                    details={"error": f"HTTP {response.status_code}"}
                )
        except Exception as e:
            return SystemStatus(
                service_name=config['name'],
                status="stopped",
                port=config['port'],
                last_check=datetime.now().strftime("%H:%M:%S"),
                details={"error": str(e)}
            )

    def check_blockchain_status(self, account_name: str, account_info: Dict) -> BlockchainStatus:
        """블록체인 계정 상태 확인"""
        address = account_info["address"]
        tx_id = account_info["tx_id"]

        try:
            # 계정 잔액 확인
            account_url = f"https://testnet-api.algonode.cloud/v2/accounts/{address}"
            account_response = requests.get(account_url, timeout=5)

            balance = 0.0
            account_status = "unknown"

            if account_response.status_code == 200:
                account_data = account_response.json()
                balance = account_data.get('account', {}).get('amount', 0) / 1000000
                account_status = account_data.get('account', {}).get('status', 'unknown')

            # 트랜잭션 상태 확인
            tx_url = f"https://testnet-api.algonode.cloud/v2/transactions/{tx_id}"
            tx_response = requests.get(tx_url, timeout=5)

            tx_status = "pending"
            if tx_response.status_code == 200:
                tx_status = "confirmed"
            elif tx_response.status_code == 404:
                tx_status = "pending"
            else:
                tx_status = "error"

            return BlockchainStatus(
                address=address,
                balance=balance,
                status=account_status,
                tx_id=tx_id,
                tx_status=tx_status,
                last_update=datetime.now().strftime("%H:%M:%S")
            )

        except Exception as e:
            return BlockchainStatus(
                address=address,
                balance=0.0,
                status="error",
                tx_id=tx_id,
                tx_status="error",
                last_update=datetime.now().strftime("%H:%M:%S")
            )

    def get_pam_token_status(self) -> Dict:
        """PAM 토큰 상태 확인"""
        token_id = "746418487"
        try:
            url = f"https://testnet-api.algonode.cloud/v2/assets/{token_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                params = data.get('asset', {}).get('params', {})
                return {
                    "status": "active" if params.get('total', 0) > 0 else "inactive",
                    "name": params.get('name', 'N/A'),
                    "total": params.get('total', 0),
                    "creator": params.get('creator', 'N/A')[:20] + "..."
                }
            else:
                return {"status": "not_found", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def display_dashboard(self):
        """대시보드 화면 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("PAM-TALK COMPREHENSIVE REAL-TIME DASHBOARD")
        print("=" * 80)
        print(f"Last Update: {timestamp}")
        print()

        # 1. 서비스 상태
        print("1. SERVICE STATUS")
        print("-" * 40)
        for service_key, service_config in self.services.items():
            status = self.check_service_status(service_key, service_config)

            status_icon = {
                "running": "[ONLINE]",
                "stopped": "[OFFLINE]",
                "error": "[ERROR]"
            }.get(status.status, "[UNKNOWN]")

            print(f"{status_icon} {status.service_name} (Port {status.port})")

            if status.status == "running" and status.details:
                if 'platform' in status.details:
                    print(f"    Platform: {status.details.get('platform', 'N/A')}")
                if 'version' in status.details:
                    print(f"    Version: {status.details.get('version', 'N/A')}")
                if 'features' in status.details:
                    features = status.details.get('features', [])
                    print(f"    Features: {len(features)} active")
            elif status.status != "running":
                print(f"    Error: {status.details.get('error', 'Unknown')}")

            print(f"    Last Check: {status.last_check}")
            print()

        # 2. 블록체인 계정 상태
        print("2. BLOCKCHAIN ACCOUNTS")
        print("-" * 40)
        for account_name, account_info in self.accounts.items():
            blockchain_status = self.check_blockchain_status(account_name, account_info)

            funding_status = "FUNDED" if blockchain_status.balance >= 1.0 else "NEEDS_FUNDING"
            funding_icon = "[READY]" if funding_status == "FUNDED" else "[WAITING]"

            print(f"{funding_icon} {account_name.upper()} ACCOUNT")
            print(f"    Address: {blockchain_status.address[:30]}...")
            print(f"    Balance: {blockchain_status.balance:.6f} ALGO")
            print(f"    Account Status: {blockchain_status.status}")
            print(f"    Transaction: {blockchain_status.tx_status}")
            print(f"    TX ID: {blockchain_status.tx_id[:25]}...")
            print(f"    Last Update: {blockchain_status.last_update}")
            print()

        # 3. PAM 토큰 상태
        print("3. PAM TOKEN STATUS")
        print("-" * 40)
        token_status = self.get_pam_token_status()

        if token_status.get("status") == "active":
            print("[ACTIVE] PAM Token")
            print(f"    Name: {token_status.get('name', 'N/A')}")
            print(f"    Total Supply: {token_status.get('total', 0):,}")
            print(f"    Creator: {token_status.get('creator', 'N/A')}")
        else:
            print("[INACTIVE] PAM Token")
            print(f"    Status: {token_status.get('status', 'unknown')}")
            if 'error' in token_status:
                print(f"    Error: {token_status['error']}")
        print()

        # 4. 시스템 요약
        print("4. SYSTEM SUMMARY")
        print("-" * 40)

        # 서비스 요약
        running_services = sum(1 for svc in [self.check_service_status(k, v) for k, v in self.services.items()] if svc.status == "running")
        total_services = len(self.services)
        print(f"Services: {running_services}/{total_services} running")

        # 블록체인 요약
        funded_accounts = sum(1 for acc in [self.check_blockchain_status(k, v) for k, v in self.accounts.items()] if self.check_blockchain_status(k, v).balance >= 1.0)
        total_accounts = len(self.accounts)
        print(f"Funded Accounts: {funded_accounts}/{total_accounts}")

        # 전체 상태
        if running_services == total_services and funded_accounts > 0:
            overall_status = "OPERATIONAL"
        elif running_services > 0 or funded_accounts > 0:
            overall_status = "PARTIAL"
        else:
            overall_status = "DOWN"

        print(f"Overall Status: {overall_status}")

        # 5. 추천 액션
        print()
        print("5. RECOMMENDED ACTIONS")
        print("-" * 40)

        if funded_accounts == 0:
            print("- Wait for account funding to complete")
            print("- Monitor blockchain transactions")
        elif token_status.get("status") != "active":
            print("- Create PAM token with funded account")
            print("- Run: python pamtalk-esg-chain/step2_create_token.py")
        elif running_services < total_services:
            print("- Start missing services")
            print("- Check service logs for errors")
        else:
            print("- System ready for full operation")
            print("- Test end-to-end functionality")

    def run_realtime(self, update_interval: int = 10):
        """실시간 모니터링 실행"""
        self.running = True

        print("Starting PAM-TALK Real-time Dashboard...")
        print(f"Update interval: {update_interval} seconds")
        print("Press Ctrl+C to stop")
        print()

        try:
            while self.running:
                self.clear_screen()
                self.display_dashboard()

                print()
                print("=" * 80)
                print(f"Next update in {update_interval} seconds... (Ctrl+C to stop)")

                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\\n\\nDashboard stopped by user")
            self.running = False

    def run_single_check(self):
        """단일 상태 확인"""
        self.display_dashboard()

def main():
    dashboard = PAMTalkDashboard()

    print("PAM-TALK Comprehensive Dashboard")
    print("=" * 40)
    print("1. Single status check")
    print("2. Real-time monitoring (10s interval)")
    print("3. Real-time monitoring (30s interval)")
    print("4. Real-time monitoring (60s interval)")
    print()

    choice = input("Select option (1-4): ").strip()

    if choice == "1":
        dashboard.run_single_check()
    elif choice == "2":
        dashboard.run_realtime(10)
    elif choice == "3":
        dashboard.run_realtime(30)
    elif choice == "4":
        dashboard.run_realtime(60)
    else:
        print("Invalid choice. Running single check...")
        dashboard.run_single_check()

if __name__ == "__main__":
    main()