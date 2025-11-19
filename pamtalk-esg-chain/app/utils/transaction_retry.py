# -*- coding: utf-8 -*-
"""
트랜잭션 재시도 및 타임아웃 처리 유틸리티
Algorand 블록체인 트랜잭션의 안정성 향상
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

from algosdk.v2client import algod
from algosdk.error import AlgodHTTPError

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """트랜잭션 관련 커스텀 예외"""
    pass


class RetryConfig:
    """재시도 설정"""

    def __init__(self,
                 max_attempts: int = 3,
                 initial_delay: float = 1.0,
                 max_delay: float = 30.0,
                 backoff_multiplier: float = 2.0,
                 timeout: float = 120.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.timeout = timeout


class TransactionRetry:
    """트랜잭션 재시도 처리 클래스"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()

    def retry_with_exponential_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """지수 백오프를 사용한 재시도"""

        last_exception = None
        delay = self.config.initial_delay
        start_time = time.time()

        for attempt in range(1, self.config.max_attempts + 1):
            # 타임아웃 확인
            if time.time() - start_time > self.config.timeout:
                raise TransactionError(f"작업 타임아웃 ({self.config.timeout}초 초과)")

            try:
                logger.info(f"트랜잭션 시도 {attempt}/{self.config.max_attempts}")
                result = func(*args, **kwargs)

                if attempt > 1:
                    logger.info(f"트랜잭션 성공 (시도 {attempt}회)")

                return result

            except Exception as e:
                last_exception = e

                # 재시도 불가능한 오류 확인
                if not self._is_retryable_error(e):
                    logger.error(f"재시도 불가능한 오류: {str(e)}")
                    raise e

                if attempt == self.config.max_attempts:
                    logger.error(f"최대 재시도 횟수 도달. 최종 오류: {str(e)}")
                    break

                # 백오프 대기
                logger.warning(f"시도 {attempt} 실패: {str(e)}. {delay:.1f}초 후 재시도...")
                time.sleep(delay)
                delay = min(delay * self.config.backoff_multiplier, self.config.max_delay)

        # 모든 시도 실패 시
        raise TransactionError(f"모든 재시도 실패. 최종 오류: {str(last_exception)}")

    def _is_retryable_error(self, error: Exception) -> bool:
        """재시도 가능한 오류인지 확인"""

        # Algorand 네트워크 관련 일시적 오류
        retryable_patterns = [
            "connection",
            "timeout",
            "network",
            "temporary",
            "rate limit",
            "429",  # Too Many Requests
            "502",  # Bad Gateway
            "503",  # Service Unavailable
            "504"   # Gateway Timeout
        ]

        error_str = str(error).lower()

        # HTTP 오류인 경우
        if isinstance(error, AlgodHTTPError):
            return error.code in [429, 502, 503, 504]

        # 일반 오류 메시지 패턴 확인
        return any(pattern in error_str for pattern in retryable_patterns)


def with_retry(config: RetryConfig = None):
    """재시도 데코레이터"""

    def decorator(func):
        retry_handler = TransactionRetry(config)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_handler.retry_with_exponential_backoff(func, *args, **kwargs)

        return wrapper

    return decorator


class AlgorandTransactionManager:
    """향상된 Algorand 트랜잭션 관리자"""

    def __init__(self, algod_client: algod.AlgodClient, retry_config: RetryConfig = None):
        self.algod_client = algod_client
        self.retry_handler = TransactionRetry(retry_config)

    @with_retry(RetryConfig(max_attempts=5, timeout=180))
    def send_transaction_with_confirmation(self, signed_txn, timeout: int = 60) -> dict:
        """트랜잭션 전송 및 확인 (재시도 포함)"""

        # 트랜잭션 전송
        tx_id = self.algod_client.send_transaction(signed_txn)
        logger.info(f"트랜잭션 전송됨: {tx_id}")

        # 확인 대기
        return self.wait_for_confirmation_with_retry(tx_id, timeout)

    @with_retry(RetryConfig(max_attempts=10, initial_delay=2.0))
    def wait_for_confirmation_with_retry(self, tx_id: str, timeout: int = 60) -> dict:
        """트랜잭션 확인 대기 (재시도 포함)"""

        start_time = time.time()
        last_round = self.algod_client.status()["last-round"]

        while time.time() - start_time < timeout:
            try:
                # 트랜잭션 상태 확인
                pending_info = self.algod_client.pending_transaction_info(tx_id)

                if pending_info.get("confirmed-round", 0) > 0:
                    logger.info(f"트랜잭션 확인됨: {tx_id} (라운드 {pending_info['confirmed-round']})")
                    return pending_info

                # 다음 라운드 대기
                self.algod_client.status_after_block(last_round + 1)
                last_round += 1

            except AlgodHTTPError as e:
                if e.code == 404:
                    # 트랜잭션이 아직 펜딩 상태가 아님
                    time.sleep(1)
                    continue
                else:
                    raise e

        raise TransactionError(f"트랜잭션 확인 타임아웃: {tx_id} (제한시간 {timeout}초)")

    @with_retry(RetryConfig(max_attempts=3))
    def get_account_info_safe(self, address: str) -> dict:
        """계정 정보 조회 (안전한 재시도 포함)"""
        try:
            return self.algod_client.account_info(address)
        except Exception as e:
            logger.error(f"계정 정보 조회 실패 ({address}): {str(e)}")
            raise

    @with_retry(RetryConfig(max_attempts=3))
    def get_suggested_params_safe(self) -> any:
        """트랜잭션 파라미터 조회 (안전한 재시도 포함)"""
        try:
            return self.algod_client.suggested_params()
        except Exception as e:
            logger.error(f"트랜잭션 파라미터 조회 실패: {str(e)}")
            raise

    def check_network_health(self) -> dict:
        """네트워크 상태 확인"""
        try:
            status = self.algod_client.status()
            health_info = {
                "healthy": True,
                "last_round": status.get("last-round"),
                "time_since_last_round": status.get("time-since-last-round"),
                "catchup_time": status.get("catchup-time"),
                "message": "네트워크 정상"
            }

            # 네트워크 지연 체크
            if status.get("time-since-last-round", 0) > 10:
                health_info["healthy"] = False
                health_info["message"] = "네트워크 지연 감지"

            return health_info

        except Exception as e:
            return {
                "healthy": False,
                "message": f"네트워크 상태 확인 실패: {str(e)}"
            }


# 사용 예시
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)

    # 테스트용 클라이언트 (실제 사용 시 실제 클라이언트 사용)
    # algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")

    # 사용 예시
    # tx_manager = AlgorandTransactionManager(algod_client)
    # health = tx_manager.check_network_health()
    # print(f"네트워크 상태: {health}")

    print("트랜잭션 재시도 유틸리티 로드 완료")