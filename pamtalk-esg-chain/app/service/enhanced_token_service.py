# -*- coding: utf-8 -*-
"""
향상된 토큰 서비스
재시도 로직과 타임아웃 처리가 개선된 토큰 전송 서비스
"""

import time
import psycopg2
from algosdk import account
from algosdk.transaction import AssetTransferTxn, PaymentTxn

from app.config import HCF_MNEMONIC, ASA_ID, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from app.utils.algorand_utils import get_algod_client
from app.utils.wallet_utils import get_wallet_keys, get_wallet_keys_from_address
from app.utils.transaction_retry import AlgorandTransactionManager, RetryConfig, with_retry


class EnhancedTokenService:
    """향상된 토큰 서비스"""

    def __init__(self):
        self.algod_client = get_algod_client()
        self.tx_manager = AlgorandTransactionManager(
            self.algod_client,
            RetryConfig(max_attempts=5, timeout=180)
        )

    @with_retry(RetryConfig(max_attempts=3, timeout=120))
    def opt_in_asset_enhanced(self, receiver_address: str, asset_id: int, table_name: str):
        """향상된 Opt-In 처리"""
        MIN_BALANCE_FOR_OPTIN = 210_000

        print(f"[향상된 Opt-In] 수신자: {receiver_address}")

        # 1. 수신자 지갑 키 조회
        rec_address, rec_private_key = get_wallet_keys_from_address(receiver_address, table_name)

        # 2. 협회 지갑 키 (충전용)
        sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)

        # 3. 네트워크 상태 확인
        network_health = self.tx_manager.check_network_health()
        if not network_health["healthy"]:
            raise Exception(f"네트워크 상태 불안정: {network_health['message']}")

        # 4. 수신자 잔액 확인
        rec_info = self.tx_manager.get_account_info_safe(receiver_address)
        rec_balance = rec_info.get("amount", 0)
        print(f"[수신자 현재 잔액] {rec_balance} microAlgos")

        # 5. 필요 시 ALGO 충전
        if rec_balance < MIN_BALANCE_FOR_OPTIN:
            print("[잔액 부족] 수신자에게 ALGO 자동 충전 중...")
            self._charge_algo_with_retry(sender_address, sender_private_key,
                                       receiver_address, MIN_BALANCE_FOR_OPTIN - rec_balance + 10_000)

        # 6. Opt-In 여부 재확인
        rec_info = self.tx_manager.get_account_info_safe(receiver_address)
        already_opted_in = any(asset['asset-id'] == asset_id for asset in rec_info.get('assets', []))

        if already_opted_in:
            print("[이미 Opt-In 되어 있음] 트랜잭션 생략")
            return "already_opted_in"

        # 7. Opt-In 트랜잭션 실행
        return self._execute_opt_in_transaction(rec_address, rec_private_key, asset_id)

    def _charge_algo_with_retry(self, sender_address: str, sender_private_key: str,
                              receiver_address: str, amount: int):
        """ALGO 충전 (재시도 포함)"""

        params = self.tx_manager.get_suggested_params_safe()
        params.flat_fee = True
        params.fee = 1000

        pay_txn = PaymentTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount
        )

        signed_pay_txn = pay_txn.sign(sender_private_key)

        # 재시도가 포함된 트랜잭션 전송
        confirmed_txn = self.tx_manager.send_transaction_with_confirmation(signed_pay_txn)
        print(f"[충전 완료] TX: {confirmed_txn.get('txn', {}).get('txn', '')}")

    def _execute_opt_in_transaction(self, receiver_address: str, receiver_private_key: str,
                                  asset_id: int) -> str:
        """Opt-In 트랜잭션 실행"""

        params = self.tx_manager.get_suggested_params_safe()
        params.flat_fee = True
        params.fee = 1000

        optin_txn = AssetTransferTxn(
            sender=receiver_address,
            sp=params,
            receiver=receiver_address,
            amt=0,
            index=asset_id
        )

        signed_optin_txn = optin_txn.sign(receiver_private_key)

        # 재시도가 포함된 트랜잭션 전송
        confirmed_txn = self.tx_manager.send_transaction_with_confirmation(signed_optin_txn)
        tx_id = confirmed_txn.get('txn', {}).get('txn', '')

        print(f"[Opt-In 성공] TXID: {tx_id}")
        return tx_id

    @with_retry(RetryConfig(max_attempts=5, timeout=300))
    def transfer_committee_token_enhanced(self, committee_id: int, amount: int) -> str:
        """향상된 위원회 토큰 전송"""

        print(f"[향상된 위원회 토큰 전송] ID: {committee_id}, 수량: {amount}")

        # 1. 네트워크 상태 확인
        network_health = self.tx_manager.check_network_health()
        if not network_health["healthy"]:
            raise Exception(f"네트워크 상태 불안정: {network_health['message']}")

        # 2. 협회 지갑 키 로드 및 검증
        sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)
        if sender_address != account.address_from_private_key(sender_private_key):
            raise Exception("HCF 지갑 주소와 프라이빗 키가 일치하지 않습니다.")

        # 3. DB 연결 및 위원회 정보 조회
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT wallet_address FROM committees WHERE id = %s", (committee_id,))
                result = cur.fetchone()
                if not result:
                    raise Exception("해당 committee_id에 대한 지갑 주소가 없습니다.")
                receiver_address = result[0]

            # 4. 수신자 Opt-In 확인 및 처리
            receiver_info = self.tx_manager.get_account_info_safe(receiver_address)
            opted_in = any(asset['asset-id'] == ASA_ID for asset in receiver_info.get("assets", []))

            if not opted_in:
                print("[Opt-In] 미등록 상태 → 자동 Opt-In 수행")
                self.opt_in_asset_enhanced(receiver_address, ASA_ID, "committees")
            else:
                print("[Opt-In] 이미 등록됨")

            # 5. 토큰 전송 트랜잭션 생성 및 실행
            tx_id = self._execute_token_transfer(sender_address, sender_private_key,
                                               receiver_address, amount)

            # 6. 데이터베이스 상태 업데이트 (재시도 포함)
            self._update_coupon_status_with_retry(conn, amount, committee_id, tx_id, "COMMITTEE")

            conn.commit()
            return tx_id

        except Exception as e:
            conn.rollback()
            print(f"[오류 발생] {str(e)}")
            raise Exception(f"토큰 전송 실패: {str(e)}")

        finally:
            conn.close()

    def _execute_token_transfer(self, sender_address: str, sender_private_key: str,
                              receiver_address: str, amount: int) -> str:
        """토큰 전송 트랜잭션 실행"""

        params = self.tx_manager.get_suggested_params_safe()
        params.flat_fee = True
        params.fee = 1000

        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount,
            index=ASA_ID
        )

        signed_txn = txn.sign(sender_private_key)

        if signed_txn.transaction.sender != sender_address:
            raise Exception("트랜잭션 서명자 주소 불일치")

        # 재시도가 포함된 트랜잭션 전송
        confirmed_txn = self.tx_manager.send_transaction_with_confirmation(signed_txn)
        tx_id = confirmed_txn.get('txn', {}).get('txn', '')

        print(f"[온체인 전송 완료] TX ID: {tx_id}")
        return tx_id

    @with_retry(RetryConfig(max_attempts=3))
    def _update_coupon_status_with_retry(self, conn, amount: int, entity_id: int,
                                       tx_id: str, status: str):
        """쿠폰 상태 업데이트 (재시도 포함)"""

        status_field_map = {
            "COMMITTEE": ("committee_id", "committee_assigned_at"),
            "PROVIDER": ("provider_id", "provider_assigned_at"),
            "CONSUMER": ("consumer_id", "consumer_assigned_at")
        }

        if status not in status_field_map:
            raise Exception(f"유효하지 않은 상태: {status}")

        id_field, timestamp_field = status_field_map[status]
        prev_status = {"COMMITTEE": "ISSUED", "PROVIDER": "COMMITTEE", "CONSUMER": "PROVIDER"}[status]

        with conn.cursor() as cur:
            cur.execute(f"""
                WITH to_update AS (
                    SELECT id
                    FROM esg_coupons
                    WHERE status = %s
                    ORDER BY id
                    LIMIT %s
                )
                UPDATE esg_coupons
                SET status = %s,
                    {id_field} = %s,
                    tx_hash = %s,
                    {timestamp_field} = NOW(),
                    updated_at = NOW()
                WHERE id IN (SELECT id FROM to_update)
                RETURNING id
            """, (prev_status, amount, status, entity_id, tx_id))

            updated_rows = cur.fetchall()
            updated_ids = [row[0] for row in updated_rows]
            print(f"[DB 업데이트 완료] {status} 쿠폰 ID: {updated_ids}")

            if len(updated_ids) != amount:
                raise Exception(f"업데이트 수량 불일치: 요청 {amount}, 실제 {len(updated_ids)}")


# 서비스 인스턴스 생성
enhanced_token_service = EnhancedTokenService()


# 사용 예시
if __name__ == "__main__":
    try:
        # 향상된 위원회 토큰 전송
        tx_id = enhanced_token_service.transfer_committee_token_enhanced(
            committee_id=1,
            amount=100
        )
        print(f"전송 완료: {tx_id}")

    except Exception as e:
        print(f"전송 실패: {str(e)}")