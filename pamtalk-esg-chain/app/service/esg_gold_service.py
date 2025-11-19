# -*- coding: utf-8 -*-
"""
ESG-Gold Token Service
ESG-GOLD 토큰 관리 서비스 (발행, 소각, 전송)
1 ESG-GOLD = 1 DC (Digital Carbon) = 1kg CO2 감축량
"""

import json
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from algosdk import account, encoding
from algosdk.v2client import algod
from algosdk.transaction import (
    AssetTransferTxn, AssetConfigTxn,
    wait_for_confirmation, PaymentTxn
)

logger = logging.getLogger(__name__)


class ESGGoldService:
    """ESG-GOLD 토큰 관리 서비스"""

    def __init__(self, config_path: str = 'esg_gold_config.json'):
        """
        Args:
            config_path: ESG-GOLD 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.client = self._create_client()
        self.asset_id = int(self.config['token_id']) if self.config.get('token_id') else None

    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    def _create_client(self) -> algod.AlgodClient:
        """Algorand 클라이언트 생성"""
        algod_address = self.config['algod_endpoint']
        algod_token = ""  # Public API
        return algod.AlgodClient(algod_token, algod_address)

    def mint_esg_gold(self, recipient_address: str, amount_dc: float,
                     creator_private_key: str, reason: str = "carbon_reduction") -> Dict:
        """
        ESG-GOLD 토큰 발행 (Minting)

        Args:
            recipient_address: 받을 지갑 주소
            amount_dc: DC 단위 수량 (1 DC = 1 kg CO2)
            creator_private_key: 발행 권한 계정의 private key
            reason: 발행 사유

        Returns:
            {
                'success': bool,
                'tx_id': str,
                'amount_dc': float,
                'amount_micro': int,
                'recipient': str,
                'timestamp': str
            }
        """
        if not self.asset_id:
            raise ValueError("ESG-GOLD token not deployed. Please deploy first.")

        try:
            # DC를 micro units로 변환
            decimals = self.config['decimals']
            amount_micro = int(amount_dc * (10 ** decimals))

            if amount_micro <= 0:
                raise ValueError(f"Invalid amount: {amount_dc} DC")

            # 발행자 주소 추출
            creator_address = account.address_from_private_key(creator_private_key)

            # 수신자가 ESG-GOLD를 옵트인했는지 확인
            if not self.has_opted_in(recipient_address):
                logger.warning(f"Recipient {recipient_address} hasn't opted in to ESG-GOLD")
                # Auto opt-in은 보안상 수신자가 직접 해야 함
                return {
                    'success': False,
                    'error': 'recipient_not_opted_in',
                    'message': 'Recipient must opt-in to ESG-GOLD first'
                }

            # Asset Transfer 트랜잭션 (Reserve → Recipient)
            params = self.client.suggested_params()

            txn = AssetTransferTxn(
                sender=creator_address,
                sp=params,
                receiver=recipient_address,
                amt=amount_micro,
                index=self.asset_id,
                note=json.dumps({
                    'type': 'esg_gold_mint',
                    'reason': reason,
                    'amount_dc': amount_dc,
                    'timestamp': datetime.now().isoformat()
                }).encode()
            )

            # 서명 및 전송
            signed_txn = txn.sign(creator_private_key)
            tx_id = self.client.send_transaction(signed_txn)

            # 확인 대기
            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            logger.info(f"Minted {amount_dc} DC ({amount_micro} micro) ESG-GOLD to {recipient_address}")

            return {
                'success': True,
                'tx_id': tx_id,
                'amount_dc': amount_dc,
                'amount_micro': amount_micro,
                'recipient': recipient_address,
                'timestamp': datetime.now().isoformat(),
                'block': confirmed_txn['confirmed-round']
            }

        except Exception as e:
            logger.error(f"Failed to mint ESG-GOLD: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def burn_esg_gold(self, amount_dc: float, owner_address: str,
                     owner_private_key: str, reason: str = "marketplace_discount") -> Dict:
        """
        ESG-GOLD 토큰 소각 (Burning)

        Args:
            amount_dc: 소각할 DC 수량
            owner_address: 토큰 소유자 주소
            owner_private_key: 소유자 private key
            reason: 소각 사유 (marketplace_discount, offset_retirement 등)

        Returns:
            {
                'success': bool,
                'tx_id': str,
                'burned_dc': float,
                'burned_micro': int,
                'remaining_balance': float
            }
        """
        if not self.asset_id:
            raise ValueError("ESG-GOLD token not deployed")

        try:
            # DC를 micro units로 변환
            decimals = self.config['decimals']
            amount_micro = int(amount_dc * (10 ** decimals))

            # 현재 잔액 확인
            balance = self.get_balance(owner_address)
            if balance < amount_dc:
                return {
                    'success': False,
                    'error': 'insufficient_balance',
                    'required': amount_dc,
                    'available': balance
                }

            # Creator address 가져오기
            asset_info = self.client.asset_info(self.asset_id)
            creator_address = asset_info['params']['creator']

            # 소각: 토큰을 creator의 reserve로 전송
            params = self.client.suggested_params()

            txn = AssetTransferTxn(
                sender=owner_address,
                sp=params,
                receiver=creator_address,  # Reserve로 전송 = 소각
                amt=amount_micro,
                index=self.asset_id,
                note=json.dumps({
                    'type': 'esg_gold_burn',
                    'reason': reason,
                    'amount_dc': amount_dc,
                    'timestamp': datetime.now().isoformat()
                }).encode()
            )

            signed_txn = txn.sign(owner_private_key)
            tx_id = self.client.send_transaction(signed_txn)

            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            # 소각 후 잔액
            remaining_balance = self.get_balance(owner_address)

            logger.info(f"Burned {amount_dc} DC ESG-GOLD from {owner_address}. Reason: {reason}")

            return {
                'success': True,
                'tx_id': tx_id,
                'burned_dc': amount_dc,
                'burned_micro': amount_micro,
                'remaining_balance': remaining_balance,
                'timestamp': datetime.now().isoformat(),
                'block': confirmed_txn['confirmed-round']
            }

        except Exception as e:
            logger.error(f"Failed to burn ESG-GOLD: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def transfer_esg_gold(self, sender_address: str, sender_private_key: str,
                         recipient_address: str, amount_dc: float,
                         note: str = "") -> Dict:
        """
        ESG-GOLD 토큰 전송

        Args:
            sender_address: 발신자 주소
            sender_private_key: 발신자 private key
            recipient_address: 수신자 주소
            amount_dc: 전송할 DC 수량
            note: 메모

        Returns:
            {'success': bool, 'tx_id': str, ...}
        """
        if not self.asset_id:
            raise ValueError("ESG-GOLD token not deployed")

        try:
            # 잔액 확인
            balance = self.get_balance(sender_address)
            if balance < amount_dc:
                return {
                    'success': False,
                    'error': 'insufficient_balance',
                    'required': amount_dc,
                    'available': balance
                }

            # 수신자 opt-in 확인
            if not self.has_opted_in(recipient_address):
                return {
                    'success': False,
                    'error': 'recipient_not_opted_in'
                }

            # 전송량 계산
            decimals = self.config['decimals']
            amount_micro = int(amount_dc * (10 ** decimals))

            # 전송 트랜잭션
            params = self.client.suggested_params()

            txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=recipient_address,
                amt=amount_micro,
                index=self.asset_id,
                note=note.encode() if note else b""
            )

            signed_txn = txn.sign(sender_private_key)
            tx_id = self.client.send_transaction(signed_txn)

            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            logger.info(f"Transferred {amount_dc} DC ESG-GOLD from {sender_address} to {recipient_address}")

            return {
                'success': True,
                'tx_id': tx_id,
                'sender': sender_address,
                'recipient': recipient_address,
                'amount_dc': amount_dc,
                'amount_micro': amount_micro,
                'timestamp': datetime.now().isoformat(),
                'block': confirmed_txn['confirmed-round']
            }

        except Exception as e:
            logger.error(f"Failed to transfer ESG-GOLD: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def opt_in_esg_gold(self, account_address: str, account_private_key: str) -> Dict:
        """
        ESG-GOLD 토큰 Opt-in
        사용자가 ESG-GOLD를 받기 위해서는 먼저 opt-in 필요

        Args:
            account_address: 계정 주소
            account_private_key: 계정 private key

        Returns:
            {'success': bool, 'tx_id': str}
        """
        if not self.asset_id:
            raise ValueError("ESG-GOLD token not deployed")

        try:
            # 이미 opt-in 되어 있는지 확인
            if self.has_opted_in(account_address):
                return {
                    'success': True,
                    'already_opted_in': True,
                    'message': 'Already opted in to ESG-GOLD'
                }

            # Opt-in 트랜잭션 (자기 자신에게 0 전송)
            params = self.client.suggested_params()

            txn = AssetTransferTxn(
                sender=account_address,
                sp=params,
                receiver=account_address,
                amt=0,
                index=self.asset_id
            )

            signed_txn = txn.sign(account_private_key)
            tx_id = self.client.send_transaction(signed_txn)

            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            logger.info(f"Account {account_address} opted in to ESG-GOLD")

            return {
                'success': True,
                'tx_id': tx_id,
                'account': account_address,
                'timestamp': datetime.now().isoformat(),
                'block': confirmed_txn['confirmed-round']
            }

        except Exception as e:
            logger.error(f"Failed to opt-in ESG-GOLD: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_balance(self, account_address: str) -> float:
        """
        ESG-GOLD 잔액 조회 (DC 단위)

        Args:
            account_address: 계정 주소

        Returns:
            잔액 (DC 단위)
        """
        if not self.asset_id:
            return 0.0

        try:
            account_info = self.client.account_info(account_address)

            # 해당 asset 찾기
            assets = account_info.get('assets', [])
            for asset in assets:
                if asset['asset-id'] == self.asset_id:
                    amount_micro = asset['amount']
                    decimals = self.config['decimals']
                    amount_dc = amount_micro / (10 ** decimals)
                    return round(amount_dc, 6)

            return 0.0

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0

    def has_opted_in(self, account_address: str) -> bool:
        """
        계정이 ESG-GOLD에 opt-in 했는지 확인

        Args:
            account_address: 계정 주소

        Returns:
            opt-in 여부
        """
        if not self.asset_id:
            return False

        try:
            account_info = self.client.account_info(account_address)
            assets = account_info.get('assets', [])

            for asset in assets:
                if asset['asset-id'] == self.asset_id:
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to check opt-in status: {e}")
            return False

    def get_asset_info(self) -> Dict:
        """
        ESG-GOLD 토큰 정보 조회

        Returns:
            토큰 정보
        """
        if not self.asset_id:
            return {}

        try:
            asset_info = self.client.asset_info(self.asset_id)
            params = asset_info['params']

            total_supply_micro = params['total']
            decimals = params['decimals']
            total_supply_dc = total_supply_micro / (10 ** decimals)

            return {
                'asset_id': self.asset_id,
                'name': params['name'],
                'unit_name': params['unit-name'],
                'total_supply': total_supply_micro,
                'total_supply_dc': total_supply_dc,
                'decimals': decimals,
                'creator': params['creator'],
                'manager': params.get('manager'),
                'reserve': params.get('reserve'),
                'freeze': params.get('freeze'),
                'clawback': params.get('clawback'),
                'url': params.get('url', ''),
                'metadata_hash': params.get('metadata-hash'),
            }

        except Exception as e:
            logger.error(f"Failed to get asset info: {e}")
            return {}

    def get_transaction_history(self, account_address: str, limit: int = 100) -> List[Dict]:
        """
        ESG-GOLD 거래 내역 조회

        Args:
            account_address: 계정 주소
            limit: 조회 개수 제한

        Returns:
            거래 내역 리스트
        """
        if not self.asset_id:
            return []

        try:
            # Algorand Indexer API 필요 (여기서는 기본 구현)
            # 실제로는 indexer를 사용하거나 DB에 저장된 거래 내역 조회
            logger.warning("Transaction history requires Algorand Indexer API")
            return []

        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            return []

    def calculate_carbon_offset(self, esg_gold_amount: float) -> Dict:
        """
        ESG-GOLD로 상쇄된 탄소량 계산

        Args:
            esg_gold_amount: ESG-GOLD 수량 (DC 단위)

        Returns:
            {
                'esg_gold': float,
                'carbon_offset_kg': float,
                'carbon_offset_tons': float,
                'trees_equivalent': float
            }
        """
        # 1 ESG-GOLD = 1 DC = 1 kg CO2
        carbon_offset_kg = esg_gold_amount * 1.0
        carbon_offset_tons = carbon_offset_kg / 1000

        # 나무 환산 (1그루 나무 = 연간 약 22kg CO2 흡수)
        trees_equivalent = carbon_offset_kg / 22

        return {
            'esg_gold': esg_gold_amount,
            'carbon_offset_kg': round(carbon_offset_kg, 3),
            'carbon_offset_tons': round(carbon_offset_tons, 6),
            'trees_equivalent': round(trees_equivalent, 2),
            'description': f'{esg_gold_amount} ESG-GOLD = {carbon_offset_kg:.3f}kg CO2 offset'
        }


# 사용 예시
if __name__ == "__main__":
    import os

    # ESG-GOLD 서비스 초기화
    service = ESGGoldService('../../esg_gold_config.json')

    # 자산 정보 조회
    asset_info = service.get_asset_info()
    if asset_info:
        print("=== ESG-GOLD Token Info ===")
        print(f"Asset ID: {asset_info['asset_id']}")
        print(f"Name: {asset_info['name']}")
        print(f"Total Supply: {asset_info['total_supply_dc']:,.2f} DC")
        print(f"Creator: {asset_info['creator']}")

    # 탄소 상쇄량 계산
    offset = service.calculate_carbon_offset(100.5)
    print(f"\n=== Carbon Offset ===")
    print(f"100.5 ESG-GOLD = {offset['carbon_offset_kg']} kg CO2")
    print(f"Equivalent to {offset['trees_equivalent']} trees")
