# -*- coding: utf-8 -*-
"""
탄소 추적 서비스
사용자별 탄소 활동 기록, 통계 및 보상 관리
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from app.utils.db_pool import db_service
from app.service.carbon_calculation_engine import (
    CarbonCalculationEngine, CarbonActivity, ActivityType, CarbonCalculationResult
)


class CarbonTrackingService:
    """탄소 추적 및 관리 서비스"""

    def __init__(self):
        self.calculation_engine = CarbonCalculationEngine()
        self.db = db_service

    def create_carbon_profile(self, user_id: str, email: str, name: str,
                            region: str, **profile_data) -> int:
        """사용자 탄소 프로필 생성"""

        query = """
            INSERT INTO carbon_profiles
            (user_id, email, name, region, household_size, lifestyle_type,
             preferred_transport, carbon_reduction_goal, monthly_token_goal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            user_id, email, name, region,
            profile_data.get('household_size', 1),
            profile_data.get('lifestyle_type', 'standard'),
            profile_data.get('preferred_transport', 'mixed'),
            profile_data.get('carbon_reduction_goal', 10.0),
            profile_data.get('monthly_token_goal', 100)
        )

        result = self.db.pool.execute_query(query, params, fetch='one')

        # 기준 배출량 초기 계산
        self._calculate_baseline_emissions(user_id, region, profile_data)

        return result['id']

    def record_carbon_activity(self, user_id: str, activity_data: Dict) -> int:
        """탄소 활동 기록"""

        # 탄소 활동 객체 생성
        activity = CarbonActivity(
            activity_type=ActivityType(activity_data['activity_type']),
            user_id=user_id,
            product_name=activity_data.get('product_name', ''),
            quantity=float(activity_data.get('quantity', 0)),
            origin_region=activity_data.get('origin_region', ''),
            destination_region=activity_data.get('destination_region', ''),
            farming_method=activity_data.get('farming_method', 'conventional'),
            transport_method=activity_data.get('transport_method', 'truck_medium'),
            packaging_type=activity_data.get('packaging_type', 'plastic'),
            activity_date=activity_data.get('activity_date', date.today().isoformat()),
            metadata=activity_data.get('metadata', {})
        )

        # 탄소 발자국 계산
        result = self.calculation_engine.calculate_carbon_footprint(activity)

        # 데이터베이스에 기록
        activity_id = self._store_activity_record(activity, result)

        # 월간 통계 업데이트
        self._update_monthly_stats(user_id, activity, result)

        # 챌린지 진행 상황 업데이트
        self._update_challenge_progress(user_id, activity, result)

        return activity_id

    def _store_activity_record(self, activity: CarbonActivity,
                              result: CarbonCalculationResult) -> int:
        """활동 기록을 데이터베이스에 저장"""

        query = """
            INSERT INTO carbon_activities
            (user_id, activity_type, product_name, quantity, origin_region,
             destination_region, farming_method, transport_method, packaging_type,
             total_emissions, transport_emissions, production_emissions,
             packaging_emissions, baseline_emissions, carbon_savings,
             reduction_percentage, token_reward_eligible, token_reward_amount,
             metadata, activity_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            activity.user_id, activity.activity_type.value, activity.product_name,
            activity.quantity, activity.origin_region, activity.destination_region,
            activity.farming_method, activity.transport_method, activity.packaging_type,
            result.total_emissions, result.transport_emissions,
            result.production_emissions, result.packaging_emissions,
            result.baseline_emissions, result.carbon_savings,
            result.reduction_percentage, result.token_reward_eligible,
            result.reward_amount, json.dumps(activity.metadata or {}),
            activity.activity_date
        )

        record = self.db.pool.execute_query(query, params, fetch='one')
        return record['id']

    def get_user_carbon_profile(self, user_id: str) -> Optional[Dict]:
        """사용자 탄소 프로필 조회"""

        query = """
            SELECT * FROM carbon_profiles WHERE user_id = %s
        """

        result = self.db.pool.execute_query(query, (user_id,), fetch='one')
        return dict(result) if result else None

    def get_user_activities(self, user_id: str, limit: int = 50,
                           activity_type: str = None,
                           start_date: str = None, end_date: str = None) -> List[Dict]:
        """사용자 활동 기록 조회"""

        conditions = ["user_id = %s"]
        params = [user_id]

        if activity_type:
            conditions.append("activity_type = %s")
            params.append(activity_type)

        if start_date:
            conditions.append("activity_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("activity_date <= %s")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT * FROM carbon_activities
            WHERE {where_clause}
            ORDER BY activity_date DESC, created_at DESC
            LIMIT %s
        """

        params.append(limit)
        results = self.db.pool.execute_query(query, tuple(params))

        return [dict(record) for record in results]

    def get_user_carbon_statistics(self, user_id: str, year: int = None,
                                  month: int = None) -> Dict:
        """사용자 탄소 통계 조회"""

        if year and month:
            # 특정 월 통계
            query = """
                SELECT * FROM carbon_monthly_stats
                WHERE user_id = %s AND year = %s AND month = %s
            """
            result = self.db.pool.execute_query(query, (user_id, year, month), fetch='one')

            if result:
                return dict(result)

        # 전체 통계 계산
        query = """
            SELECT
                COUNT(*) as total_activities,
                COALESCE(SUM(total_emissions), 0) as total_emissions,
                COALESCE(SUM(baseline_emissions), 0) as total_baseline_emissions,
                COALESCE(SUM(carbon_savings), 0) as total_carbon_savings,
                COALESCE(AVG(reduction_percentage), 0) as average_reduction_percentage,
                COALESCE(SUM(CASE WHEN token_reward_eligible THEN token_reward_amount ELSE 0 END), 0) as total_potential_tokens
            FROM carbon_activities
            WHERE user_id = %s
        """

        if year:
            query += " AND EXTRACT(YEAR FROM activity_date) = %s"
            params = (user_id, year)
        else:
            params = (user_id,)

        result = self.db.pool.execute_query(query, params, fetch='one')

        return dict(result) if result else {}

    def create_carbon_challenge(self, challenge_data: Dict) -> int:
        """탄소 챌린지 생성"""

        query = """
            INSERT INTO carbon_challenges
            (challenge_name, description, challenge_type, target_activity_type,
             target_savings_amount, target_activities_count, min_reduction_percentage,
             reward_tokens, bonus_multiplier, start_date, end_date, max_participants)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            challenge_data['challenge_name'],
            challenge_data.get('description', ''),
            challenge_data['challenge_type'],
            challenge_data.get('target_activity_type'),
            challenge_data.get('target_savings_amount'),
            challenge_data.get('target_activities_count'),
            challenge_data.get('min_reduction_percentage'),
            challenge_data['reward_tokens'],
            challenge_data.get('bonus_multiplier', 1.0),
            challenge_data['start_date'],
            challenge_data['end_date'],
            challenge_data.get('max_participants')
        )

        result = self.db.pool.execute_query(query, params, fetch='one')
        return result['id']

    def join_challenge(self, user_id: str, challenge_id: int) -> bool:
        """챌린지 참여"""

        try:
            # 챌린지 정보 확인
            challenge = self._get_challenge_info(challenge_id)
            if not challenge or not challenge['active']:
                return False

            # 참여자 수 확인
            if (challenge['max_participants'] and
                challenge['current_participants'] >= challenge['max_participants']):
                return False

            # 이미 참여 중인지 확인
            existing = self._check_user_challenge_participation(user_id, challenge_id)
            if existing:
                return False

            # 참여 기록 생성
            join_query = """
                INSERT INTO user_challenge_participations
                (user_id, challenge_id, participation_status)
                VALUES (%s, %s, 'active')
            """

            # 챌린지 참여자 수 업데이트
            update_query = """
                UPDATE carbon_challenges
                SET current_participants = current_participants + 1
                WHERE id = %s
            """

            # 트랜잭션으로 실행
            queries = [
                {'query': join_query, 'params': (user_id, challenge_id)},
                {'query': update_query, 'params': (challenge_id,)}
            ]

            self.db.pool.execute_transaction(queries)
            return True

        except Exception as e:
            print(f"챌린지 참여 실패: {str(e)}")
            return False

    def get_active_challenges(self, limit: int = 10) -> List[Dict]:
        """활성 챌린지 목록 조회"""

        query = """
            SELECT * FROM carbon_challenges
            WHERE active = TRUE
            AND start_date <= CURRENT_DATE
            AND end_date >= CURRENT_DATE
            ORDER BY created_at DESC
            LIMIT %s
        """

        results = self.db.pool.execute_query(query, (limit,))
        return [dict(record) for record in results]

    def get_user_challenges(self, user_id: str) -> List[Dict]:
        """사용자 참여 챌린지 조회"""

        query = """
            SELECT
                ucp.*,
                cc.challenge_name,
                cc.description,
                cc.challenge_type,
                cc.reward_tokens,
                cc.start_date,
                cc.end_date
            FROM user_challenge_participations ucp
            JOIN carbon_challenges cc ON ucp.challenge_id = cc.id
            WHERE ucp.user_id = %s
            ORDER BY ucp.joined_at DESC
        """

        results = self.db.pool.execute_query(query, (user_id,))
        return [dict(record) for record in results]

    def process_pending_rewards(self, user_id: str) -> Dict:
        """대기 중인 보상 처리"""

        # 승인되지 않은 활동 보상 조회
        query = """
            SELECT
                id,
                carbon_savings,
                token_reward_amount
            FROM carbon_activities
            WHERE user_id = %s
            AND token_reward_eligible = TRUE
            AND token_reward_claimed = FALSE
            AND verified = TRUE
        """

        activities = self.db.pool.execute_query(query, (user_id,))

        total_tokens = 0
        activity_ids = []

        for activity in activities:
            total_tokens += activity['token_reward_amount']
            activity_ids.append(activity['id'])

        if total_tokens > 0:
            # 보상 히스토리에 기록
            reward_id = self._create_reward_record(user_id, total_tokens, 'activity', activity_ids)

            return {
                'success': True,
                'total_tokens': total_tokens,
                'activities_count': len(activity_ids),
                'reward_id': reward_id
            }

        return {
            'success': False,
            'message': '처리할 보상이 없습니다.'
        }

    def _calculate_baseline_emissions(self, user_id: str, region: str, profile_data: Dict):
        """사용자 기준 배출량 계산"""
        # 지역별, 가구 규모별 평균 배출량 계산 로직
        # 실제로는 통계 데이터 기반으로 계산

        household_size = profile_data.get('household_size', 1)
        lifestyle = profile_data.get('lifestyle_type', 'standard')

        # 한국 평균 가구당 월간 탄소 배출량 (대략적)
        base_emissions = {
            'eco': 250,      # kg CO2/month
            'standard': 350,  # kg CO2/month
            'premium': 450   # kg CO2/month
        }

        monthly_baseline = base_emissions.get(lifestyle, 350) * household_size

        # 프로필 업데이트
        update_query = """
            UPDATE carbon_profiles
            SET baseline_monthly_emissions = %s
            WHERE user_id = %s
        """

        self.db.pool.execute_query(update_query, (monthly_baseline, user_id), fetch=None)

    def _update_monthly_stats(self, user_id: str, activity: CarbonActivity,
                             result: CarbonCalculationResult):
        """월간 통계 업데이트"""

        activity_date = datetime.strptime(activity.activity_date, '%Y-%m-%d')
        year = activity_date.year
        month = activity_date.month

        # 기존 통계 조회
        query = """
            SELECT * FROM carbon_monthly_stats
            WHERE user_id = %s AND year = %s AND month = %s
        """

        existing = self.db.pool.execute_query(query, (user_id, year, month), fetch='one')

        if existing:
            # 업데이트
            update_query = """
                UPDATE carbon_monthly_stats
                SET total_activities = total_activities + 1,
                    total_emissions = total_emissions + %s,
                    total_baseline_emissions = total_baseline_emissions + %s,
                    total_carbon_savings = total_carbon_savings + %s,
                    total_tokens_earned = total_tokens_earned + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND year = %s AND month = %s
            """

            params = (
                result.total_emissions, result.baseline_emissions,
                result.carbon_savings, result.reward_amount,
                user_id, year, month
            )

        else:
            # 새로 생성
            update_query = """
                INSERT INTO carbon_monthly_stats
                (user_id, year, month, total_activities, total_emissions,
                 total_baseline_emissions, total_carbon_savings, total_tokens_earned)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                user_id, year, month, 1, result.total_emissions,
                result.baseline_emissions, result.carbon_savings, result.reward_amount
            )

        self.db.pool.execute_query(update_query, params, fetch=None)

    def _update_challenge_progress(self, user_id: str, activity: CarbonActivity,
                                  result: CarbonCalculationResult):
        """챌린지 진행 상황 업데이트"""

        # 사용자의 활성 챌린지 조회
        query = """
            SELECT ucp.id, ucp.challenge_id, cc.target_activity_type,
                   cc.target_savings_amount, cc.target_activities_count
            FROM user_challenge_participations ucp
            JOIN carbon_challenges cc ON ucp.challenge_id = cc.id
            WHERE ucp.user_id = %s
            AND ucp.participation_status = 'active'
            AND cc.active = TRUE
        """

        participations = self.db.pool.execute_query(query, (user_id,))

        for participation in participations:
            # 챌린지 조건 확인
            target_activity = participation['target_activity_type']
            if target_activity and target_activity != activity.activity_type.value:
                continue

            # 진행 상황 업데이트
            update_query = """
                UPDATE user_challenge_participations
                SET current_savings = current_savings + %s,
                    current_activities = current_activities + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            self.db.pool.execute_query(
                update_query,
                (result.carbon_savings, participation['id']),
                fetch=None
            )

            # 목표 달성 확인
            self._check_challenge_completion(participation['id'])

    def _check_challenge_completion(self, participation_id: int):
        """챌린지 완료 여부 확인"""

        # 참여 정보 및 챌린지 조건 조회
        query = """
            SELECT ucp.*, cc.target_savings_amount, cc.target_activities_count,
                   cc.reward_tokens
            FROM user_challenge_participations ucp
            JOIN carbon_challenges cc ON ucp.challenge_id = cc.id
            WHERE ucp.id = %s
        """

        participation = self.db.pool.execute_query(query, (participation_id,), fetch='one')

        if not participation:
            return

        # 완료 조건 확인
        target_savings = participation['target_savings_amount']
        target_activities = participation['target_activities_count']

        savings_achieved = (not target_savings or
                           participation['current_savings'] >= target_savings)
        activities_achieved = (not target_activities or
                              participation['current_activities'] >= target_activities)

        if savings_achieved and activities_achieved:
            # 챌린지 완료 처리
            update_query = """
                UPDATE user_challenge_participations
                SET participation_status = 'completed',
                    target_achieved = TRUE,
                    completion_date = CURRENT_TIMESTAMP,
                    reward_tokens = %s
                WHERE id = %s
            """

            self.db.pool.execute_query(
                update_query,
                (participation['reward_tokens'], participation_id),
                fetch=None
            )

    def _get_challenge_info(self, challenge_id: int) -> Optional[Dict]:
        """챌린지 정보 조회"""
        query = "SELECT * FROM carbon_challenges WHERE id = %s"
        result = self.db.pool.execute_query(query, (challenge_id,), fetch='one')
        return dict(result) if result else None

    def _check_user_challenge_participation(self, user_id: str, challenge_id: int) -> bool:
        """사용자 챌린지 참여 여부 확인"""
        query = """
            SELECT id FROM user_challenge_participations
            WHERE user_id = %s AND challenge_id = %s
        """
        result = self.db.pool.execute_query(query, (user_id, challenge_id), fetch='one')
        return result is not None

    def _create_reward_record(self, user_id: str, token_amount: int,
                             source_type: str, source_ids: List[int]) -> int:
        """보상 기록 생성"""

        query = """
            INSERT INTO carbon_reward_history
            (user_id, source_type, token_amount, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING id
        """

        result = self.db.pool.execute_query(
            query, (user_id, source_type, token_amount), fetch='one'
        )

        return result['id']


# 서비스 인스턴스
carbon_tracking_service = CarbonTrackingService()


# 사용 예시
if __name__ == "__main__":
    service = carbon_tracking_service

    # 테스트 사용자 프로필 생성
    try:
        profile_id = service.create_carbon_profile(
            user_id="test_user_123",
            email="test@example.com",
            name="테스트 사용자",
            region="서울시",
            household_size=2,
            lifestyle_type="eco",
            carbon_reduction_goal=20.0
        )
        print(f"프로필 생성: {profile_id}")

        # 활동 기록
        activity_id = service.record_carbon_activity(
            user_id="test_user_123",
            activity_data={
                'activity_type': 'local_food_purchase',
                'product_name': '유기농 상추',
                'quantity': 1.5,
                'origin_region': '경기도',
                'destination_region': '서울시',
                'farming_method': 'organic',
                'transport_method': 'truck_small',
                'packaging_type': 'paper'
            }
        )
        print(f"활동 기록: {activity_id}")

    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")