# -*- coding: utf-8 -*-
"""
Algorand 블록체인 실제 연동 서비스
테스트넷 연결, ASA 생성, 트랜잭션 발송
"""
import os
import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod, indexer
from algosdk.transaction import AssetConfigTxn, AssetTransferTxn, PaymentTxn
from algosdk.atomic_transaction_composer import *
from algosdk.logic import get_application_address
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class AlgorandClient:
    def __init__(self):
        # Algorand 테스트넷 설정
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.indexer_address = "https://testnet-idx.algonode.cloud"
        self.indexer_token = ""

        # 클라이언트 초기화
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
        self.indexer_client = indexer.IndexerClient(self.indexer_token, self.indexer_address)

        # PAM-TALK ESG 토큰 설정 (환경변수에서 로드)
        self.pam_token_id = os.getenv('PAM_TOKEN_ASA_ID')  # 생성 후 설정
        self.creator_private_key = os.getenv('CREATOR_PRIVATE_KEY')  # 관리자 개인키
        self.creator_address = account.address_from_private_key(self.creator_private_key) if self.creator_private_key else None

    def create_pam_esg_token(self) -> Tuple[bool, str, Optional[int]]:
        """
        PAM-TALK ESG 토큰 (ASA) 생성
        Returns: (성공여부, 트랜잭션해시, ASA_ID)
        """
        try:
            if not self.creator_private_key:
                # 새 계정 생성 (최초 실행시)
                private_key, address = account.generate_account()
                print(f"새 관리자 계정 생성됨:")
                print(f"주소: {address}")
                print(f"개인키: {private_key}")
                print(f"니모닉: {mnemonic.from_private_key(private_key)}")
                print("⚠️  테스트넷 ALGO를 받아주세요: https://testnet.algoexplorer.io/dispenser")
                return False, "관리자 계정 생성 완료. 테스트넷 ALGO 필요", None

            # 현재 네트워크 파라미터 가져오기
            params = self.algod_client.suggested_params()

            # ASA 생성 트랜잭션
            txn = AssetConfigTxn(
                sender=self.creator_address,
                sp=params,
                total=1000000000,  # 10억 개 (소수점 3자리)
                default_frozen=False,
                unit_name="PAM",
                asset_name="PAM-TALK ESG Token",
                manager=self.creator_address,
                reserve=self.creator_address,
                freeze=self.creator_address,
                clawback=self.creator_address,
                url="https://pam-talk.io/esg-token",
                decimals=3,
                note="농업 ESG 활동 보상 토큰".encode()
            )

            # 트랜잭션 서명
            stxn = txn.sign(self.creator_private_key)

            # 블록체인에 전송
            tx_id = self.algod_client.send_transaction(stxn)

            # 트랜잭션 확인 대기
            confirmed_txn = self.wait_for_confirmation(tx_id)

            # ASA ID 추출
            asset_id = confirmed_txn["asset-index"]

            logger.info(f"PAM-TALK ESG 토큰 생성 완료: ASA ID {asset_id}")

            return True, tx_id, asset_id

        except Exception as e:
            logger.error(f"ASA 생성 오류: {e}")
            return False, str(e), None

    def create_user_wallet(self) -> Dict[str, str]:
        """
        새 사용자 지갑 생성
        Returns: 지갑 정보 (주소, 개인키, 니모닉)
        """
        try:
            private_key, address = account.generate_account()
            wallet_mnemonic = mnemonic.from_private_key(private_key)

            return {
                'address': address,
                'private_key': private_key,
                'mnemonic': wallet_mnemonic,
                'network': 'testnet'
            }

        except Exception as e:
            logger.error(f"지갑 생성 오류: {e}")
            return {}

    def opt_in_to_asset(self, user_private_key: str, asset_id: int) -> Tuple[bool, str]:
        """
        사용자가 ASA 수신을 위해 opt-in 수행
        """
        try:
            user_address = account.address_from_private_key(user_private_key)
            params = self.algod_client.suggested_params()

            # Asset opt-in 트랜잭션 (자기 자신에게 0개 전송)
            txn = AssetTransferTxn(
                sender=user_address,
                sp=params,
                receiver=user_address,
                amt=0,
                index=asset_id
            )

            # 트랜잭션 서명 및 전송
            stxn = txn.sign(user_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            # 확인 대기
            self.wait_for_confirmation(tx_id)

            logger.info(f"사용자 {user_address} ASA opt-in 완료")
            return True, tx_id

        except Exception as e:
            logger.error(f"ASA opt-in 오류: {e}")
            return False, str(e)

    def transfer_tokens(
        self,
        recipient_address: str,
        amount: int,
        note: str = ""
    ) -> Tuple[bool, str]:
        """
        PAM 토큰 전송 (보상 지급)
        amount: 소수점 3자리 기준 (1000 = 1.000 PAM)
        """
        try:
            if not self.pam_token_id:
                raise ValueError("PAM 토큰 ASA ID가 설정되지 않음")

            params = self.algod_client.suggested_params()

            # Asset 전송 트랜잭션
            txn = AssetTransferTxn(
                sender=self.creator_address,
                sp=params,
                receiver=recipient_address,
                amt=amount,
                index=int(self.pam_token_id),
                note=note.encode() if note else None
            )

            # 트랜잭션 서명 및 전송
            stxn = txn.sign(self.creator_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            # 확인 대기
            self.wait_for_confirmation(tx_id)

            logger.info(f"{amount/1000} PAM 토큰을 {recipient_address}에게 전송 완료")
            return True, tx_id

        except Exception as e:
            logger.error(f"토큰 전송 오류: {e}")
            return False, str(e)

    def get_account_info(self, address: str) -> Optional[Dict]:
        """계정 정보 조회"""
        try:
            return self.algod_client.account_info(address)
        except Exception as e:
            logger.error(f"계정 조회 오류: {e}")
            return None

    def get_asset_balance(self, address: str, asset_id: int) -> int:
        """특정 ASA 잔액 조회"""
        try:
            account_info = self.algod_client.account_info(address)
            assets = account_info.get('assets', [])

            for asset in assets:
                if asset['asset-id'] == asset_id:
                    return asset['amount']

            return 0  # Asset을 보유하지 않음 또는 opt-in 안함

        except Exception as e:
            logger.error(f"잔액 조회 오류: {e}")
            return 0

    def get_transaction_info(self, tx_id: str) -> Optional[Dict]:
        """트랜잭션 정보 조회"""
        try:
            return self.indexer_client.search_transactions(txid=tx_id)
        except Exception as e:
            logger.error(f"트랜잭션 조회 오류: {e}")
            return None

    def wait_for_confirmation(self, tx_id: str, timeout: int = 10) -> Dict:
        """트랜잭션 확인 대기"""
        try:
            confirmed_txn = self.algod_client.pending_transaction_info(tx_id)
            while confirmed_txn.get("confirmed-round", 0) == 0:
                print(f"트랜잭션 {tx_id} 확인 대기 중...")
                confirmed_txn = self.algod_client.pending_transaction_info(tx_id)

            return confirmed_txn

        except Exception as e:
            logger.error(f"트랜잭션 확인 오류: {e}")
            raise

    def get_network_status(self) -> Dict[str, any]:
        """네트워크 상태 조회"""
        try:
            status = self.algod_client.status()
            return {
                'connected': True,
                'network': 'testnet',
                'last_round': status['last-round'],
                'time_since_last_round': status['time-since-last-round'],
                'catchup_time': status['catchup-time'],
                'pam_token_id': self.pam_token_id
            }
        except Exception as e:
            logger.error(f"네트워크 상태 조회 오류: {e}")
            return {
                'connected': False,
                'error': str(e)
            }

    def check_pam_token_info(self) -> Optional[Dict]:
        """PAM 토큰 정보 조회"""
        try:
            if not self.pam_token_id:
                return None

            asset_info = self.algod_client.asset_info(int(self.pam_token_id))
            return asset_info

        except Exception as e:
            logger.error(f"PAM 토큰 정보 조회 오류: {e}")
            return None