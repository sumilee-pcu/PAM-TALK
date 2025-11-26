#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Economic Impact Analyzer
경제적 효과 분석 - 산업연관분석 기법 적용
"""

import json
from typing import Dict
from dataclasses import dataclass


@dataclass
class RegionalMultiplier:
    """지역 승수 (한국은행 산업연관표 기준)"""
    production: float = 2.2  # 생산 유발 계수
    value_added: float = 1.8  # 부가가치 유발 계수
    employment: float = 0.000023  # 고용 유발 계수 (명/백만원)


class EconomicAnalyzer:
    """경제 효과 분석기"""

    def __init__(self, population: int = 100000):
        """
        초기화

        Args:
            population: 대상 지역 인구 (기본: 10만 명)
        """
        self.population = population
        self.multiplier = RegionalMultiplier()

        # 참여자 규모
        self.participants = {
            "producers": 100,
            "consumers": 2000,
            "stores": 30,
            "enterprises": 5
        }

        # 농산물 거래 규모 추정
        self.transaction = {
            "avg_monthly_per_consumer": 150000,  # 원/월 (1인당)
            "avg_monthly_per_store": 10000000,  # 원/월 (가맹점당)
        }

    def calculate_direct_effects(self) -> Dict:
        """직접 효과 계산"""

        # 1. 지역 내 소비 증대
        # 로컬푸드 비중 증가: 23% → 70%
        baseline_local_ratio = 0.23
        improved_local_ratio = 0.70

        # 연간 총 거래액
        annual_consumer_spending = (self.participants["consumers"] *
                                   self.transaction["avg_monthly_per_consumer"] * 12)

        # 로컬푸드 소비 증가분
        local_consumption_increase = annual_consumer_spending * (
            improved_local_ratio - baseline_local_ratio
        )

        # 2. 생산자 소득 증가
        # 수취가격 28% 상승
        producer_price_increase_rate = 0.28

        # 생산자 총 매출 추정 (연간)
        annual_producer_revenue = (self.participants["stores"] *
                                  self.transaction["avg_monthly_per_store"] * 12 * 0.6)

        producer_income_increase = annual_producer_revenue * producer_price_increase_rate

        # 3. 가맹점 매출 증대
        # 디지털 쿠폰 결제 도입으로 매출 증가 (추정 15%)
        store_revenue_increase_rate = 0.15

        annual_store_revenue = (self.participants["stores"] *
                               self.transaction["avg_monthly_per_store"] * 12)

        store_revenue_increase = annual_store_revenue * store_revenue_increase_rate

        # 총 직접 효과
        total_direct = (local_consumption_increase +
                       producer_income_increase +
                       store_revenue_increase)

        return {
            "local_consumption": {
                "description": "지역 내 소비 증대",
                "baseline_ratio": baseline_local_ratio * 100,
                "improved_ratio": improved_local_ratio * 100,
                "annual_increase_krw": round(local_consumption_increase / 100000000, 1),
                "annual_increase_billion": round(local_consumption_increase / 100000000, 1)
            },
            "producer_income": {
                "description": "생산자 소득 증가",
                "price_increase_rate": producer_price_increase_rate * 100,
                "annual_increase_krw": round(producer_income_increase / 100000000, 1),
                "annual_increase_billion": round(producer_income_increase / 100000000, 1)
            },
            "store_revenue": {
                "description": "가맹점 매출 증대",
                "revenue_increase_rate": store_revenue_increase_rate * 100,
                "annual_increase_krw": round(store_revenue_increase / 100000000, 1),
                "annual_increase_billion": round(store_revenue_increase / 100000000, 1)
            },
            "total": {
                "annual_increase_krw": round(total_direct / 100000000, 1),
                "annual_increase_billion": round(total_direct / 100000000, 1)
            }
        }

    def calculate_indirect_effects(self, direct_total: float) -> Dict:
        """간접 효과 계산 (산업연관분석)"""

        # 생산 유발 효과
        production_induced = direct_total * self.multiplier.production

        # 부가가치 유발 효과
        value_added_induced = direct_total * self.multiplier.value_added

        # 고용 유발 효과 (명)
        employment_induced = direct_total * self.multiplier.employment

        return {
            "production_induced": {
                "description": "생산 유발 효과",
                "multiplier": self.multiplier.production,
                "amount_billion": round(production_induced / 100000000, 1)
            },
            "value_added_induced": {
                "description": "부가가치 유발 효과",
                "multiplier": self.multiplier.value_added,
                "amount_billion": round(value_added_induced / 100000000, 1)
            },
            "employment_induced": {
                "description": "고용 유발 효과",
                "multiplier": self.multiplier.employment,
                "jobs_created": round(employment_induced, 0)
            },
            "total": {
                "amount_billion": round(production_induced / 100000000, 1)
            }
        }

    def calculate_total_economic_impact(self) -> Dict:
        """총 경제적 효과"""

        # 직접 효과
        direct_effects = self.calculate_direct_effects()
        direct_total = direct_effects["total"]["annual_increase_krw"] * 100000000

        # 간접 효과
        indirect_effects = self.calculate_indirect_effects(direct_total)
        indirect_total = indirect_effects["total"]["amount_billion"] * 100000000

        # 총 효과
        total_impact = direct_total + indirect_total
        per_capita_benefit = total_impact / self.population

        return {
            "direct_total_billion": direct_effects["total"]["annual_increase_billion"],
            "indirect_total_billion": indirect_effects["total"]["amount_billion"],
            "total_impact_billion": round(total_impact / 100000000, 1),
            "per_capita_benefit_krw": round(per_capita_benefit, 0),
            "employment_created": indirect_effects["employment_induced"]["jobs_created"]
        }

    def run_analysis(self) -> Dict:
        """전체 경제 효과 분석 실행"""

        direct = self.calculate_direct_effects()
        direct_total = direct["total"]["annual_increase_krw"] * 100000000
        indirect = self.calculate_indirect_effects(direct_total)
        total = self.calculate_total_economic_impact()

        return {
            "methodology": "산업연관분석 (Input-Output Analysis)",
            "reference": "한국은행 산업연관표 기준",
            "region": {
                "population": self.population,
                "participants": self.participants
            },
            "multipliers": {
                "production": self.multiplier.production,
                "value_added": self.multiplier.value_added,
                "employment": self.multiplier.employment
            },
            "direct_effects": direct,
            "indirect_effects": indirect,
            "total_impact": total
        }

    def export_json(self, filepath: str = "data/simulation/economic_results.json"):
        """결과를 JSON으로 저장"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results = self.run_analysis()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return filepath


if __name__ == "__main__":
    # 분석기 실행
    analyzer = EconomicAnalyzer(population=100000)
    results = analyzer.run_analysis()

    print("=" * 70)
    print("경제적 효과 분석 (산업연관분석)")
    print("=" * 70)

    print(f"\n[분석 방법론]")
    print(f"기법: {results['methodology']}")
    print(f"기준: {results['reference']}")
    print(f"대상 지역 인구: {results['region']['population']:,}명")

    print(f"\n[적용 승수]")
    print(f"생산 유발 계수: {results['multipliers']['production']}")
    print(f"부가가치 유발 계수: {results['multipliers']['value_added']}")
    print(f"고용 유발 계수: {results['multipliers']['employment']}")

    print("\n[직접 효과]")
    direct = results["direct_effects"]
    print(f"1. {direct['local_consumption']['description']}")
    print(f"   로컬푸드 비중: {direct['local_consumption']['baseline_ratio']}% → "
          f"{direct['local_consumption']['improved_ratio']}%")
    print(f"   연간 증가: {direct['local_consumption']['annual_increase_billion']}억원")

    print(f"\n2. {direct['producer_income']['description']}")
    print(f"   수취가격 증가: {direct['producer_income']['price_increase_rate']}%")
    print(f"   연간 증가: {direct['producer_income']['annual_increase_billion']}억원")

    print(f"\n3. {direct['store_revenue']['description']}")
    print(f"   매출 증가율: {direct['store_revenue']['revenue_increase_rate']}%")
    print(f"   연간 증가: {direct['store_revenue']['annual_increase_billion']}억원")

    print(f"\n직접 효과 합계: {direct['total']['annual_increase_billion']}억원")

    print("\n[간접 효과]")
    indirect = results["indirect_effects"]
    print(f"1. {indirect['production_induced']['description']}: "
          f"{indirect['production_induced']['amount_billion']}억원")
    print(f"2. {indirect['value_added_induced']['description']}: "
          f"{indirect['value_added_induced']['amount_billion']}억원")
    print(f"3. {indirect['employment_induced']['description']}: "
          f"{int(indirect['employment_induced']['jobs_created'])}명 추가 고용")

    print(f"\n간접 효과 합계: {indirect['total']['amount_billion']}억원")

    print("\n" + "=" * 70)
    print("[총 경제적 효과]")
    total = results["total_impact"]
    print(f"직접 효과: {total['direct_total_billion']}억원")
    print(f"간접 효과: {total['indirect_total_billion']}억원")
    print(f"총 효과: {total['total_impact_billion']}억원")
    print(f"1인당 편익: {total['per_capita_benefit_krw']:,}원/년")
    print(f"고용 창출: 약 {int(total['employment_created'])}명")
    print("=" * 70)

    # JSON 저장
    filepath = analyzer.export_json()
    print(f"\n결과 저장: {filepath}")
