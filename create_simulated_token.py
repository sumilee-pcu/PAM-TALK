#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM 토큰 시뮬레이션 생성기
실제 블록체인 없이 PAM-TALK 기능을 완전히 테스트할 수 있는 환경 구축
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class SimulatedPAMToken:
    token_id: str
    name: str
    symbol: str
    total_supply: int
    decimals: int
    creator_address: str
    created_at: str
    description: str

class PAMTokenSimulator:
    def __init__(self):
        self.token_data = None
        self.accounts = {}
        self.transactions = []

    def create_pam_token(self):
        """시뮬레이션된 PAM 토큰 생성"""

        print("Creating Simulated PAM Token...")
        print("=" * 40)

        # 시뮬레이션된 토큰 데이터 생성
        self.token_data = SimulatedPAMToken(
            token_id="SIM746418487",  # 시뮬레이션 접두사
            name="PAM-TALK ESG Token (Simulated)",
            symbol="PAM-SIM",
            total_supply=1000000000,  # 10억 토큰
            decimals=3,
            creator_address="SIMULATION_MODE_CREATOR",
            created_at=datetime.now().isoformat(),
            description="Simulated PAM-TALK ESG token for testing and development"
        )

        print(f"Token Created Successfully!")
        print(f"Token ID: {self.token_data.token_id}")
        print(f"Name: {self.token_data.name}")
        print(f"Symbol: {self.token_data.symbol}")
        print(f"Total Supply: {self.token_data.total_supply:,}")
        print(f"Decimals: {self.token_data.decimals}")
        print()

        # 초기 계정들에 토큰 배분
        self.initialize_accounts()

        return self.token_data

    def initialize_accounts(self):
        """초기 계정들에 토큰 배분"""

        print("Initializing Account Balances...")
        print("-" * 30)

        # PAM-TALK 계정들
        initial_distribution = {
            "committee": {
                "address": "COMMITTEE_SIMULATION_ADDRESS",
                "balance": 100000000,  # 1억 토큰 (10%)
                "role": "Committee/Treasury"
            },
            "supplier1": {
                "address": "SUPPLIER1_SIMULATION_ADDRESS",
                "balance": 50000000,   # 5천만 토큰 (5%)
                "role": "Local Supplier"
            },
            "consumer1": {
                "address": "CONSUMER1_SIMULATION_ADDRESS",
                "balance": 10000000,   # 1천만 토큰 (1%)
                "role": "Eco Consumer"
            },
            "farmer1": {
                "address": "FARMER1_SIMULATION_ADDRESS",
                "balance": 25000000,   # 2천5백만 토큰 (2.5%)
                "role": "Local Farmer"
            }
        }

        for account_name, data in initial_distribution.items():
            self.accounts[account_name] = data
            print(f"{data['role']}: {data['balance']:,} PAM tokens")

            # 트랜잭션 기록 생성
            self.transactions.append({
                "tx_id": f"SIM_INIT_{account_name.upper()}_{int(time.time())}",
                "type": "initial_distribution",
                "from": "TOKEN_CREATOR",
                "to": data['address'],
                "amount": data['balance'],
                "timestamp": datetime.now().isoformat(),
                "status": "confirmed"
            })

        print()

    def transfer_tokens(self, from_account: str, to_account: str, amount: int, reason: str = ""):
        """토큰 전송 시뮬레이션"""

        if from_account not in self.accounts:
            return {"success": False, "error": "Sender account not found"}

        if self.accounts[from_account]['balance'] < amount:
            return {"success": False, "error": "Insufficient balance"}

        # 계정 생성 (존재하지 않는 경우)
        if to_account not in self.accounts:
            self.accounts[to_account] = {
                "address": f"USER_{to_account.upper()}_ADDRESS",
                "balance": 0,
                "role": "User"
            }

        # 잔액 업데이트
        self.accounts[from_account]['balance'] -= amount
        self.accounts[to_account]['balance'] += amount

        # 트랜잭션 기록
        tx_id = f"SIM_TX_{int(time.time())}"
        transaction = {
            "tx_id": tx_id,
            "type": "transfer",
            "from": self.accounts[from_account]['address'],
            "to": self.accounts[to_account]['address'],
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "confirmed"
        }

        self.transactions.append(transaction)

        return {
            "success": True,
            "tx_id": tx_id,
            "transaction": transaction
        }

    def get_account_balance(self, account_name: str):
        """계정 잔액 조회"""
        if account_name in self.accounts:
            return self.accounts[account_name]['balance']
        return 0

    def get_token_info(self):
        """토큰 정보 조회"""
        return asdict(self.token_data) if self.token_data else None

    def get_transaction_history(self, limit: int = 10):
        """트랜잭션 히스토리 조회"""
        return self.transactions[-limit:]

    def save_simulation_state(self):
        """시뮬레이션 상태 저장"""

        state = {
            "token": asdict(self.token_data) if self.token_data else None,
            "accounts": self.accounts,
            "transactions": self.transactions,
            "last_updated": datetime.now().isoformat()
        }

        filename = "pam_token_simulation_state.json"
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"Simulation state saved to: {filename}")
        return filename

    def load_simulation_state(self, filename: str = "pam_token_simulation_state.json"):
        """시뮬레이션 상태 로드"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)

            if state.get('token'):
                self.token_data = SimulatedPAMToken(**state['token'])

            self.accounts = state.get('accounts', {})
            self.transactions = state.get('transactions', [])

            print(f"Simulation state loaded from: {filename}")
            return True

        except FileNotFoundError:
            print(f"No saved state found: {filename}")
            return False
        except Exception as e:
            print(f"Error loading state: {e}")
            return False

def demo_pam_token_operations():
    """PAM 토큰 운영 데모"""

    print("PAM-TALK TOKEN SIMULATION DEMO")
    print("=" * 50)
    print()

    # 시뮬레이터 생성
    simulator = PAMTokenSimulator()

    # 토큰 생성
    token = simulator.create_pam_token()

    # 에코 활동 시뮬레이션
    print("SIMULATING ECO ACTIVITIES...")
    print("-" * 30)

    # 1. 로컬 푸드 구매 보상
    result = simulator.transfer_tokens(
        "committee", "consumer1", 1000,
        "Local food purchase reward"
    )
    if result['success']:
        print("✓ Consumer rewarded for local food purchase: 1,000 PAM")

    # 2. 농부 직판 보상
    result = simulator.transfer_tokens(
        "committee", "farmer1", 5000,
        "Direct sale to consumer bonus"
    )
    if result['success']:
        print("✓ Farmer rewarded for direct sale: 5,000 PAM")

    # 3. 탄소 절약 챌린지 보상
    result = simulator.transfer_tokens(
        "committee", "consumer1", 2000,
        "Carbon footprint reduction challenge"
    )
    if result['success']:
        print("✓ Consumer completed carbon challenge: 2,000 PAM")

    print()

    # 잔액 확인
    print("ACCOUNT BALANCES AFTER ACTIVITIES:")
    print("-" * 35)
    for account_name, data in simulator.accounts.items():
        balance = data['balance']
        role = data['role']
        print(f"{role}: {balance:,} PAM")

    print()

    # 최근 트랜잭션
    print("RECENT TRANSACTIONS:")
    print("-" * 20)
    for tx in simulator.get_transaction_history(5):
        print(f"TX: {tx['tx_id'][:15]}... | {tx['amount']:,} PAM | {tx['reason']}")

    print()

    # 상태 저장
    filename = simulator.save_simulation_state()

    print()
    print("SIMULATION COMPLETE!")
    print("=" * 30)
    print("✓ PAM token created and distributed")
    print("✓ Eco activities simulated")
    print("✓ Rewards distributed")
    print("✓ State saved for PAM-TALK integration")
    print()
    print(f"Next step: Integrate with PAM-TALK platform")
    print(f"Use simulation data for testing all features")

if __name__ == "__main__":
    demo_pam_token_operations()