#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated PAM-TALK Simulator
통합 PAM-TALK 시뮬레이터 - 유통/탄소/경제 효과 종합 분석
"""

import json
import sys
import os
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_models.distribution_simulator import DistributionSimulator
from ai_models.carbon_calculator import CarbonCalculator
from ai_models.economic_analyzer import EconomicAnalyzer


class IntegratedSimulator:
    """통합 시뮬레이터"""

    def __init__(self, population: int = 100000):
        """
        초기화

        Args:
            population: 대상 지역 인구 (기본: 10만 명)
        """
        self.population = population

        # 각 모듈 초기화
        self.distribution = DistributionSimulator()
        self.carbon = CarbonCalculator(population=population)
        self.economic = EconomicAnalyzer(population=population)

    def run_full_simulation(self) -> Dict:
        """전체 시뮬레이션 실행"""

        print("\n" + "=" * 70)
        print("PAM-TALK 플랫폼 효과 시뮬레이션")
        print("=" * 70)
        print(f"대상 지역: 인구 {self.population:,}명 규모 중소도시")
        print(f"참여 규모: 생산자 100명, 소비자 2,000명, 가맹점 30개, 기업 5개")
        print("=" * 70)

        # 1. 유통 구조 시뮬레이션
        print("\n[1/4] 유통 구조 효과 분석 중...")
        distribution_results = self.distribution.run_simulation()

        # 2. 탄소 절감 계산
        print("[2/4] 탄소 절감 효과 계산 중...")
        carbon_results = self.carbon.run_calculation()

        # 3. 경제 효과 분석
        print("[3/4] 경제적 효과 분석 중...")
        economic_results = self.economic.run_analysis()

        # 4. LSTM 수요 예측 효과 (distribution에 포함)
        print("[4/4] 종합 분석 중...")

        # 통합 결과
        integrated_results = {
            "metadata": {
                "simulation_type": "PAM-TALK Platform Impact Analysis",
                "population": self.population,
                "participants": {
                    "producers": 100,
                    "consumers": 2000,
                    "stores": 30,
                    "enterprises": 5
                },
                "duration": "1년 (Annual Simulation)"
            },
            "distribution": distribution_results,
            "carbon": carbon_results,
            "economic": economic_results,
            "summary": self._create_summary(
                distribution_results,
                carbon_results,
                economic_results
            )
        }

        return integrated_results

    def _create_summary(self, dist: Dict, carbon: Dict, econ: Dict) -> Dict:
        """요약 보고서 생성"""

        return {
            "key_metrics": {
                "distribution": {
                    "stage_reduction": f"{dist['overall']['improvements']['stage_reduction_pct']}%",
                    "margin_reduction": f"{dist['overall']['improvements']['margin_reduction_pp']}%p",
                    "producer_price_increase": f"{dist['overall']['improvements']['producer_price_increase_pct']}%",
                    "consumer_price_decrease": f"{dist['overall']['improvements']['consumer_price_decrease_pct']}%"
                },
                "carbon": {
                    "total_reduction_ton": carbon["total"]["total_reduction_ton"],
                    "reduction_pct": f"{carbon['total']['reduction_pct']}%",
                    "car_equivalent": int(carbon["total"]["equivalent"]["passenger_cars"])
                },
                "economic": {
                    "total_impact_billion": econ["total_impact"]["total_impact_billion"],
                    "per_capita_benefit_krw": econ["total_impact"]["per_capita_benefit_krw"],
                    "jobs_created": int(econ["total_impact"]["employment_created"])
                }
            },
            "achievements": [
                {
                    "category": "유통 효율화",
                    "achievement": f"5단계 → 2단계 유통 구조로 {dist['overall']['improvements']['stage_reduction_pct']}% 단축",
                    "benefit": f"생산자 수익 {dist['overall']['improvements']['producer_price_increase_pct']}% 증가, 소비자 가격 {dist['overall']['improvements']['consumer_price_decrease_pct']}% 하락"
                },
                {
                    "category": "탄소 절감",
                    "achievement": f"연간 {carbon['total']['total_reduction_ton']}톤 CO₂e 절감 ({carbon['total']['reduction_pct']}% 감축)",
                    "benefit": f"승용차 {int(carbon['total']['equivalent']['passenger_cars'])}대의 연간 배출량에 해당"
                },
                {
                    "category": "경제 활성화",
                    "achievement": f"연간 {econ['total_impact']['total_impact_billion']}억원 경제적 효과",
                    "benefit": f"1인당 {econ['total_impact']['per_capita_benefit_krw']:,}원 편익, 약 {int(econ['total_impact']['employment_created'])}명 고용 창출"
                },
                {
                    "category": "수요 예측",
                    "achievement": f"LSTM 모델 {dist['lstm_effects']['prediction_accuracy']}% 정확도 달성",
                    "benefit": f"재고 비용 {dist['lstm_effects']['inventory_cost_reduction']}% 절감, 폐기율 {dist['lstm_effects']['waste_reduction']}% 감소"
                }
            ]
        }

    def export_full_results(self, filepath: str = "data/simulation/integrated_results.json"):
        """통합 결과를 JSON으로 저장"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results = self.run_full_simulation()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return filepath

    def print_summary_report(self):
        """요약 보고서 출력"""
        results = self.run_full_simulation()
        summary = results["summary"]

        print("\n" + "=" * 70)
        print("시뮬레이션 결과 요약")
        print("=" * 70)

        print("\n[핵심 성과 지표 (KPI)]")
        kpi = summary["key_metrics"]

        print("\n1. 유통 효율화")
        print(f"   - 유통 단계 감축: {kpi['distribution']['stage_reduction']}")
        print(f"   - 유통 마진 절감: {kpi['distribution']['margin_reduction']}")
        print(f"   - 생산자 수익 증가: {kpi['distribution']['producer_price_increase']}")
        print(f"   - 소비자 가격 하락: {kpi['distribution']['consumer_price_decrease']}")

        print("\n2. 탄소 절감")
        print(f"   - 총 절감량: {kpi['carbon']['total_reduction_ton']}톤 CO₂e/년")
        print(f"   - 절감률: {kpi['carbon']['reduction_pct']}")
        print(f"   - 환산: 승용차 {kpi['carbon']['car_equivalent']}대 배출량")

        print("\n3. 경제 활성화")
        print(f"   - 총 경제 효과: {kpi['economic']['total_impact_billion']}억원/년")
        print(f"   - 1인당 편익: {kpi['economic']['per_capita_benefit_krw']:,}원/년")
        print(f"   - 고용 창출: 약 {kpi['economic']['jobs_created']}명")

        print("\n[주요 성과]")
        for i, achievement in enumerate(summary["achievements"], 1):
            print(f"\n{i}. {achievement['category']}")
            print(f"   성과: {achievement['achievement']}")
            print(f"   효과: {achievement['benefit']}")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    # 통합 시뮬레이터 실행
    simulator = IntegratedSimulator(population=100000)

    # 요약 보고서 출력
    simulator.print_summary_report()

    # 전체 결과 저장
    filepath = simulator.export_full_results()
    print(f"\n전체 결과 저장: {filepath}")
    print("=" * 70)
