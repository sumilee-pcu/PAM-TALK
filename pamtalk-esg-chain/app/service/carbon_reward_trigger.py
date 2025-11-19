# -*- coding: utf-8 -*-
"""
탄소 절약 보상 자동 트리거 시스템
탄소 절약 활동 감지 시 자동으로 토큰 발행 및 분배 처리
"""

import asyncio
import time
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.service.carbon_tracking_service import carbon_tracking_service
from app.service.batch_service import batch_service
from app.service.enhanced_token_service import enhanced_token_service
from app.service.smart_contract_service import SmartContractService
from app.utils.db_pool import db_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RewardTriggerConfig:
    """보상 트리거 설정"""
    min_carbon_savings: float = 0.5  # 최소 절약량 (kg CO2)
    max_daily_tokens_per_user: int = 500  # 사용자당 일일 최대 토큰
    batch_processing_interval: int = 300  # 배치 처리 간격 (초)
    auto_verification_threshold: float = 5.0  # 자동 검증 임계값
    manual_review_threshold: float = 50.0  # 수동 검토 필요 임계값


class CarbonRewardTrigger:
    """탄소 보상 자동 트리거"""

    def __init__(self, config: RewardTriggerConfig = None):
        self.config = config or RewardTriggerConfig()
        self.carbon_service = carbon_tracking_service
        self.batch_service = batch_service
        self.token_service = enhanced_token_service
        self.smart_contract_service = SmartContractService()
        self.db = db_service

        # 처리 상태 추적
        self.processing_active = False
        self.last_processed_time = datetime.now()

    async def start_monitoring(self):
        """탄소 보상 모니터링 시작"""
        logger.info("탄소 보상 자동 트리거 시작")
        self.processing_active = True

        while self.processing_active:
            try:
                await self.process_pending_rewards()
                await asyncio.sleep(self.config.batch_processing_interval)

            except Exception as e:
                logger.error(f"보상 처리 중 오류: {str(e)}")
                await asyncio.sleep(60)  # 오류 시 1분 대기

    async def stop_monitoring(self):
        """모니터링 중지"""
        logger.info("탄소 보상 자동 트리거 중지")
        self.processing_active = False

    async def process_pending_rewards(self):
        """대기 중인 보상 처리"""
        logger.info("대기 중인 보상 처리 시작")

        # 1. 미처리 활동 조회
        pending_activities = self._get_pending_reward_activities()

        if not pending_activities:
            logger.info("처리할 보상이 없습니다.")
            return

        logger.info(f"{len(pending_activities)}개의 보상 대기 활동 발견")

        # 2. 활동별 보상 처리
        processed_count = 0
        failed_count = 0

        for activity in pending_activities:
            try:
                success = await self._process_single_activity_reward(activity)
                if success:
                    processed_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"활동 {activity['id']} 보상 처리 실패: {str(e)}")
                failed_count += 1

        # 3. 배치 토큰 발행 처리
        await self._process_batch_token_minting()

        logger.info(f"보상 처리 완료: 성공 {processed_count}, 실패 {failed_count}")

    async def _process_single_activity_reward(self, activity: Dict) -> bool:
        """단일 활동 보상 처리"""
        activity_id = activity['id']
        user_id = activity['user_id']
        carbon_savings = float(activity['carbon_savings'])
        token_amount = int(activity['token_reward_amount'])

        logger.info(f"활동 보상 처리: 사용자 {user_id}, 절약량 {carbon_savings}kg, 토큰 {token_amount}개")

        try:
            # 1. 일일 토큰 제한 확인
            if not self._check_daily_token_limit(user_id, token_amount):
                logger.warning(f"사용자 {user_id} 일일 토큰 제한 초과")
                return False

            # 2. 자동 검증 처리
            verification_result = await self._verify_carbon_activity(activity)

            if not verification_result['verified']:
                logger.warning(f"활동 {activity_id} 검증 실패: {verification_result['reason']}")
                await self._mark_for_manual_review(activity_id, verification_result['reason'])
                return False

            # 3. 스마트계약에 탄소 절약량 기록
            if hasattr(self, 'smart_contract_app_id'):
                await self._record_carbon_savings_on_chain(
                    user_id, carbon_savings, activity['activity_type']
                )

            # 4. 보상 기록 생성
            reward_id = await self._create_reward_record(
                user_id, activity_id, carbon_savings, token_amount
            )

            # 5. 활동 검증 완료 처리
            await self._mark_activity_verified(activity_id, reward_id)

            logger.info(f"활동 {activity_id} 보상 처리 완료 (보상 ID: {reward_id})")
            return True

        except Exception as e:
            logger.error(f"활동 {activity_id} 보상 처리 실패: {str(e)}")
            return False

    async def _verify_carbon_activity(self, activity: Dict) -> Dict:
        """탄소 활동 자동 검증"""
        carbon_savings = float(activity['carbon_savings'])
        reduction_percentage = float(activity['reduction_percentage'])

        # 1. 기본 유효성 검증
        if carbon_savings < self.config.min_carbon_savings:
            return {
                'verified': False,
                'reason': f'최소 절약량 미달 ({carbon_savings}kg < {self.config.min_carbon_savings}kg)'
            }

        # 2. 과도한 절약량 검증
        if carbon_savings > self.config.manual_review_threshold:
            return {
                'verified': False,
                'reason': f'과도한 절약량으로 수동 검토 필요 ({carbon_savings}kg)'
            }

        # 3. 비정상적인 절약 비율 검증
        if reduction_percentage > 95:
            return {
                'verified': False,
                'reason': f'비정상적인 절약 비율 ({reduction_percentage}%)'
            }

        # 4. 지역별 거리 검증
        origin = activity['origin_region']
        destination = activity['destination_region']

        if origin and destination:
            if not self._validate_regional_distance(origin, destination):
                return {
                    'verified': False,
                    'reason': f'비정상적인 지역 간 거리 ({origin} -> {destination})'
                }

        # 5. 사용자 활동 패턴 검증
        user_pattern_valid = await self._validate_user_activity_pattern(
            activity['user_id'], activity['activity_type'], carbon_savings
        )

        if not user_pattern_valid:
            return {
                'verified': False,
                'reason': '비정상적인 사용자 활동 패턴 감지'
            }

        # 6. 자동 검증 통과
        return {
            'verified': True,
            'reason': '자동 검증 통과',
            'verification_score': self._calculate_verification_score(activity)
        }

    async def _validate_user_activity_pattern(self, user_id: str, activity_type: str,
                                            carbon_savings: float) -> bool:
        """사용자 활동 패턴 검증"""

        # 최근 7일간 동일 사용자의 유사 활동 조회
        query = """
            SELECT carbon_savings, activity_date
            FROM carbon_activities
            WHERE user_id = %s
            AND activity_type = %s
            AND activity_date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY activity_date DESC
        """

        recent_activities = self.db.pool.execute_query(query, (user_id, activity_type))

        if not recent_activities:
            return True  # 첫 활동은 통과

        # 평균 절약량 계산
        total_savings = sum(float(act['carbon_savings']) for act in recent_activities)
        avg_savings = total_savings / len(recent_activities)

        # 현재 활동이 평균의 10배를 초과하는지 확인
        if carbon_savings > avg_savings * 10:
            logger.warning(f"사용자 {user_id} 비정상 패턴: 현재 {carbon_savings}kg, 평균 {avg_savings}kg")
            return False

        # 일일 활동 빈도 확인 (하루 20회 초과 시 의심)
        today_activities = [act for act in recent_activities
                           if act['activity_date'] == date.today()]

        if len(today_activities) > 20:
            logger.warning(f"사용자 {user_id} 일일 활동 과다: {len(today_activities)}회")
            return False

        return True

    def _validate_regional_distance(self, origin: str, destination: str) -> bool:
        """지역 간 거리 유효성 검증"""
        # 동일 지역인 경우
        if origin == destination:
            return True

        # 알려진 거리 매트릭스에서 확인
        from app.service.carbon_calculation_engine import DISTANCE_MATRIX

        key1 = (origin, destination)
        key2 = (destination, origin)

        distance = None
        if key1 in DISTANCE_MATRIX:
            distance = DISTANCE_MATRIX[key1]
        elif key2 in DISTANCE_MATRIX:
            distance = DISTANCE_MATRIX[key2]

        # 거리가 1000km를 초과하면 의심스러운 것으로 판단
        if distance and distance > 1000:
            return False

        return True

    def _calculate_verification_score(self, activity: Dict) -> float:
        """검증 점수 계산 (0-100)"""
        score = 100.0

        # 절약량에 따른 점수 차감
        carbon_savings = float(activity['carbon_savings'])
        if carbon_savings > 20:
            score -= 20
        elif carbon_savings > 10:
            score -= 10

        # 절약 비율에 따른 점수 차감
        reduction_percentage = float(activity['reduction_percentage'])
        if reduction_percentage > 80:
            score -= 15
        elif reduction_percentage > 60:
            score -= 5

        return max(0, score)

    def _check_daily_token_limit(self, user_id: str, token_amount: int) -> bool:
        """일일 토큰 제한 확인"""

        query = """
            SELECT COALESCE(SUM(token_amount), 0) as daily_tokens
            FROM carbon_reward_history
            WHERE user_id = %s
            AND DATE(created_at) = CURRENT_DATE
            AND status != 'rejected'
        """

        result = self.db.pool.execute_query(query, (user_id,), fetch='one')
        daily_tokens = int(result['daily_tokens'])

        return (daily_tokens + token_amount) <= self.config.max_daily_tokens_per_user

    async def _record_carbon_savings_on_chain(self, user_id: str, carbon_savings: float,
                                            activity_type: str):
        """스마트계약에 탄소 절약량 기록"""
        try:
            # 스마트계약 앱 ID가 설정되어 있는 경우에만 실행
            app_id = getattr(self, 'smart_contract_app_id', None)
            if not app_id:
                return

            # 사용자 지갑 정보 조회 (실제 구현 시 필요)
            user_mnemonic = None  # 실제로는 사용자 지갑에서 조회

            if user_mnemonic:
                result = self.smart_contract_service.record_carbon_savings(
                    app_id=app_id,
                    carbon_amount=int(carbon_savings * 1000),  # g 단위로 변환
                    activity_type=activity_type,
                    user_mnemonic=user_mnemonic
                )

                logger.info(f"스마트계약 기록 완료: {result['tx_id']}")

        except Exception as e:
            logger.error(f"스마트계약 기록 실패: {str(e)}")
            # 스마트계약 기록 실패는 전체 프로세스를 중단하지 않음

    async def _create_reward_record(self, user_id: str, activity_id: int,
                                   carbon_savings: float, token_amount: int) -> int:
        """보상 기록 생성"""

        query = """
            INSERT INTO carbon_reward_history
            (user_id, source_type, source_id, carbon_savings, token_amount, status)
            VALUES (%s, 'activity', %s, %s, %s, 'approved')
            RETURNING id
        """

        result = self.db.pool.execute_query(
            query, (user_id, activity_id, carbon_savings, token_amount), fetch='one'
        )

        return result['id']

    async def _mark_activity_verified(self, activity_id: int, reward_id: int):
        """활동 검증 완료 표시"""

        query = """
            UPDATE carbon_activities
            SET verified = TRUE,
                verified_by = 'auto_system',
                verified_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        self.db.pool.execute_query(query, (activity_id,), fetch=None)

    async def _mark_for_manual_review(self, activity_id: int, reason: str):
        """수동 검토 대상으로 표시"""

        query = """
            UPDATE carbon_activities
            SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
            WHERE id = %s
        """

        metadata = json.dumps({
            'manual_review_required': True,
            'review_reason': reason,
            'review_requested_at': datetime.now().isoformat()
        })

        self.db.pool.execute_query(query, (metadata, activity_id), fetch=None)

    async def _process_batch_token_minting(self):
        """배치 토큰 발행 처리"""

        # 승인된 보상 중 아직 토큰이 발행되지 않은 것들 조회
        query = """
            SELECT
                user_id,
                SUM(token_amount) as total_tokens,
                COUNT(*) as reward_count
            FROM carbon_reward_history
            WHERE status = 'approved'
            AND mint_tx_hash IS NULL
            GROUP BY user_id
            HAVING SUM(token_amount) >= 10  -- 최소 10토큰 이상일 때만 발행
        """

        pending_rewards = self.db.pool.execute_query(query)

        if not pending_rewards:
            logger.info("발행할 토큰이 없습니다.")
            return

        logger.info(f"{len(pending_rewards)}명의 사용자에게 토큰 발행 예정")

        for reward in pending_rewards:
            try:
                await self._mint_tokens_for_user(
                    reward['user_id'],
                    int(reward['total_tokens'])
                )

            except Exception as e:
                logger.error(f"사용자 {reward['user_id']} 토큰 발행 실패: {str(e)}")

    async def _mint_tokens_for_user(self, user_id: str, token_amount: int):
        """특정 사용자에게 토큰 발행"""

        # 대량 발행 배치 작업 생성
        job_id = batch_service.create_mass_mint_job(
            amount=token_amount,
            description=f"탄소 절약 보상 토큰 ({user_id})",
            issued_by="carbon_reward_system",
            asset_id=int(os.getenv("ASA_ID")),
            asset_name=os.getenv("ASA_NAME", "PAM Token"),
            unit_name="CARBON"
        )

        logger.info(f"사용자 {user_id} 토큰 발행 작업 생성: {job_id}")

        # 보상 기록에 발행 작업 ID 업데이트
        update_query = """
            UPDATE carbon_reward_history
            SET status = 'minting',
                mint_tx_hash = %s
            WHERE user_id = %s
            AND status = 'approved'
            AND mint_tx_hash IS NULL
        """

        self.db.pool.execute_query(update_query, (job_id, user_id), fetch=None)

    def _get_pending_reward_activities(self) -> List[Dict]:
        """대기 중인 보상 활동 조회"""

        query = """
            SELECT *
            FROM carbon_activities
            WHERE token_reward_eligible = TRUE
            AND verified = FALSE
            AND carbon_savings >= %s
            AND created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            ORDER BY created_at ASC
            LIMIT 100
        """

        results = self.db.pool.execute_query(
            query, (self.config.min_carbon_savings,)
        )

        return [dict(record) for record in results]


# 서비스 인스턴스
carbon_reward_trigger = CarbonRewardTrigger()


# 사용 예시 (비동기 실행)
async def main():
    """메인 실행 함수"""
    try:
        # 보상 트리거 시작
        await carbon_reward_trigger.start_monitoring()

    except KeyboardInterrupt:
        logger.info("사용자에 의한 중단")
        await carbon_reward_trigger.stop_monitoring()

    except Exception as e:
        logger.error(f"시스템 오류: {str(e)}")


if __name__ == "__main__":
    # 비동기 이벤트 루프 실행
    asyncio.run(main())