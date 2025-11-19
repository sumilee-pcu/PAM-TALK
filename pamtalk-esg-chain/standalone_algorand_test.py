# -*- coding: utf-8 -*-
"""
독립적인 Algorand 테스트 스크립트
데이터베이스 없이 실제 블록체인 연동 테스트
"""
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, AssetTransferTxn
import time

class AlgorandTester:
    def __init__(self):
        # Algorand 테스트넷 클라이언트
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)

        print("Algorand Testnet Connection Success!")

    def create_account(self):
        """새 계정 생성"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)

        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': account_mnemonic
        }

    def check_balance(self, address):
        """계정 잔액 조회"""
        try:
            account_info = self.algod_client.account_info(address)
            balance = account_info['amount'] / 1000000  # microAlgos to Algos
            return balance
        except Exception as e:
            print(f"Balance check error: {e}")
            return 0

    def create_pam_token(self, creator_private_key):
        """PAM-TALK ESG 토큰 생성"""
        try:
            creator_address = account.address_from_private_key(creator_private_key)

            # 잔액 확인
            balance = self.check_balance(creator_address)
            if balance < 0.1:
                print(f"❌ 잔액 부족: {balance} ALGO")
                print(f"📱 https://testnet.algoexplorer.io/dispenser 에서 ALGO를 받으세요")
                print(f"💳 주소: {creator_address}")
                return None, None

            # 네트워크 파라미터
            params = self.algod_client.suggested_params()

            # ASA 생성 트랜잭션
            txn = AssetConfigTxn(
                sender=creator_address,
                sp=params,
                total=1000000000,  # 10억 개
                default_frozen=False,
                unit_name="PAM",
                asset_name="PAM-TALK ESG Token",
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                url="https://pam-talk.io/esg-token",
                decimals=3,
                note="농업 ESG 활동 보상 토큰".encode()
            )

            # 트랜잭션 서명
            stxn = txn.sign(creator_private_key)

            # 블록체인에 전송
            tx_id = self.algod_client.send_transaction(stxn)
            print(f"🚀 트랜잭션 전송됨: {tx_id}")
            print(f"🔍 Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            # 확인 대기
            print("⏳ 트랜잭션 확인 대기 중...")
            confirmed_txn = self.wait_for_confirmation(tx_id)

            # ASA ID 추출
            asset_id = confirmed_txn["asset-index"]

            print(f"✅ PAM-TALK ESG 토큰 생성 완료!")
            print(f"🪙 ASA ID: {asset_id}")
            print(f"🌐 토큰 정보: https://testnet.algoexplorer.io/asset/{asset_id}")

            return tx_id, asset_id

        except Exception as e:
            print(f"❌ 토큰 생성 오류: {e}")
            return None, None

    def opt_in_asset(self, user_private_key, asset_id):
        """ASA opt-in (토큰 수신 준비)"""
        try:
            user_address = account.address_from_private_key(user_private_key)
            params = self.algod_client.suggested_params()

            # opt-in 트랜잭션 (자기에게 0개 전송)
            txn = AssetTransferTxn(
                sender=user_address,
                sp=params,
                receiver=user_address,
                amt=0,
                index=asset_id
            )

            stxn = txn.sign(user_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            self.wait_for_confirmation(tx_id)

            print(f"✅ {user_address} ASA opt-in 완료")
            print(f"🔍 Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            return tx_id

        except Exception as e:
            print(f"❌ opt-in 오류: {e}")
            return None

    def transfer_tokens(self, sender_private_key, recipient_address, asset_id, amount):
        """토큰 전송"""
        try:
            sender_address = account.address_from_private_key(sender_private_key)
            params = self.algod_client.suggested_params()

            # 토큰 전송 트랜잭션
            txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=recipient_address,
                amt=amount,
                index=asset_id,
                note=f"PAM-TALK ESG 보상: {amount/1000} PAM".encode()
            )

            stxn = txn.sign(sender_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            self.wait_for_confirmation(tx_id)

            print(f"✅ {amount/1000} PAM 토큰 전송 완료!")
            print(f"📤 From: {sender_address}")
            print(f"📥 To: {recipient_address}")
            print(f"🔍 Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            return tx_id

        except Exception as e:
            print(f"❌ 토큰 전송 오류: {e}")
            return None

    def wait_for_confirmation(self, tx_id):
        """트랜잭션 확인 대기"""
        try:
            confirmed_txn = self.algod_client.pending_transaction_info(tx_id)
            while confirmed_txn.get("confirmed-round", 0) == 0:
                print("⏳ 확인 대기...")
                time.sleep(2)
                confirmed_txn = self.algod_client.pending_transaction_info(tx_id)

            print(f"✅ 확인됨! 블록: {confirmed_txn['confirmed-round']}")
            return confirmed_txn

        except Exception as e:
            print(f"❌ 확인 오류: {e}")
            raise

def main():
    """메인 테스트 실행"""
    print("PAM-TALK ESG Chain Blockchain Test Start!")
    print("=" * 50)

    tester = AlgorandTester()

    # 1. 관리자 계정 생성
    print("\n1️⃣ 관리자 계정 생성")
    admin_account = tester.create_account()
    print(f"📱 관리자 주소: {admin_account['address']}")
    print(f"🔑 니모닉: {admin_account['mnemonic']}")
    print(f"💰 테스트넷 ALGO 받기: https://testnet.algoexplorer.io/dispenser")
    print(f"🔍 지갑 확인: https://testnet.algoexplorer.io/address/{admin_account['address']}")

    # ALGO 받을 때까지 대기
    input("\n⏸️  위 링크에서 ALGO를 받은 후 Enter를 눌러주세요...")

    # 2. PAM 토큰 생성
    print("\n2️⃣ PAM-TALK ESG 토큰 생성")
    tx_hash, asset_id = tester.create_pam_token(admin_account['private_key'])

    if not asset_id:
        print("❌ 토큰 생성 실패. 스크립트를 다시 실행해주세요.")
        return

    # 3. 사용자 계정 생성
    print("\n3️⃣ 사용자 계정 생성")
    user_account = tester.create_account()
    print(f"👤 사용자 주소: {user_account['address']}")
    print(f"🔍 지갑 확인: https://testnet.algoexplorer.io/address/{user_account['address']}")

    # 4. 사용자 opt-in
    print("\n4️⃣ 사용자 PAM 토큰 opt-in")
    # 사용자도 ALGO가 필요함
    print(f"💰 사용자도 ALGO 받기: https://testnet.algoexplorer.io/dispenser")
    print(f"📱 사용자 주소: {user_account['address']}")
    input("⏸️  사용자 주소로도 ALGO를 받은 후 Enter를 눌러주세요...")

    opt_in_tx = tester.opt_in_asset(user_account['private_key'], asset_id)

    if opt_in_tx:
        # 5. 토큰 전송 (보상 지급)
        print("\n5️⃣ PAM 토큰 전송 (보상 지급)")
        transfer_tx = tester.transfer_tokens(
            admin_account['private_key'],
            user_account['address'],
            asset_id,
            50000  # 50.000 PAM
        )

        if transfer_tx:
            print("\n🎉 테스트 완료!")
            print("=" * 50)
            print("📋 최종 결과:")
            print(f"🪙 PAM 토큰 ASA ID: {asset_id}")
            print(f"🌐 토큰 정보: https://testnet.algoexplorer.io/asset/{asset_id}")
            print(f"👑 관리자 지갑: https://testnet.algoexplorer.io/address/{admin_account['address']}")
            print(f"👤 사용자 지갑: https://testnet.algoexplorer.io/address/{user_account['address']}")
            print(f"💸 전송 트랜잭션: https://testnet.algoexplorer.io/tx/{transfer_tx}")
            print("\n✅ 이제 모든 링크가 실제로 동작합니다!")

if __name__ == "__main__":
    main()