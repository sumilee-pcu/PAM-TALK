#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알고랜드 트랜잭션 모니터링 및 리포트 시스템
PAM-TALK 프로젝트용 실시간 블록체인 상태 추적
"""

import requests
import time
import json
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class TransactionReport:
    tx_id: str
    status: str  # "pending", "confirmed", "failed", "not_found"
    round_number: Optional[int] = None
    tx_type: Optional[str] = None
    amount: Optional[float] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    fee: Optional[float] = None
    timestamp: Optional[str] = None
    confirmation_time: Optional[str] = None

@dataclass
class AccountReport:
    address: str
    balance_algo: float
    assets: List[Dict]
    status: str
    created_apps: List[int]
    created_assets: List[int]
    last_update: str

class AlgorandTransactionMonitor:
    def __init__(self):
        self.testnet_api = "https://testnet-api.algonode.cloud/v2"
        self.mainnet_api = "https://mainnet-api.algonode.cloud/v2"
        self.monitored_txs = {}
        self.monitored_accounts = {}
        self.is_monitoring = False

    def get_transaction_status(self, tx_id: str, network: str = "testnet") -> TransactionReport:
        """단일 트랜잭션 상태 조회"""
        api_base = self.testnet_api if network == "testnet" else self.mainnet_api
        url = f"{api_base}/transactions/{tx_id}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tx_data = data.get('transaction', {})

                # 기본 정보
                report = TransactionReport(
                    tx_id=tx_id,
                    status="confirmed",
                    round_number=tx_data.get('confirmed-round'),
                    tx_type=tx_data.get('tx-type'),
                    timestamp=datetime.now().isoformat()
                )

                # 결제 트랜잭션 정보
                if 'payment-transaction' in tx_data:
                    payment = tx_data['payment-transaction']
                    report.amount = payment.get('amount', 0) / 1000000  # microALGO to ALGO
                    report.receiver = payment.get('receiver')

                # 송신자 정보
                report.sender = tx_data.get('sender')
                report.fee = tx_data.get('fee', 0) / 1000000

                return report

            elif response.status_code == 404:
                return TransactionReport(
                    tx_id=tx_id,
                    status="not_found",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return TransactionReport(
                    tx_id=tx_id,
                    status="failed",
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            return TransactionReport(
                tx_id=tx_id,
                status="error",
                timestamp=datetime.now().isoformat()
            )

    def get_account_status(self, address: str, network: str = "testnet") -> AccountReport:
        """계정 상태 조회"""
        api_base = self.testnet_api if network == "testnet" else self.mainnet_api
        url = f"{api_base}/accounts/{address}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                account_data = data.get('account', {})

                return AccountReport(
                    address=address,
                    balance_algo=account_data.get('amount', 0) / 1000000,
                    assets=account_data.get('assets', []),
                    status=account_data.get('status', 'Offline'),
                    created_apps=account_data.get('created-apps', []),
                    created_assets=account_data.get('created-assets', []),
                    last_update=datetime.now().isoformat()
                )
            else:
                return AccountReport(
                    address=address,
                    balance_algo=0.0,
                    assets=[],
                    status="Not Found",
                    created_apps=[],
                    created_assets=[],
                    last_update=datetime.now().isoformat()
                )

        except Exception as e:
            return AccountReport(
                address=address,
                balance_algo=0.0,
                assets=[],
                status="Error",
                created_apps=[],
                created_assets=[],
                last_update=datetime.now().isoformat()
            )

    def monitor_transaction(self, tx_id: str, timeout_minutes: int = 30, network: str = "testnet"):
        """트랜잭션을 지속적으로 모니터링"""
        print(f"🔍 트랜잭션 모니터링 시작: {tx_id}")
        print(f"⏰ 타임아웃: {timeout_minutes}분")
        print("=" * 60)

        start_time = datetime.now()
        timeout_time = start_time + timedelta(minutes=timeout_minutes)

        while datetime.now() < timeout_time:
            report = self.get_transaction_status(tx_id, network)

            # 상태 출력
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 상태: {report.status}")

            if report.status == "confirmed":
                print("✅ 트랜잭션 확인됨!")
                print(f"   라운드: {report.round_number}")
                print(f"   타입: {report.tx_type}")
                if report.amount:
                    print(f"   금액: {report.amount:.6f} ALGO")
                if report.receiver:
                    print(f"   수신자: {report.receiver}")
                print(f"   수수료: {report.fee:.6f} ALGO")
                break
            elif report.status == "failed":
                print("❌ 트랜잭션 실패")
                break
            elif report.status == "not_found":
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"⏳ 대기 중... ({elapsed:.0f}초 경과)")

            time.sleep(30)  # 30초마다 확인

        if datetime.now() >= timeout_time:
            print("⏰ 타임아웃: 트랜잭션이 제한 시간 내에 확인되지 않았습니다.")

        return report

    def monitor_account(self, address: str, duration_minutes: int = 10, network: str = "testnet"):
        """계정을 지속적으로 모니터링"""
        print(f"👤 계정 모니터링 시작: {address[:8]}...")
        print(f"⏰ 모니터링 시간: {duration_minutes}분")
        print("=" * 60)

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        previous_balance = None

        while datetime.now() < end_time:
            report = self.get_account_status(address, network)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # 잔액 변화 감지
            if previous_balance is not None and report.balance_algo != previous_balance:
                change = report.balance_algo - previous_balance
                print(f"💰 [{timestamp}] 잔액 변화 감지!")
                print(f"   이전: {previous_balance:.6f} ALGO")
                print(f"   현재: {report.balance_algo:.6f} ALGO")
                print(f"   변화: {change:+.6f} ALGO")
            else:
                print(f"[{timestamp}] 잔액: {report.balance_algo:.6f} ALGO")

            # 자산 정보
            if report.assets:
                print(f"   보유 자산: {len(report.assets)}개")
                for asset in report.assets[:3]:  # 최대 3개만 표시
                    asset_id = asset.get('asset-id')
                    amount = asset.get('amount', 0)
                    print(f"     Asset {asset_id}: {amount}")

            previous_balance = report.balance_algo
            time.sleep(30)  # 30초마다 확인

        return report

    def generate_report(self, tx_id: str = None, address: str = None, network: str = "testnet"):
        """종합 리포트 생성"""
        print("📊 PAM-TALK 블록체인 상태 리포트")
        print("=" * 50)
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"네트워크: {network.upper()}")
        print()

        # 트랜잭션 리포트
        if tx_id:
            print("🔗 트랜잭션 상태")
            print("-" * 30)
            tx_report = self.get_transaction_status(tx_id, network)
            print(f"TX ID: {tx_id}")
            print(f"상태: {tx_report.status}")
            if tx_report.status == "confirmed":
                print(f"라운드: {tx_report.round_number}")
                print(f"타입: {tx_report.tx_type}")
                if tx_report.amount:
                    print(f"금액: {tx_report.amount:.6f} ALGO")
                print(f"수수료: {tx_report.fee:.6f} ALGO")
            print()

        # 계정 리포트
        if address:
            print("👤 계정 상태")
            print("-" * 30)
            acc_report = self.get_account_status(address, network)
            print(f"주소: {address}")
            print(f"잔액: {acc_report.balance_algo:.6f} ALGO")
            print(f"상태: {acc_report.status}")
            print(f"보유 자산: {len(acc_report.assets)}개")
            print(f"생성한 앱: {len(acc_report.created_apps)}개")
            print(f"생성한 자산: {len(acc_report.created_assets)}개")
            print()

        # 저장
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "network": network,
            "transaction": tx_report.__dict__ if tx_id else None,
            "account": acc_report.__dict__ if address else None
        }

        filename = f"blockchain_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"📄 리포트 저장됨: {filename}")
        return report_data

def main():
    """메인 실행 함수"""
    monitor = AlgorandTransactionMonitor()

    # PAM-TALK 기본 설정
    pam_tx_id = "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
    pam_admin_address = "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM"

    print("🚀 PAM-TALK 블록체인 모니터링 시스템")
    print("=" * 50)
    print("1. 트랜잭션 모니터링")
    print("2. 계정 모니터링")
    print("3. 종합 리포트 생성")
    print("4. 실시간 모니터링 (트랜잭션 + 계정)")
    print()

    choice = input("선택하세요 (1-4): ").strip()

    if choice == "1":
        monitor.monitor_transaction(pam_tx_id, timeout_minutes=30)

    elif choice == "2":
        monitor.monitor_account(pam_admin_address, duration_minutes=10)

    elif choice == "3":
        monitor.generate_report(tx_id=pam_tx_id, address=pam_admin_address)

    elif choice == "4":
        print("🔄 실시간 모니터링 시작 (Ctrl+C로 중지)")
        try:
            # 트랜잭션과 계정을 동시에 모니터링
            while True:
                print("\\n" + "="*60)
                monitor.generate_report(tx_id=pam_tx_id, address=pam_admin_address)
                print("다음 업데이트까지 60초 대기...")
                time.sleep(60)
        except KeyboardInterrupt:
            print("\\n모니터링이 중지되었습니다.")

    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()