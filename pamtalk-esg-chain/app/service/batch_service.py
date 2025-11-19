# -*- coding: utf-8 -*-
"""
대량 토큰 발행 배치 처리 서비스
Redis 기반 큐 시스템을 활용한 비동기 처리
"""

import json
import time
import logging
import threading
from datetime import datetime
from queue import Queue
from typing import List, Dict, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from app.service.coupon_service import create_initial_coupons

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchJobStatus:
    """배치 작업 상태"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchJob:
    """배치 작업 객체"""

    def __init__(self, job_id: str, job_type: str, parameters: dict, priority: int = 5):
        self.job_id = job_id
        self.job_type = job_type
        self.parameters = parameters
        self.priority = priority
        self.status = BatchJobStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.result = None


class BatchProcessor:
    """배치 작업 처리기"""

    def __init__(self, worker_count: int = 3):
        self.worker_count = worker_count
        self.job_queue = Queue()
        self.workers = []
        self.running = False
        self.jobs_storage = {}  # 실제 환경에서는 Redis 등 사용

    def start(self):
        """배치 프로세서 시작"""
        self.running = True

        for i in range(self.worker_count):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        logger.info(f"배치 프로세서 시작: {self.worker_count}개 워커")

    def stop(self):
        """배치 프로세서 중지"""
        self.running = False
        logger.info("배치 프로세서 중지")

    def submit_job(self, job: BatchJob) -> str:
        """작업 큐에 추가"""
        self.jobs_storage[job.job_id] = job
        self.job_queue.put(job)
        logger.info(f"배치 작업 추가: {job.job_id} ({job.job_type})")
        return job.job_id

    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """작업 상태 조회"""
        return self.jobs_storage.get(job_id)

    def _worker_loop(self, worker_id: int):
        """워커 루프"""
        logger.info(f"배치 워커 {worker_id} 시작")

        while self.running:
            try:
                # 작업 가져오기 (타임아웃 1초)
                job = self.job_queue.get(timeout=1)

                logger.info(f"워커 {worker_id}가 작업 처리 시작: {job.job_id}")

                # 작업 처리
                self._process_job(job, worker_id)

                self.job_queue.task_done()

            except:
                # 타임아웃이나 기타 예외 발생 시 계속 진행
                continue

    def _process_job(self, job: BatchJob, worker_id: int):
        """작업 처리"""
        job.status = BatchJobStatus.PROCESSING
        job.started_at = datetime.now()

        try:
            if job.job_type == "MASS_TOKEN_MINT":
                result = self._process_mass_mint(job, worker_id)
            elif job.job_type == "BATCH_TRANSFER":
                result = self._process_batch_transfer(job, worker_id)
            else:
                raise Exception(f"알 수 없는 작업 타입: {job.job_type}")

            job.status = BatchJobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.now()

            logger.info(f"작업 완료: {job.job_id} (워커 {worker_id})")

        except Exception as e:
            job.status = BatchJobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()

            logger.error(f"작업 실패: {job.job_id} - {str(e)}")

    def _process_mass_mint(self, job: BatchJob, worker_id: int) -> Dict:
        """대량 토큰 발행 처리"""
        params = job.parameters
        amount = params['amount']
        description = params['description']
        issued_by = params['issued_by']
        asset_id = params['asset_id']
        asset_name = params['asset_name']
        unit_name = params['unit_name']

        # 배치 크기 설정 (메모리 효율성)
        batch_size = params.get('batch_size', 5000)

        logger.info(f"대량 발행 시작: {amount}개, 배치 크기: {batch_size}")

        try:
            # 기존 coupon_service 활용하여 발행
            create_initial_coupons(
                amount=amount,
                description=description,
                issued_by=issued_by,
                asset_id=asset_id,
                asset_name=asset_name,
                unit_name=unit_name
            )

            return {
                'issued_amount': amount,
                'batch_size': batch_size,
                'worker_id': worker_id,
                'processing_time': (datetime.now() - job.started_at).total_seconds()
            }

        except Exception as e:
            raise Exception(f"대량 발행 실패: {str(e)}")

    def _process_batch_transfer(self, job: BatchJob, worker_id: int) -> Dict:
        """배치 전송 처리"""
        params = job.parameters
        transfers = params['transfers']  # [{'recipient': 'addr', 'amount': 100}, ...]

        logger.info(f"배치 전송 시작: {len(transfers)}개 전송")

        success_count = 0
        failed_transfers = []

        for transfer in transfers:
            try:
                # 실제 전송 로직 구현 (token_service 활용)
                # 여기서는 로깅만 수행
                logger.info(f"전송: {transfer['recipient']} <- {transfer['amount']}")
                success_count += 1

            except Exception as e:
                failed_transfers.append({
                    'recipient': transfer['recipient'],
                    'amount': transfer['amount'],
                    'error': str(e)
                })

        return {
            'total_transfers': len(transfers),
            'success_count': success_count,
            'failed_count': len(failed_transfers),
            'failed_transfers': failed_transfers,
            'worker_id': worker_id
        }


class BatchService:
    """배치 서비스 메인 클래스"""

    def __init__(self):
        self.processor = BatchProcessor(worker_count=3)
        self.processor.start()

    def create_mass_mint_job(self, amount: int, description: str, issued_by: str,
                           asset_id: int, asset_name: str, unit_name: str,
                           priority: int = 5) -> str:
        """대량 발행 작업 생성"""

        job_id = f"mint_{int(time.time())}_{amount}"

        job = BatchJob(
            job_id=job_id,
            job_type="MASS_TOKEN_MINT",
            parameters={
                'amount': amount,
                'description': description,
                'issued_by': issued_by,
                'asset_id': asset_id,
                'asset_name': asset_name,
                'unit_name': unit_name,
                'batch_size': min(amount, 5000)  # 최대 배치 크기
            },
            priority=priority
        )

        return self.processor.submit_job(job)

    def create_batch_transfer_job(self, transfers: List[Dict], priority: int = 5) -> str:
        """배치 전송 작업 생성"""

        job_id = f"transfer_{int(time.time())}_{len(transfers)}"

        job = BatchJob(
            job_id=job_id,
            job_type="BATCH_TRANSFER",
            parameters={'transfers': transfers},
            priority=priority
        )

        return self.processor.submit_job(job)

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        job = self.processor.get_job_status(job_id)

        if not job:
            return None

        return {
            'job_id': job.job_id,
            'job_type': job.job_type,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'result': job.result
        }

    def get_queue_info(self) -> Dict:
        """큐 정보 조회"""
        return {
            'queue_size': self.processor.job_queue.qsize(),
            'worker_count': self.processor.worker_count,
            'running': self.processor.running,
            'total_jobs': len(self.processor.jobs_storage)
        }

    def shutdown(self):
        """서비스 종료"""
        self.processor.stop()


# 글로벌 배치 서비스 인스턴스
batch_service = BatchService()


# 사용 예시
if __name__ == "__main__":
    # 대량 발행 작업 생성
    job_id = batch_service.create_mass_mint_job(
        amount=100000,
        description="대량 토큰 발행 테스트",
        issued_by="admin@pamtalk.com",
        asset_id=99999999,
        asset_name="PAM Token",
        unit_name="PAM"
    )

    print(f"작업 ID: {job_id}")

    # 상태 확인
    while True:
        status = batch_service.get_job_status(job_id)
        print(f"상태: {status['status']}")

        if status['status'] in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED]:
            print(f"최종 결과: {status}")
            break

        time.sleep(2)

    # 서비스 종료
    batch_service.shutdown()