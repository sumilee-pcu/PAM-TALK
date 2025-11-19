# -*- coding: utf-8 -*-
"""
블록체인 기반 검증 기록 서비스
Algorand 블록체인에 검증 데이터 저장 및 위조 방지
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from algosdk import account, encoding
from algosdk.v2client import algod
from algosdk.transaction import (
    ApplicationCreateTxn,
    ApplicationCallTxn,
    OnComplete,
    StateSchema,
    wait_for_confirmation,
    PaymentTxn
)

from .committee_verification_workflow import VerificationResult

logger = logging.getLogger(__name__)


class BlockchainVerificationService:
    """블록체인 검증 기록 서비스"""

    def __init__(self, algod_endpoint: str = "https://testnet-api.algonode.cloud",
                 creator_private_key: Optional[str] = None):
        """
        Args:
            algod_endpoint: Algorand 노드 엔드포인트
            creator_private_key: 스마트 계약 생성자 private key
        """
        self.algod_token = ""
        self.algod_address = algod_endpoint
        self.client = algod.AlgodClient(self.algod_token, self.algod_address)
        self.creator_private_key = creator_private_key

    def store_verification_on_chain(self, verification_result: VerificationResult,
                                   verifier_private_key: str) -> Dict:
        """
        검증 결과를 블록체인에 저장

        Args:
            verification_result: 검증 결과
            verifier_private_key: 검증자 private key

        Returns:
            {
                'success': bool,
                'tx_id': str,
                'block': int,
                'verification_hash': str
            }
        """
        try:
            # 검증 데이터 해시 생성
            verification_hash = self._generate_verification_hash(verification_result)

            # 검증 데이터를 JSON으로 직렬화
            verification_data = {
                'result_id': verification_result.result_id,
                'measurement_id': verification_result.measurement_id,
                'approved': verification_result.approved,
                'carbon_verified': verification_result.carbon_savings_verified,
                'dc_verified': verification_result.dc_units_verified,
                'verified_by': verification_result.verified_by,
                'verified_at': verification_result.verified_at,
                'verification_hash': verification_hash
            }

            # Note 필드에 JSON 데이터 저장 (최대 1KB)
            note_json = json.dumps(verification_data)

            # 트랜잭션 파라미터
            params = self.client.suggested_params()

            # 검증자 주소
            verifier_address = account.address_from_private_key(verifier_private_key)

            # Payment 트랜잭션 생성 (0 ALGO, Note에 데이터 저장)
            txn = PaymentTxn(
                sender=verifier_address,
                sp=params,
                receiver=verifier_address,  # 자기 자신에게
                amt=0,  # 0 ALGO
                note=note_json.encode()
            )

            # 서명
            signed_txn = txn.sign(verifier_private_key)

            # 전송
            tx_id = self.client.send_transaction(signed_txn)

            # 확인 대기
            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            logger.info(f"Verification stored on-chain: {tx_id}, "
                       f"Result ID: {verification_result.result_id}")

            # 검증 결과에 TX ID 저장
            verification_result.blockchain_tx_id = tx_id

            return {
                'success': True,
                'tx_id': tx_id,
                'block': confirmed_txn['confirmed-round'],
                'verification_hash': verification_hash,
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{tx_id}"
            }

        except Exception as e:
            logger.error(f"Failed to store verification on-chain: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def retrieve_verification_from_chain(self, tx_id: str) -> Optional[Dict]:
        """
        블록체인에서 검증 기록 조회

        Args:
            tx_id: 트랜잭션 ID

        Returns:
            검증 데이터 또는 None
        """
        try:
            # 트랜잭션 정보 조회
            txn_info = self.client.pending_transaction_info(tx_id)

            # Note 필드에서 데이터 추출
            if 'txn' in txn_info and 'txn' in txn_info['txn']:
                note_b64 = txn_info['txn']['txn'].get('note')
                if note_b64:
                    import base64
                    note_bytes = base64.b64decode(note_b64)
                    note_json = note_bytes.decode()
                    verification_data = json.loads(note_json)

                    logger.info(f"Verification retrieved from chain: {tx_id}")

                    return verification_data

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve verification from chain: {e}")
            return None

    def verify_data_integrity(self, verification_data: Dict) -> Tuple[bool, str]:
        """
        블록체인 데이터 무결성 검증

        Args:
            verification_data: 검증 데이터

        Returns:
            (검증 성공 여부, 메시지)
        """
        try:
            # 저장된 해시
            stored_hash = verification_data.get('verification_hash')
            if not stored_hash:
                return False, "해시가 없습니다"

            # 데이터로부터 해시 재계산
            data_for_hash = {
                'result_id': verification_data['result_id'],
                'measurement_id': verification_data['measurement_id'],
                'approved': verification_data['approved'],
                'carbon_verified': verification_data['carbon_verified'],
                'dc_verified': verification_data['dc_verified'],
                'verified_by': verification_data['verified_by'],
                'verified_at': verification_data['verified_at']
            }

            calculated_hash = hashlib.sha256(
                json.dumps(data_for_hash, sort_keys=True).encode()
            ).hexdigest()

            # 해시 비교
            if stored_hash == calculated_hash:
                return True, "데이터 무결성 검증 성공"
            else:
                return False, "데이터가 변조되었습니다"

        except Exception as e:
            return False, f"검증 실패: {e}"

    def get_verification_history(self, wallet_address: str,
                                limit: int = 100) -> List[Dict]:
        """
        지갑 주소의 검증 이력 조회

        Args:
            wallet_address: 검증자 지갑 주소
            limit: 조회 개수 제한

        Returns:
            검증 이력 목록
        """
        try:
            # Algorand Indexer API가 필요 (여기서는 기본 구현)
            # 실제로는 indexer.search_transactions() 사용

            logger.info(f"Fetching verification history for {wallet_address}")

            # Placeholder
            return []

        except Exception as e:
            logger.error(f"Failed to fetch verification history: {e}")
            return []

    def create_verification_certificate_nft(self, verification_result: VerificationResult,
                                           creator_private_key: str) -> Dict:
        """
        검증 인증서 NFT 생성

        Args:
            verification_result: 검증 결과
            creator_private_key: 생성자 private key

        Returns:
            NFT 정보
        """
        try:
            from algosdk.transaction import AssetConfigTxn

            params = self.client.suggested_params()
            creator_address = account.address_from_private_key(creator_private_key)

            # NFT 메타데이터
            nft_metadata = {
                'name': f"Carbon Verification Certificate #{verification_result.result_id}",
                'description': f"Verified carbon reduction: {verification_result.carbon_savings_verified} kg CO₂",
                'properties': {
                    'measurement_id': verification_result.measurement_id,
                    'carbon_verified': verification_result.carbon_savings_verified,
                    'dc_verified': verification_result.dc_units_verified,
                    'verified_by': verification_result.verified_by,
                    'verified_at': verification_result.verified_at
                }
            }

            # NFT 생성 (ASA)
            txn = AssetConfigTxn(
                sender=creator_address,
                sp=params,
                total=1,  # NFT는 총 1개
                default_frozen=False,
                unit_name="CVCERT",
                asset_name=f"CV-{verification_result.result_id[:8]}",
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                url="https://pam-talk.com/verification-cert",
                decimals=0,
                note=json.dumps(nft_metadata).encode()
            )

            # 서명 및 전송
            signed_txn = txn.sign(creator_private_key)
            tx_id = self.client.send_transaction(signed_txn)

            # 확인 대기
            confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

            # Asset ID 추출
            asset_id = confirmed_txn['asset-index']

            logger.info(f"Verification certificate NFT created: {asset_id}")

            return {
                'success': True,
                'asset_id': asset_id,
                'tx_id': tx_id,
                'metadata': nft_metadata,
                'explorer_url': f"https://testnet.algoexplorer.io/asset/{asset_id}"
            }

        except Exception as e:
            logger.error(f"Failed to create verification certificate NFT: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def batch_store_verifications(self, verification_results: List[VerificationResult],
                                 verifier_private_key: str) -> List[Dict]:
        """
        여러 검증 결과 일괄 저장

        Args:
            verification_results: 검증 결과 목록
            verifier_private_key: 검증자 private key

        Returns:
            저장 결과 목록
        """
        results = []

        for verification in verification_results:
            result = self.store_verification_on_chain(verification, verifier_private_key)
            results.append(result)

            # Rate limiting (초당 최대 2 TPS)
            import time
            time.sleep(0.5)

        return results

    def generate_proof_of_verification(self, verification_result: VerificationResult) -> Dict:
        """
        검증 증명서 생성 (블록체인 기반)

        Args:
            verification_result: 검증 결과

        Returns:
            증명서 데이터
        """
        verification_hash = self._generate_verification_hash(verification_result)

        proof = {
            'proof_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'verification_summary': {
                'result_id': verification_result.result_id,
                'measurement_id': verification_result.measurement_id,
                'approved': verification_result.approved,
                'carbon_savings_verified': verification_result.carbon_savings_verified,
                'dc_units_verified': verification_result.dc_units_verified
            },
            'verification_details': {
                'verified_by': verification_result.verified_by,
                'verified_at': verification_result.verified_at,
                'verification_method': verification_result.verification_method,
                'evidence_verified': verification_result.evidence_verified,
                'data_integrity_verified': verification_result.data_integrity_verified,
                'calculation_verified': verification_result.calculation_verified
            },
            'blockchain_record': {
                'tx_id': verification_result.blockchain_tx_id,
                'verification_hash': verification_hash,
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{verification_result.blockchain_tx_id}" if verification_result.blockchain_tx_id else None
            },
            'verifier_comments': verification_result.verifier_comments
        }

        return proof

    def verify_proof_authenticity(self, proof: Dict) -> Tuple[bool, str]:
        """
        증명서 진위 확인

        Args:
            proof: 증명서 데이터

        Returns:
            (진위 여부, 메시지)
        """
        try:
            # 블록체인에서 데이터 조회
            tx_id = proof['blockchain_record']['tx_id']
            if not tx_id:
                return False, "블록체인 트랜잭션 ID가 없습니다"

            chain_data = self.retrieve_verification_from_chain(tx_id)
            if not chain_data:
                return False, "블록체인에서 데이터를 찾을 수 없습니다"

            # 해시 비교
            stored_hash = chain_data.get('verification_hash')
            proof_hash = proof['blockchain_record']['verification_hash']

            if stored_hash == proof_hash:
                # 데이터 무결성 검증
                is_valid, message = self.verify_data_integrity(chain_data)
                if is_valid:
                    return True, "증명서가 진짜이며 변조되지 않았습니다"
                else:
                    return False, f"데이터 무결성 검증 실패: {message}"
            else:
                return False, "해시가 일치하지 않습니다"

        except Exception as e:
            return False, f"검증 실패: {e}"

    def get_verification_audit_trail(self, measurement_id: str) -> List[Dict]:
        """
        측정 데이터의 전체 감사 추적 조회

        Args:
            measurement_id: 측정 ID

        Returns:
            감사 추적 목록
        """
        # 측정 → 검증 요청 → 검증 결과 → 블록체인 기록 전체 추적

        audit_trail = []

        # DB 또는 블록체인에서 조회
        logger.info(f"Fetching audit trail for measurement {measurement_id}")

        return audit_trail

    def _generate_verification_hash(self, verification_result: VerificationResult) -> str:
        """
        검증 결과 해시 생성

        Args:
            verification_result: 검증 결과

        Returns:
            SHA256 해시
        """
        hash_data = {
            'result_id': verification_result.result_id,
            'measurement_id': verification_result.measurement_id,
            'approved': verification_result.approved,
            'carbon_verified': verification_result.carbon_savings_verified,
            'dc_verified': verification_result.dc_units_verified,
            'verified_by': verification_result.verified_by,
            'verified_at': verification_result.verified_at
        }

        json_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get_blockchain_stats(self) -> Dict:
        """
        블록체인 저장 통계

        Returns:
            통계 정보
        """
        try:
            status = self.client.status()

            return {
                'network': 'testnet',
                'current_round': status['last-round'],
                'time_since_last_round': status.get('time-since-last-round', 0),
                'last_version': status.get('last-version', ''),
                'node_connected': True
            }

        except Exception as e:
            logger.error(f"Failed to get blockchain stats: {e}")
            return {
                'network': 'testnet',
                'node_connected': False,
                'error': str(e)
            }


# 사용 예시
if __name__ == "__main__":
    from committee_verification_workflow import VerificationResult

    # 블록체인 서비스 초기화
    blockchain_service = BlockchainVerificationService()

    # 검증 결과 예시
    verification_result = VerificationResult(
        result_id="VRS-20240115123456",
        request_id="VRQ-20240115123450",
        measurement_id="MRV-user123-20240115123400",
        approved=True,
        confidence_score_verified=85.5,
        carbon_savings_verified=5.2,
        dc_units_verified=6.24,
        verification_method="committee_review",
        verified_by="committee001",
        verified_at=datetime.now().isoformat(),
        checklist_results={
            'evidence_check': True,
            'data_integrity_check': True,
            'calculation_check': True
        },
        evidence_verified=True,
        data_integrity_verified=True,
        calculation_verified=True,
        verifier_comments="검증 완료. 모든 증빙이 확인되었습니다."
    )

    print("=== 블록체인 검증 서비스 ===")
    print(f"검증 결과 ID: {verification_result.result_id}")
    print(f"탄소 감축: {verification_result.carbon_savings_verified} kg")

    # 검증 증명서 생성
    proof = blockchain_service.generate_proof_of_verification(verification_result)
    print(f"\n증명서 생성 완료")
    print(f"검증 해시: {proof['blockchain_record']['verification_hash'][:16]}...")

    # 블록체인 통계
    stats = blockchain_service.get_blockchain_stats()
    print(f"\n블록체인 연결: {stats['node_connected']}")
    if stats['node_connected']:
        print(f"현재 라운드: {stats['current_round']}")
