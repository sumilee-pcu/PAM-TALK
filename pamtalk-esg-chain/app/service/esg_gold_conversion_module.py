# -*- coding: utf-8 -*-
"""
ESG-Gold Automatic Conversion Module
탄소 감축 활동 → ESG-GOLD 자동 변환 및 보상 모듈
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .carbon_calculation_engine import (
    CarbonCalculationEngine,
    CarbonActivity,
    ActivityType
)
from .esg_gold_service import ESGGoldService

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """ESG-GOLD 변환 결과"""
    success: bool
    user_id: str
    carbon_savings_kg: float
    dc_units: float
    esg_gold_minted: float
    pam_tokens_awarded: int
    transaction_id: Optional[str]
    timestamp: str
    error: Optional[str] = None


class ESGGoldConversionModule:
    """ESG-GOLD 자동 변환 모듈"""

    def __init__(self, esg_gold_service: ESGGoldService,
                 creator_private_key: str,
                 db_connection=None):
        """
        Args:
            esg_gold_service: ESG-GOLD 토큰 서비스
            creator_private_key: ESG-GOLD 발행 권한 계정의 private key
            db_connection: 데이터베이스 연결 (선택사항)
        """
        self.esg_service = esg_gold_service
        self.carbon_engine = CarbonCalculationEngine()
        self.creator_private_key = creator_private_key
        self.db = db_connection

        # 일일 변환 제한 (사용자당)
        self.daily_conversion_limit_dc = 1000.0  # 1000 DC/day
        self.daily_conversions = {}  # user_id: {date: amount}

    def process_carbon_activity(self, activity: CarbonActivity,
                                user_wallet_address: str) -> ConversionResult:
        """
        탄소 감축 활동 처리 및 ESG-GOLD 자동 발행

        Args:
            activity: 탄소 감축 활동 정보
            user_wallet_address: 사용자 지갑 주소

        Returns:
            ConversionResult
        """
        try:
            # 1. 탄소 발자국 계산
            carbon_result = self.carbon_engine.calculate_carbon_footprint(activity)

            logger.info(f"Carbon footprint calculated for user {activity.user_id}: "
                       f"{carbon_result.carbon_savings} kg CO2 saved")

            # 2. 일일 한도 확인
            if not self._check_daily_limit(activity.user_id, carbon_result.digital_carbon_units):
                return ConversionResult(
                    success=False,
                    user_id=activity.user_id,
                    carbon_savings_kg=carbon_result.carbon_savings,
                    dc_units=carbon_result.digital_carbon_units,
                    esg_gold_minted=0.0,
                    pam_tokens_awarded=0,
                    transaction_id=None,
                    timestamp=datetime.now().isoformat(),
                    error="daily_limit_exceeded"
                )

            # 3. ESG-GOLD 옵트인 확인
            if not self.esg_service.has_opted_in(user_wallet_address):
                logger.warning(f"User {activity.user_id} wallet not opted in to ESG-GOLD")
                # 자동으로 옵트인은 하지 않음 (사용자가 직접 해야 함)
                return ConversionResult(
                    success=False,
                    user_id=activity.user_id,
                    carbon_savings_kg=carbon_result.carbon_savings,
                    dc_units=carbon_result.digital_carbon_units,
                    esg_gold_minted=0.0,
                    pam_tokens_awarded=0,
                    transaction_id=None,
                    timestamp=datetime.now().isoformat(),
                    error="wallet_not_opted_in"
                )

            # 4. ESG-GOLD 발행
            mint_result = self.esg_service.mint_esg_gold(
                recipient_address=user_wallet_address,
                amount_dc=carbon_result.digital_carbon_units,
                creator_private_key=self.creator_private_key,
                reason=f"carbon_reduction_{activity.activity_type.value}"
            )

            if not mint_result['success']:
                return ConversionResult(
                    success=False,
                    user_id=activity.user_id,
                    carbon_savings_kg=carbon_result.carbon_savings,
                    dc_units=carbon_result.digital_carbon_units,
                    esg_gold_minted=0.0,
                    pam_tokens_awarded=0,
                    transaction_id=None,
                    timestamp=datetime.now().isoformat(),
                    error=mint_result.get('error', 'mint_failed')
                )

            # 5. 일일 사용량 업데이트
            self._update_daily_usage(activity.user_id, carbon_result.digital_carbon_units)

            # 6. DB에 변환 기록 저장 (선택사항)
            if self.db:
                self._save_conversion_record(
                    activity=activity,
                    carbon_result=carbon_result,
                    mint_result=mint_result
                )

            logger.info(f"ESG-GOLD minted successfully: {carbon_result.esg_gold_actual} DC "
                       f"to {user_wallet_address}")

            return ConversionResult(
                success=True,
                user_id=activity.user_id,
                carbon_savings_kg=carbon_result.carbon_savings,
                dc_units=carbon_result.digital_carbon_units,
                esg_gold_minted=carbon_result.esg_gold_actual,
                pam_tokens_awarded=carbon_result.reward_amount,
                transaction_id=mint_result['tx_id'],
                timestamp=mint_result['timestamp']
            )

        except Exception as e:
            logger.error(f"Failed to process carbon activity: {e}")
            return ConversionResult(
                success=False,
                user_id=activity.user_id,
                carbon_savings_kg=0.0,
                dc_units=0.0,
                esg_gold_minted=0.0,
                pam_tokens_awarded=0,
                transaction_id=None,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

    def batch_process_activities(self, activities: List[Tuple[CarbonActivity, str]]) -> List[ConversionResult]:
        """
        여러 활동을 일괄 처리

        Args:
            activities: [(CarbonActivity, wallet_address), ...]

        Returns:
            List[ConversionResult]
        """
        results = []

        for activity, wallet in activities:
            result = self.process_carbon_activity(activity, wallet)
            results.append(result)

            # API rate limiting
            import time
            time.sleep(0.5)  # 0.5초 대기

        return results

    def calculate_reward_preview(self, activity: CarbonActivity) -> Dict:
        """
        보상 미리보기 (실제 발행 없이 계산만)

        Args:
            activity: 탄소 감축 활동

        Returns:
            보상 정보
        """
        carbon_result = self.carbon_engine.calculate_carbon_footprint(activity)

        return {
            'carbon_savings_kg': carbon_result.carbon_savings,
            'reduction_percentage': carbon_result.reduction_percentage,
            'dc_units': carbon_result.digital_carbon_units,
            'esg_gold_amount': carbon_result.esg_gold_actual,
            'pam_tokens': carbon_result.reward_amount,
            'breakdown': {
                'transport_emissions': carbon_result.transport_emissions,
                'production_emissions': carbon_result.production_emissions,
                'packaging_emissions': carbon_result.packaging_emissions,
                'total_emissions': carbon_result.total_emissions,
                'baseline_emissions': carbon_result.baseline_emissions
            }
        }

    def get_user_conversion_stats(self, user_id: str, days: int = 30) -> Dict:
        """
        사용자의 변환 통계 조회

        Args:
            user_id: 사용자 ID
            days: 조회 기간 (일)

        Returns:
            통계 정보
        """
        if not self.db:
            logger.warning("Database not configured, cannot retrieve stats")
            return {}

        try:
            # DB에서 사용자의 변환 기록 조회
            # 실제 구현에서는 SQL 쿼리 실행
            query = """
                SELECT
                    COUNT(*) as total_conversions,
                    SUM(carbon_savings_kg) as total_carbon_saved,
                    SUM(dc_units) as total_dc_earned,
                    SUM(esg_gold_minted) as total_esg_gold,
                    SUM(pam_tokens_awarded) as total_pam_tokens
                FROM esg_gold_conversions
                WHERE user_id = ?
                AND timestamp >= datetime('now', '-{} days')
            """.format(days)

            # 여기서는 예시로 빈 딕셔너리 반환
            return {
                'user_id': user_id,
                'period_days': days,
                'total_conversions': 0,
                'total_carbon_saved_kg': 0.0,
                'total_dc_earned': 0.0,
                'total_esg_gold': 0.0,
                'total_pam_tokens': 0
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}

    def apply_marketplace_discount(self, user_wallet: str, user_private_key: str,
                                   esg_gold_amount: float,
                                   purchase_amount: float) -> Dict:
        """
        마켓플레이스에서 ESG-GOLD를 사용한 할인 적용

        사용된 ESG-GOLD의 10%는 소각됨

        Args:
            user_wallet: 사용자 지갑 주소
            user_private_key: 사용자 private key
            esg_gold_amount: 사용할 ESG-GOLD 수량
            purchase_amount: 구매 금액 (원)

        Returns:
            {
                'success': bool,
                'discount_rate': float,  # 할인율
                'discount_amount': float,  # 할인 금액
                'final_amount': float,  # 최종 결제 금액
                'esg_gold_used': float,
                'esg_gold_burned': float,
                'burn_tx_id': str
            }
        """
        try:
            # 1. ESG-GOLD 잔액 확인
            balance = self.esg_service.get_balance(user_wallet)
            if balance < esg_gold_amount:
                return {
                    'success': False,
                    'error': 'insufficient_esg_gold',
                    'required': esg_gold_amount,
                    'available': balance
                }

            # 2. 할인율 계산 (1 DC = 1원 할인, 최대 20%)
            discount_amount = min(esg_gold_amount, purchase_amount * 0.2)
            discount_rate = (discount_amount / purchase_amount) * 100
            final_amount = purchase_amount - discount_amount

            # 3. ESG-GOLD 소각 (10% burn)
            total_micro, burned_micro = self.carbon_engine.calculate_esg_gold_burn(
                esg_gold_amount, 'marketplace_discount'
            )

            burned_dc = burned_micro / (10 ** 6)

            burn_result = self.esg_service.burn_esg_gold(
                amount_dc=burned_dc,
                owner_address=user_wallet,
                owner_private_key=user_private_key,
                reason='marketplace_discount'
            )

            if not burn_result['success']:
                return {
                    'success': False,
                    'error': 'burn_failed',
                    'details': burn_result
                }

            # 4. DB에 할인 기록 저장
            if self.db:
                self._save_discount_record(
                    user_wallet=user_wallet,
                    esg_gold_used=esg_gold_amount,
                    esg_gold_burned=burned_dc,
                    purchase_amount=purchase_amount,
                    discount_amount=discount_amount,
                    burn_tx_id=burn_result['tx_id']
                )

            return {
                'success': True,
                'discount_rate': round(discount_rate, 2),
                'discount_amount': round(discount_amount, 2),
                'final_amount': round(final_amount, 2),
                'esg_gold_used': esg_gold_amount,
                'esg_gold_burned': burned_dc,
                'burn_tx_id': burn_result['tx_id'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to apply marketplace discount: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _check_daily_limit(self, user_id: str, dc_amount: float) -> bool:
        """일일 변환 한도 확인"""
        today = datetime.now().date().isoformat()

        if user_id not in self.daily_conversions:
            self.daily_conversions[user_id] = {}

        user_daily = self.daily_conversions[user_id]

        # 오래된 날짜 데이터 삭제
        old_dates = [date for date in user_daily.keys()
                    if date < (datetime.now() - timedelta(days=7)).date().isoformat()]
        for old_date in old_dates:
            del user_daily[old_date]

        # 오늘 사용량 확인
        today_usage = user_daily.get(today, 0.0)

        if today_usage + dc_amount > self.daily_conversion_limit_dc:
            logger.warning(f"Daily limit exceeded for user {user_id}: "
                         f"{today_usage + dc_amount} > {self.daily_conversion_limit_dc}")
            return False

        return True

    def _update_daily_usage(self, user_id: str, dc_amount: float):
        """일일 사용량 업데이트"""
        today = datetime.now().date().isoformat()

        if user_id not in self.daily_conversions:
            self.daily_conversions[user_id] = {}

        if today not in self.daily_conversions[user_id]:
            self.daily_conversions[user_id][today] = 0.0

        self.daily_conversions[user_id][today] += dc_amount

    def _save_conversion_record(self, activity: CarbonActivity,
                                carbon_result, mint_result: Dict):
        """DB에 변환 기록 저장"""
        if not self.db:
            return

        try:
            query = """
                INSERT INTO esg_gold_conversions (
                    user_id, activity_type, carbon_savings_kg, dc_units,
                    esg_gold_minted, pam_tokens_awarded, transaction_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.db.execute(query, (
                activity.user_id,
                activity.activity_type.value,
                carbon_result.carbon_savings,
                carbon_result.digital_carbon_units,
                carbon_result.esg_gold_actual,
                carbon_result.reward_amount,
                mint_result['tx_id'],
                mint_result['timestamp']
            ))
            self.db.commit()

            logger.info(f"Conversion record saved for user {activity.user_id}")

        except Exception as e:
            logger.error(f"Failed to save conversion record: {e}")

    def _save_discount_record(self, user_wallet: str, esg_gold_used: float,
                             esg_gold_burned: float, purchase_amount: float,
                             discount_amount: float, burn_tx_id: str):
        """DB에 할인 기록 저장"""
        if not self.db:
            return

        try:
            query = """
                INSERT INTO esg_gold_marketplace_discounts (
                    user_wallet, esg_gold_used, esg_gold_burned,
                    purchase_amount, discount_amount, burn_tx_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            self.db.execute(query, (
                user_wallet,
                esg_gold_used,
                esg_gold_burned,
                purchase_amount,
                discount_amount,
                burn_tx_id,
                datetime.now().isoformat()
            ))
            self.db.commit()

            logger.info(f"Discount record saved for wallet {user_wallet}")

        except Exception as e:
            logger.error(f"Failed to save discount record: {e}")


# 사용 예시
if __name__ == "__main__":
    from algosdk import account

    # ESG-GOLD 서비스 초기화
    esg_service = ESGGoldService('../../esg_gold_config.json')

    # Creator 계정 정보 (예시 - 실제로는 안전하게 관리)
    creator_private_key = "YOUR_CREATOR_PRIVATE_KEY"

    # 변환 모듈 초기화
    conversion_module = ESGGoldConversionModule(
        esg_gold_service=esg_service,
        creator_private_key=creator_private_key
    )

    # 테스트 활동
    test_activity = CarbonActivity(
        activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
        user_id="user123",
        product_name="유기농 토마토",
        quantity=3.0,
        origin_region="경기도",
        destination_region="서울시",
        farming_method="organic",
        transport_method="truck_small",
        packaging_type="paper",
        activity_date=datetime.now().isoformat()
    )

    # 보상 미리보기
    preview = conversion_module.calculate_reward_preview(test_activity)
    print("=== Reward Preview ===")
    print(f"Carbon Saved: {preview['carbon_savings_kg']} kg CO2")
    print(f"DC Units: {preview['dc_units']}")
    print(f"ESG-GOLD: {preview['esg_gold_amount']}")
    print(f"PAM Tokens: {preview['pam_tokens']}")

    # 실제 변환 (사용자 지갑 주소 필요)
    # user_wallet = "USER_WALLET_ADDRESS"
    # result = conversion_module.process_carbon_activity(test_activity, user_wallet)
    # print(f"\nConversion Result: {result}")
