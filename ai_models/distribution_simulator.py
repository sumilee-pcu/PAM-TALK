#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distribution Structure Simulator
유통 구조 시뮬레이터 - PAM-TALK 플랫폼 도입 효과 분석
"""

import json
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class DistributionConfig:
    """유통 구조 설정"""
    stages: int  # 유통 단계 수
    margin_min: float  # 최소 마진율 (%)
    margin_max: float  # 최대 마진율 (%)
    local_food_ratio: float  # 로컬푸드 비중 (%)
    food_mileage: float  # 평균 푸드 마일리지 (km)
    packaging_rate: float  # 일회용 포장재 사용률 (%)


@dataclass
class ProductTypeResult:
    """농산물 유형별 결과"""
    name: str
    baseline_margin: float
    improved_margin: float
    margin_reduction: float
    producer_price_increase: float
    consumer_price_decrease: float
    volume_increase: float


class DistributionSimulator:
    """유통 구조 시뮬레이터"""

    def __init__(self):
        """초기화"""
        # 기준선 (Baseline) 설정
        self.baseline = DistributionConfig(
            stages=5,
            margin_min=35.0,
            margin_max=45.0,
            local_food_ratio=23.0,
            food_mileage=150.0,
            packaging_rate=85.0
        )

        # 개선안 (PAM-TALK 도입 후)
        self.improved = DistributionConfig(
            stages=2,
            margin_min=10.0,
            margin_max=15.0,
            local_food_ratio=70.0,
            food_mileage=25.0,
            packaging_rate=40.0
        )

        # 농산물 유형별 데이터
        self.product_types = {
            "leafy_vegetables": {  # 엽채류
                "name": "엽채류",
                "baseline_margin": 42.0,
                "improved_margin": 12.0,
                "producer_price_increase": 32.0,
                "consumer_price_decrease": 18.0,
                "volume_increase": 45.0
            },
            "fruit_vegetables": {  # 과채류
                "name": "과채류",
                "baseline_margin": 38.0,
                "improved_margin": 14.0,
                "producer_price_increase": 28.0,
                "consumer_price_decrease": 14.0,
                "volume_increase": 38.0
            },
            "root_vegetables": {  # 근채류
                "name": "근채류",
                "baseline_margin": 35.0,
                "improved_margin": 10.0,
                "producer_price_increase": 35.0,
                "consumer_price_decrease": 20.0,
                "volume_increase": 50.0
            },
            "fruits": {  # 과실류
                "name": "과실류",
                "baseline_margin": 45.0,
                "improved_margin": 15.0,
                "producer_price_increase": 30.0,
                "consumer_price_decrease": 16.0,
                "volume_increase": 42.0
            }
        }

    def calculate_overall_improvement(self) -> Dict:
        """전체 유통 구조 개선 효과 계산"""
        avg_baseline_margin = (self.baseline.margin_min + self.baseline.margin_max) / 2
        avg_improved_margin = (self.improved.margin_min + self.improved.margin_max) / 2
        margin_reduction = avg_baseline_margin - avg_improved_margin

        stage_reduction = ((self.baseline.stages - self.improved.stages) /
                          self.baseline.stages * 100)

        return {
            "baseline": {
                "stages": self.baseline.stages,
                "avg_margin": avg_baseline_margin,
                "local_food_ratio": self.baseline.local_food_ratio,
                "food_mileage": self.baseline.food_mileage,
                "packaging_rate": self.baseline.packaging_rate
            },
            "improved": {
                "stages": self.improved.stages,
                "avg_margin": avg_improved_margin,
                "local_food_ratio": self.improved.local_food_ratio,
                "food_mileage": self.improved.food_mileage,
                "packaging_rate": self.improved.packaging_rate
            },
            "improvements": {
                "stage_reduction_pct": round(stage_reduction, 1),
                "margin_reduction_pp": round(margin_reduction, 1),
                "producer_price_increase_pct": 28.0,  # 평균
                "consumer_price_decrease_pct": 15.0,  # 평균
                "local_food_increase_pp": self.improved.local_food_ratio - self.baseline.local_food_ratio,
                "food_mileage_reduction_pct": round(
                    (self.baseline.food_mileage - self.improved.food_mileage) /
                    self.baseline.food_mileage * 100, 1
                ),
                "packaging_reduction_pp": self.baseline.packaging_rate - self.improved.packaging_rate
            }
        }

    def calculate_product_type_effects(self) -> List[Dict]:
        """농산물 유형별 효과 분석"""
        results = []

        for key, data in self.product_types.items():
            margin_reduction = data["baseline_margin"] - data["improved_margin"]

            result = {
                "type": key,
                "name": data["name"],
                "baseline_margin": data["baseline_margin"],
                "improved_margin": data["improved_margin"],
                "margin_reduction": round(margin_reduction, 1),
                "producer_price_increase": data["producer_price_increase"],
                "consumer_price_decrease": data["consumer_price_decrease"],
                "volume_increase": data["volume_increase"]
            }
            results.append(result)

        return results

    def calculate_lstm_effects(self, accuracy: float = 85.0) -> Dict:
        """LSTM 수요 예측 시스템 효과"""
        return {
            "prediction_accuracy": accuracy,
            "inventory_cost_reduction": 18.0,  # %
            "waste_reduction": 27.0,  # %
            "benefits": [
                {
                    "stakeholder": "생산자",
                    "benefit": "2-4주 전 수요 예측으로 파종 시기와 재배 품목 최적화"
                },
                {
                    "stakeholder": "가맹점",
                    "benefit": "적정 재고로 신선도 보장"
                },
                {
                    "stakeholder": "플랫폼",
                    "benefit": "물류 자원 사전 배치로 운영 효율 향상"
                }
            ]
        }

    def run_simulation(self) -> Dict:
        """전체 시뮬레이션 실행"""
        return {
            "overall": self.calculate_overall_improvement(),
            "product_types": self.calculate_product_type_effects(),
            "lstm_effects": self.calculate_lstm_effects()
        }

    def export_json(self, filepath: str = "data/simulation/distribution_results.json"):
        """결과를 JSON으로 저장"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results = self.run_simulation()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return filepath


if __name__ == "__main__":
    # 시뮬레이터 실행
    simulator = DistributionSimulator()
    results = simulator.run_simulation()

    print("=" * 70)
    print("유통 구조 시뮬레이션 결과")
    print("=" * 70)

    # 전체 개선 효과
    overall = results["overall"]
    print("\n[전체 유통 구조 개선 효과]")
    print(f"유통 단계: {overall['baseline']['stages']}단계 → {overall['improved']['stages']}단계 "
          f"({overall['improvements']['stage_reduction_pct']}% 단축)")
    print(f"유통 마진: {overall['baseline']['avg_margin']}% → {overall['improved']['avg_margin']}% "
          f"({overall['improvements']['margin_reduction_pp']}%p 절감)")
    print(f"생산자 수취가격: {overall['improvements']['producer_price_increase_pct']}% 상승")
    print(f"소비자 구매가격: {overall['improvements']['consumer_price_decrease_pct']}% 하락")
    print(f"로컬푸드 비중: {overall['baseline']['local_food_ratio']}% → {overall['improved']['local_food_ratio']}%")
    print(f"푸드 마일리지: {overall['baseline']['food_mileage']}km → {overall['improved']['food_mileage']}km "
          f"({overall['improvements']['food_mileage_reduction_pct']}% 감소)")

    # 농산물 유형별
    print("\n[농산물 유형별 분석]")
    for product in results["product_types"]:
        print(f"\n{product['name']}:")
        print(f"  유통 마진: {product['baseline_margin']}% → {product['improved_margin']}% "
              f"({product['margin_reduction']}%p 감소)")
        print(f"  생산자 수취가격: {product['producer_price_increase']}% 증가")
        print(f"  소비자 구매가격: {product['consumer_price_decrease']}% 하락")
        print(f"  거래량: {product['volume_increase']}% 증가")

    # LSTM 효과
    lstm = results["lstm_effects"]
    print("\n[LSTM 수요 예측 효과]")
    print(f"예측 정확도: {lstm['prediction_accuracy']}%")
    print(f"재고 비용 절감: {lstm['inventory_cost_reduction']}%")
    print(f"폐기율 감소: {lstm['waste_reduction']}%")

    # JSON 저장
    filepath = simulator.export_json()
    print(f"\n결과 저장: {filepath}")
    print("=" * 70)
