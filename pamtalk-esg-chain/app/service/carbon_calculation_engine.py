# -*- coding: utf-8 -*-
"""
탄소 발자국 계산 엔진
지역별, 활동별, 제품별 탄소 배출량 및 절약량 계산
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# ESG-GOLD 변환 상수
ESG_GOLD_CONVERSION = {
    'dc_per_kg_co2': 1.0,  # 1 DC = 1 kg CO2 감축
    'esg_gold_decimals': 6,  # ESG-GOLD 토큰 decimals
    'micro_units_per_dc': 1_000_000,  # 1 DC = 1,000,000 micro ESG-GOLD
    'min_dc_for_mint': 0.1,  # 최소 발행 DC 단위
}

# 탄소 계산 관련 상수 (한국 기준)
CARBON_FACTORS = {
    # 운송 수단별 CO2 배출량 (kg CO2/km·ton)
    'transport': {
        'truck_small': 0.62,  # 1톤 트럭
        'truck_medium': 0.45,  # 5톤 트럭
        'truck_large': 0.38,   # 10톤 트럭
        'rail': 0.022,         # 철도
        'ship': 0.015,         # 선박
        'airplane': 0.5        # 항공 (단거리)
    },

    # 농업 활동별 CO2 배출량 (kg CO2/kg)
    'agriculture': {
        'organic_vegetables': 0.3,    # 유기농 채소
        'conventional_vegetables': 0.5, # 일반 채소
        'organic_fruits': 0.4,        # 유기농 과일
        'conventional_fruits': 0.7,   # 일반 과일
        'organic_grains': 0.8,        # 유기농 곡물
        'conventional_grains': 1.2,   # 일반 곡물
        'greenhouse': 2.5,            # 온실 재배
        'open_field': 0.8             # 노지 재배
    },

    # 포장재별 CO2 배출량 (kg CO2/kg)
    'packaging': {
        'plastic': 3.4,
        'paper': 0.9,
        'biodegradable': 0.4,
        'reusable': 0.1
    },

    # 에너지원별 CO2 배출량 (kg CO2/kWh)
    'energy': {
        'coal': 0.82,
        'natural_gas': 0.35,
        'renewable': 0.02,
        'nuclear': 0.06
    }
}

# 지역별 거리 매트릭스 (km) - 주요 도시 간
DISTANCE_MATRIX = {
    ('경기도', '서울시'): 30,
    ('경기도', '인천시'): 25,
    ('경기도', '부산시'): 325,
    ('경기도', '대구시'): 237,
    ('경기도', '대전시'): 140,
    ('경기도', '광주시'): 267,
    ('경기도', '울산시'): 290,
    ('전라남도', '광주시'): 50,
    ('전라남도', '서울시'): 300,
    ('전라남도', '부산시'): 350,
    ('경상북도', '대구시'): 30,
    ('경상북도', '서울시'): 260,
    ('경상북도', '부산시'): 120,
    ('충청남도', '대전시'): 40,
    ('충청남도', '서울시'): 120,
    ('강원도', '서울시'): 150
}


class ActivityType(Enum):
    """활동 유형"""
    LOCAL_FOOD_PURCHASE = "local_food_purchase"
    ORGANIC_FARMING = "organic_farming"
    RENEWABLE_ENERGY = "renewable_energy"
    WASTE_REDUCTION = "waste_reduction"
    TRANSPORT_REDUCTION = "transport_reduction"
    PACKAGING_REDUCTION = "packaging_reduction"


@dataclass
class CarbonActivity:
    """탄소 관련 활동 정보"""
    activity_type: ActivityType
    user_id: str
    product_name: str
    quantity: float  # kg 또는 개수
    origin_region: str
    destination_region: str
    farming_method: str  # organic, conventional
    transport_method: str
    packaging_type: str
    activity_date: str
    metadata: Dict = None


@dataclass
class CarbonCalculationResult:
    """탄소 계산 결과"""
    total_emissions: float  # 총 배출량 (kg CO2)
    transport_emissions: float
    production_emissions: float
    packaging_emissions: float
    carbon_savings: float  # 절약량 (기준 대비)
    baseline_emissions: float  # 기준 배출량
    reduction_percentage: float
    token_reward_eligible: bool
    reward_amount: int  # 토큰 개수
    # ESG-Gold 관련 필드 추가
    digital_carbon_units: float  # 1 DC = 1 kg CO2 감축
    esg_gold_amount: int  # ESG-GOLD 토큰 (micro units, 6 decimals)
    esg_gold_actual: float  # 실제 ESG-GOLD (decimals 적용)


class CarbonCalculationEngine:
    """탄소 발자국 계산 엔진"""

    def __init__(self):
        self.carbon_factors = CARBON_FACTORS
        self.distance_matrix = DISTANCE_MATRIX
        self.esg_gold_config = ESG_GOLD_CONVERSION

    def calculate_carbon_footprint(self, activity: CarbonActivity) -> CarbonCalculationResult:
        """종합적인 탄소 발자국 계산"""

        # 1. 운송 배출량 계산
        transport_emissions = self._calculate_transport_emissions(
            activity.origin_region,
            activity.destination_region,
            activity.quantity,
            activity.transport_method
        )

        # 2. 생산 배출량 계산
        production_emissions = self._calculate_production_emissions(
            activity.product_name,
            activity.quantity,
            activity.farming_method
        )

        # 3. 포장 배출량 계산
        packaging_emissions = self._calculate_packaging_emissions(
            activity.quantity,
            activity.packaging_type
        )

        total_emissions = transport_emissions + production_emissions + packaging_emissions

        # 4. 기준 배출량 계산 (일반적인 방법 대비)
        baseline_emissions = self._calculate_baseline_emissions(activity)

        # 5. 탄소 절약량 계산
        carbon_savings = max(0, baseline_emissions - total_emissions)
        reduction_percentage = (carbon_savings / baseline_emissions * 100) if baseline_emissions > 0 else 0

        # 6. 토큰 보상 계산 (PAM 토큰)
        token_reward_eligible, reward_amount = self._calculate_token_reward(
            carbon_savings, activity.activity_type
        )

        # 7. ESG-GOLD 변환 계산 (1 DC = 1 kg CO2)
        dc_units, esg_gold_micro, esg_gold_actual = self._convert_to_esg_gold(
            carbon_savings, activity.activity_type
        )

        return CarbonCalculationResult(
            total_emissions=round(total_emissions, 3),
            transport_emissions=round(transport_emissions, 3),
            production_emissions=round(production_emissions, 3),
            packaging_emissions=round(packaging_emissions, 3),
            carbon_savings=round(carbon_savings, 3),
            baseline_emissions=round(baseline_emissions, 3),
            reduction_percentage=round(reduction_percentage, 2),
            token_reward_eligible=token_reward_eligible,
            reward_amount=reward_amount,
            digital_carbon_units=round(dc_units, 3),
            esg_gold_amount=esg_gold_micro,
            esg_gold_actual=round(esg_gold_actual, 6)
        )

    def _calculate_transport_emissions(self, origin: str, destination: str,
                                     quantity: float, transport_method: str) -> float:
        """운송 배출량 계산"""
        # 거리 조회
        distance = self._get_distance(origin, destination)

        # 운송 수단별 배출계수
        emission_factor = self.carbon_factors['transport'].get(transport_method, 0.5)

        # 배출량 = 거리(km) × 중량(ton) × 배출계수(kg CO2/km·ton)
        weight_in_tons = quantity / 1000
        emissions = distance * weight_in_tons * emission_factor

        return max(0, emissions)

    def _calculate_production_emissions(self, product_name: str, quantity: float,
                                      farming_method: str) -> float:
        """생산 배출량 계산"""
        # 제품 유형 분류
        product_category = self._classify_product(product_name)

        # 농법별 배출계수 조회
        method_key = f"{farming_method}_{product_category}"
        emission_factor = self.carbon_factors['agriculture'].get(
            method_key,
            self.carbon_factors['agriculture']['conventional_vegetables']
        )

        # 배출량 = 수량(kg) × 배출계수(kg CO2/kg)
        return quantity * emission_factor

    def _calculate_packaging_emissions(self, quantity: float, packaging_type: str) -> float:
        """포장 배출량 계산"""
        # 포장재 무게 추정 (제품 무게의 5-15%)
        packaging_ratio = {
            'plastic': 0.15,
            'paper': 0.10,
            'biodegradable': 0.12,
            'reusable': 0.05
        }

        packaging_weight = quantity * packaging_ratio.get(packaging_type, 0.10)
        emission_factor = self.carbon_factors['packaging'].get(packaging_type, 1.0)

        return packaging_weight * emission_factor

    def _calculate_baseline_emissions(self, activity: CarbonActivity) -> float:
        """기준 배출량 계산 (일반적인 유통 방식)"""
        # 일반적인 시나리오: 장거리 운송 + 일반농법 + 플라스틱 포장
        baseline_activity = CarbonActivity(
            activity_type=activity.activity_type,
            user_id=activity.user_id,
            product_name=activity.product_name,
            quantity=activity.quantity,
            origin_region="경상북도",  # 가정: 원거리 산지
            destination_region=activity.destination_region,
            farming_method="conventional",
            transport_method="truck_medium",
            packaging_type="plastic",
            activity_date=activity.activity_date
        )

        # 기준 배출량 계산
        transport_baseline = self._calculate_transport_emissions(
            baseline_activity.origin_region,
            baseline_activity.destination_region,
            baseline_activity.quantity,
            baseline_activity.transport_method
        )

        production_baseline = self._calculate_production_emissions(
            baseline_activity.product_name,
            baseline_activity.quantity,
            baseline_activity.farming_method
        )

        packaging_baseline = self._calculate_packaging_emissions(
            baseline_activity.quantity,
            baseline_activity.packaging_type
        )

        return transport_baseline + production_baseline + packaging_baseline

    def _calculate_token_reward(self, carbon_savings: float,
                               activity_type: ActivityType) -> Tuple[bool, int]:
        """토큰 보상 계산"""
        # 최소 절약량 기준 (kg CO2)
        min_savings_threshold = 0.5

        if carbon_savings < min_savings_threshold:
            return False, 0

        # 활동별 보상 배율
        reward_multipliers = {
            ActivityType.LOCAL_FOOD_PURCHASE: 10,  # 1kg CO2 = 10 토큰
            ActivityType.ORGANIC_FARMING: 15,      # 1kg CO2 = 15 토큰
            ActivityType.RENEWABLE_ENERGY: 20,     # 1kg CO2 = 20 토큰
            ActivityType.WASTE_REDUCTION: 12,      # 1kg CO2 = 12 토큰
            ActivityType.TRANSPORT_REDUCTION: 8,   # 1kg CO2 = 8 토큰
            ActivityType.PACKAGING_REDUCTION: 5    # 1kg CO2 = 5 토큰
        }

        multiplier = reward_multipliers.get(activity_type, 10)
        reward_amount = int(carbon_savings * multiplier)

        # 최대 보상 제한 (일일 500토큰)
        max_daily_reward = 500
        reward_amount = min(reward_amount, max_daily_reward)

        return True, reward_amount

    def _convert_to_esg_gold(self, carbon_savings: float,
                            activity_type: ActivityType) -> Tuple[float, int, float]:
        """
        탄소 절약량을 ESG-GOLD 토큰으로 변환

        1 DC (Digital Carbon) = 1 kg CO2 감축량
        1 ESG-GOLD = 1 DC = 1 kg CO2

        Returns:
            (DC 단위, ESG-GOLD micro units, ESG-GOLD actual)
        """
        # 최소 변환 기준
        min_dc = self.esg_gold_config['min_dc_for_mint']

        if carbon_savings < min_dc:
            return 0.0, 0, 0.0

        # 1 DC = 1 kg CO2 감축
        dc_units = carbon_savings * self.esg_gold_config['dc_per_kg_co2']

        # 활동 유형별 보상 배율 적용
        activity_multipliers = {
            ActivityType.LOCAL_FOOD_PURCHASE: 1.2,  # 지역 먹거리 20% 보너스
            ActivityType.ORGANIC_FARMING: 1.5,      # 유기농 50% 보너스
            ActivityType.RENEWABLE_ENERGY: 2.0,     # 재생에너지 100% 보너스
            ActivityType.WASTE_REDUCTION: 1.8,      # 폐기물 감축 80% 보너스
            ActivityType.TRANSPORT_REDUCTION: 1.3,  # 운송 감축 30% 보너스
            ActivityType.PACKAGING_REDUCTION: 1.3   # 포장 감축 30% 보너스
        }

        multiplier = activity_multipliers.get(activity_type, 1.0)
        dc_units_with_bonus = dc_units * multiplier

        # ESG-GOLD 토큰 계산 (micro units)
        # 1 ESG-GOLD = 1,000,000 micro units (6 decimals)
        esg_gold_micro = int(dc_units_with_bonus * self.esg_gold_config['micro_units_per_dc'])

        # 실제 ESG-GOLD (decimals 적용)
        esg_gold_actual = esg_gold_micro / self.esg_gold_config['micro_units_per_dc']

        return dc_units_with_bonus, esg_gold_micro, esg_gold_actual

    def calculate_esg_gold_burn(self, esg_gold_amount: float,
                               burn_mechanism: str = 'marketplace_discount') -> Tuple[int, int]:
        """
        ESG-GOLD 소각량 계산

        Args:
            esg_gold_amount: 사용할 ESG-GOLD 수량 (actual units)
            burn_mechanism: 소각 메커니즘 ('marketplace_discount' or 'offset_retirement')

        Returns:
            (사용될 micro units, 소각될 micro units)
        """
        burn_rates = {
            'marketplace_discount': 0.1,  # 10% 소각
            'offset_retirement': 1.0,     # 100% 소각 (영구 제거)
            'premium_service': 0.05,      # 5% 소각
        }

        burn_rate = burn_rates.get(burn_mechanism, 0.1)

        total_micro = int(esg_gold_amount * self.esg_gold_config['micro_units_per_dc'])
        burned_micro = int(total_micro * burn_rate)

        return total_micro, burned_micro

    def _get_distance(self, origin: str, destination: str) -> float:
        """지역 간 거리 조회"""
        # 직접 매칭
        key1 = (origin, destination)
        key2 = (destination, origin)

        if key1 in self.distance_matrix:
            return self.distance_matrix[key1]
        elif key2 in self.distance_matrix:
            return self.distance_matrix[key2]

        # 매칭되지 않으면 기본값 (평균 거리)
        return 150.0  # km

    def _classify_product(self, product_name: str) -> str:
        """제품 분류"""
        product_name_lower = product_name.lower()

        # 채소류
        vegetables = ['상추', '배추', '무', '당근', '양파', '감자', '토마토', '오이', '브로콜리']
        if any(veg in product_name_lower for veg in vegetables):
            return 'vegetables'

        # 과일류
        fruits = ['사과', '배', '딸기', '포도', '복숭아', '감', '귤', '바나나']
        if any(fruit in product_name_lower for fruit in fruits):
            return 'fruits'

        # 곡물류
        grains = ['쌀', '보리', '밀', '콩', '옥수수']
        if any(grain in product_name_lower for grain in grains):
            return 'grains'

        # 기본값
        return 'vegetables'

    def get_carbon_statistics(self, activities: List[CarbonActivity]) -> Dict:
        """탄소 통계 계산"""
        if not activities:
            return {
                'total_activities': 0,
                'total_carbon_savings': 0,
                'average_reduction_percentage': 0,
                'total_token_rewards': 0,
                'by_activity_type': {}
            }

        results = [self.calculate_carbon_footprint(activity) for activity in activities]

        total_savings = sum(result.carbon_savings for result in results)
        total_tokens = sum(result.reward_amount for result in results)
        avg_reduction = sum(result.reduction_percentage for result in results) / len(results)

        # 활동별 통계
        by_activity = {}
        for activity, result in zip(activities, results):
            activity_type = activity.activity_type.value
            if activity_type not in by_activity:
                by_activity[activity_type] = {
                    'count': 0,
                    'total_savings': 0,
                    'total_tokens': 0
                }

            by_activity[activity_type]['count'] += 1
            by_activity[activity_type]['total_savings'] += result.carbon_savings
            by_activity[activity_type]['total_tokens'] += result.reward_amount

        return {
            'total_activities': len(activities),
            'total_carbon_savings': round(total_savings, 3),
            'average_reduction_percentage': round(avg_reduction, 2),
            'total_token_rewards': total_tokens,
            'by_activity_type': by_activity
        }


# 사용 예시
if __name__ == "__main__":
    engine = CarbonCalculationEngine()

    # 테스트 활동
    test_activity = CarbonActivity(
        activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
        user_id="user123",
        product_name="유기농 상추",
        quantity=2.0,  # 2kg
        origin_region="경기도",
        destination_region="서울시",
        farming_method="organic",
        transport_method="truck_small",
        packaging_type="paper",
        activity_date="2024-01-15"
    )

    # 탄소 발자국 계산
    result = engine.calculate_carbon_footprint(test_activity)

    print("=== 탄소 발자국 계산 결과 ===")
    print(f"총 배출량: {result.total_emissions} kg CO2")
    print(f"- 운송: {result.transport_emissions} kg CO2")
    print(f"- 생산: {result.production_emissions} kg CO2")
    print(f"- 포장: {result.packaging_emissions} kg CO2")
    print(f"탄소 절약량: {result.carbon_savings} kg CO2")
    print(f"절약 비율: {result.reduction_percentage}%")
    print(f"토큰 보상: {result.reward_amount}개 토큰")