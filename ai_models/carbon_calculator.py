#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carbon Reduction Calculator
탄소 절감 계산기 - ISO 14067:2018 표준 및 환경부 배출 계수 기반
"""

import json
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EmissionFactor:
    """배출 계수"""
    truck_transport: float = 0.082  # kg CO₂e/ton·km (환경부)
    plastic_packaging: float = 3.2  # kg CO₂e/kg
    ev_charging_reduction: float = 5.0  # kg CO₂e/건
    eco_packaging_reduction: float = 0.5  # kg CO₂e/건


class CarbonCalculator:
    """탄소 절감 계산기"""

    def __init__(self, population: int = 100000):
        """
        초기화

        Args:
            population: 대상 지역 인구 (기본: 10만 명)
        """
        self.population = population
        self.emission_factor = EmissionFactor()

        # 기준선 설정
        self.baseline = {
            "avg_food_mileage": 150.0,  # km
            "packaging_rate": 85.0,  # %
            "esg_participation": 5.0,  # %
            "monthly_transport": 280.0  # 톤
        }

        # 개선안 설정 (PAM-TALK 도입 후)
        self.improved = {
            "avg_food_mileage": 25.0,  # km
            "packaging_rate": 40.0,  # %
            "esg_participation": 35.0,  # %
            "monthly_ev_charging": 200,  # 건/월
            "monthly_eco_packaging": 500  # 건/월
        }

        # 참여자 규모
        self.participants = {
            "producers": 100,
            "consumers": 2000,
            "stores": 30,
            "enterprises": 5
        }

    def calculate_food_mileage_reduction(self) -> Dict:
        """푸드 마일리지 감축 효과"""
        # 연간 운송량 (톤)
        annual_transport = self.baseline["monthly_transport"] * 12

        # 기존 배출량
        baseline_distance = self.baseline["avg_food_mileage"]
        baseline_emissions = (annual_transport * baseline_distance *
                            self.emission_factor.truck_transport)

        # 개선 후 배출량
        improved_distance = self.improved["avg_food_mileage"]
        improved_emissions = (annual_transport * improved_distance *
                            self.emission_factor.truck_transport)

        # 절감량
        reduction = baseline_emissions - improved_emissions
        reduction_pct = (reduction / baseline_emissions) * 100

        return {
            "category": "푸드 마일리지 감축",
            "baseline": {
                "distance_km": baseline_distance,
                "annual_emissions_ton": round(baseline_emissions / 1000, 1)
            },
            "improved": {
                "distance_km": improved_distance,
                "annual_emissions_ton": round(improved_emissions / 1000, 1)
            },
            "reduction": {
                "distance_reduction_pct": round(
                    (baseline_distance - improved_distance) / baseline_distance * 100, 1
                ),
                "annual_reduction_ton": round(reduction / 1000, 1),
                "reduction_pct": round(reduction_pct, 1)
            }
        }

    def calculate_packaging_reduction(self) -> Dict:
        """포장재 절감 효과"""
        # 연간 포장재 사용량 추정 (kg)
        # 가정: 소비자 1인당 월 4회 구매, 건당 평균 200g 포장재
        monthly_purchases = self.participants["consumers"] * 4
        packaging_per_purchase = 0.2  # kg

        # 기존 포장재 사용량
        baseline_usage = (monthly_purchases * 12 * packaging_per_purchase *
                         (self.baseline["packaging_rate"] / 100))

        # 개선 후 사용량
        improved_usage = (monthly_purchases * 12 * packaging_per_purchase *
                         (self.improved["packaging_rate"] / 100))

        # 절감량
        reduction_kg = baseline_usage - improved_usage
        reduction_emissions = reduction_kg * self.emission_factor.plastic_packaging

        return {
            "category": "포장재 절감",
            "baseline": {
                "usage_rate_pct": self.baseline["packaging_rate"],
                "annual_usage_ton": round(baseline_usage / 1000, 2)
            },
            "improved": {
                "usage_rate_pct": self.improved["packaging_rate"],
                "annual_usage_ton": round(improved_usage / 1000, 2)
            },
            "reduction": {
                "usage_reduction_ton": round(reduction_kg / 1000, 2),
                "annual_reduction_ton": round(reduction_emissions / 1000, 1),
                "reduction_pct": round(
                    (baseline_usage - improved_usage) / baseline_usage * 100, 1
                )
            }
        }

    def calculate_esg_activity_reduction(self) -> Dict:
        """소비자 ESG 활동 효과"""
        # 참여자 수
        baseline_participants = int(self.participants["consumers"] *
                                   (self.baseline["esg_participation"] / 100))
        improved_participants = int(self.participants["consumers"] *
                                   (self.improved["esg_participation"] / 100))

        # 참여자 증가
        participant_increase = improved_participants - baseline_participants

        # 1인당 연간 절감량 (kg CO₂e)
        per_capita_reduction = 40.0  # 대중교통, 자전거 이용 등

        # 총 절감량
        total_reduction = participant_increase * per_capita_reduction

        return {
            "category": "소비자 ESG 활동",
            "baseline": {
                "participation_pct": self.baseline["esg_participation"],
                "participants": baseline_participants
            },
            "improved": {
                "participation_pct": self.improved["esg_participation"],
                "participants": improved_participants
            },
            "reduction": {
                "participant_increase": participant_increase,
                "per_capita_reduction_kg": per_capita_reduction,
                "annual_reduction_ton": round(total_reduction / 1000, 1)
            }
        }

    def calculate_enterprise_infrastructure(self) -> Dict:
        """대기업 인프라 활용 효과"""
        # 전기차 충전
        ev_monthly = self.improved["monthly_ev_charging"]
        ev_annual_reduction = (ev_monthly * 12 *
                              self.emission_factor.ev_charging_reduction)

        # 친환경 포장 지원
        eco_monthly = self.improved["monthly_eco_packaging"]
        eco_annual_reduction = (eco_monthly * 12 *
                               self.emission_factor.eco_packaging_reduction)

        total_reduction = ev_annual_reduction + eco_annual_reduction

        return {
            "category": "대기업 인프라 활용",
            "ev_charging": {
                "monthly_count": ev_monthly,
                "annual_reduction_ton": round(ev_annual_reduction / 1000, 1)
            },
            "eco_packaging": {
                "monthly_count": eco_monthly,
                "annual_reduction_ton": round(eco_annual_reduction / 1000, 1)
            },
            "total": {
                "annual_reduction_ton": round(total_reduction / 1000, 1)
            }
        }

    def calculate_total_reduction(self) -> Dict:
        """총 탄소 절감 효과"""
        food_mileage = self.calculate_food_mileage_reduction()
        packaging = self.calculate_packaging_reduction()
        esg_activity = self.calculate_esg_activity_reduction()
        infrastructure = self.calculate_enterprise_infrastructure()

        total_reduction = (
            food_mileage["reduction"]["annual_reduction_ton"] +
            packaging["reduction"]["annual_reduction_ton"] +
            esg_activity["reduction"]["annual_reduction_ton"] +
            infrastructure["total"]["annual_reduction_ton"]
        )

        # 기준 배출량 (문서 기준)
        baseline_emissions = 298.0  # 톤 CO₂e

        return {
            "baseline_emissions_ton": baseline_emissions,
            "total_reduction_ton": round(total_reduction, 1),
            "reduction_pct": round((total_reduction / baseline_emissions) * 100, 1),
            "equivalent": {
                "passenger_cars": round(total_reduction / 2.3, 0),  # 승용차 1대당 연간 2.3톤
                "description": f"승용차 {int(total_reduction / 2.3)}대의 연간 배출량에 해당"
            }
        }

    def run_calculation(self) -> Dict:
        """전체 탄소 절감 계산 실행"""
        return {
            "standard": "ISO 14067:2018",
            "emission_factors": {
                "truck_transport": f"{self.emission_factor.truck_transport} kg CO₂e/ton·km",
                "plastic_packaging": f"{self.emission_factor.plastic_packaging} kg CO₂e/kg",
                "ev_charging": f"{self.emission_factor.ev_charging_reduction} kg CO₂e/건",
                "eco_packaging": f"{self.emission_factor.eco_packaging_reduction} kg CO₂e/건"
            },
            "details": {
                "food_mileage": self.calculate_food_mileage_reduction(),
                "packaging": self.calculate_packaging_reduction(),
                "esg_activity": self.calculate_esg_activity_reduction(),
                "infrastructure": self.calculate_enterprise_infrastructure()
            },
            "total": self.calculate_total_reduction()
        }

    def export_json(self, filepath: str = "data/simulation/carbon_results.json"):
        """결과를 JSON으로 저장"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results = self.run_calculation()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return filepath


if __name__ == "__main__":
    # 계산기 실행
    calculator = CarbonCalculator(population=100000)
    results = calculator.run_calculation()

    print("=" * 70)
    print("탄소 절감 효과 분석 (ISO 14067:2018 표준)")
    print("=" * 70)

    print(f"\n[적용 배출 계수]")
    for key, value in results["emission_factors"].items():
        print(f"  {key}: {value}")

    print("\n[세부 항목별 절감 효과]")

    # 1. 푸드 마일리지
    fm = results["details"]["food_mileage"]
    print(f"\n1. {fm['category']}")
    print(f"   운송 거리: {fm['baseline']['distance_km']}km → "
          f"{fm['improved']['distance_km']}km "
          f"({fm['reduction']['distance_reduction_pct']}% 감소)")
    print(f"   연간 절감: {fm['reduction']['annual_reduction_ton']}톤 CO₂e "
          f"({fm['reduction']['reduction_pct']}% 절감)")

    # 2. 포장재
    pkg = results["details"]["packaging"]
    print(f"\n2. {pkg['category']}")
    print(f"   사용률: {pkg['baseline']['usage_rate_pct']}% → "
          f"{pkg['improved']['usage_rate_pct']}%")
    print(f"   연간 절감: {pkg['reduction']['annual_reduction_ton']}톤 CO₂e "
          f"({pkg['reduction']['reduction_pct']}% 절감)")

    # 3. ESG 활동
    esg = results["details"]["esg_activity"]
    print(f"\n3. {esg['category']}")
    print(f"   참여율: {esg['baseline']['participation_pct']}% → "
          f"{esg['improved']['participation_pct']}%")
    print(f"   참여자 증가: {esg['reduction']['participant_increase']}명")
    print(f"   연간 절감: {esg['reduction']['annual_reduction_ton']}톤 CO₂e")

    # 4. 인프라
    inf = results["details"]["infrastructure"]
    print(f"\n4. {inf['category']}")
    print(f"   전기차 충전: 월 {inf['ev_charging']['monthly_count']}건, "
          f"연간 {inf['ev_charging']['annual_reduction_ton']}톤 CO₂e 절감")
    print(f"   친환경 포장: 월 {inf['eco_packaging']['monthly_count']}건, "
          f"연간 {inf['eco_packaging']['annual_reduction_ton']}톤 CO₂e 절감")

    # 총 효과
    total = results["total"]
    print("\n" + "=" * 70)
    print("[총 탄소 절감 효과]")
    print(f"기준 배출량: {total['baseline_emissions_ton']}톤 CO₂e")
    print(f"총 절감량: {total['total_reduction_ton']}톤 CO₂e")
    print(f"절감률: {total['reduction_pct']}%")
    print(f"환산: {total['equivalent']['description']}")
    print("=" * 70)

    # JSON 저장
    filepath = calculator.export_json()
    print(f"\n결과 저장: {filepath}")
