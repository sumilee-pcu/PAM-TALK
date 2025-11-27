#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
농부-소비자 자동 매칭 알고리즘
PAM-TALK Farmer-Consumer Matching Engine
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import math

logger = logging.getLogger(__name__)


@dataclass
class FarmerProfile:
    """농부 프로필"""
    farmer_id: str
    name: str
    region: str
    farm_type: str
    crop_types: List[str]
    certifications: List[str]
    esg_score: float
    latitude: float
    longitude: float
    farming_method: str  # organic, conventional, sustainable
    available_quantity: float  # kg
    price_range: tuple  # (min, max) per kg


@dataclass
class ConsumerProfile:
    """소비자 프로필"""
    consumer_id: str
    name: str
    region: str
    latitude: float
    longitude: float
    preferences: Dict
    # preferences = {
    #     'product_types': ['tomato', 'lettuce'],
    #     'farming_method': 'organic',
    #     'max_distance_km': 50,
    #     'max_price_per_kg': 5000,
    #     'min_esg_score': 70,
    #     'certifications_required': ['organic', 'gmo_free']
    # }


@dataclass
class MatchResult:
    """매칭 결과"""
    farmer_id: str
    farmer_name: str
    consumer_id: str
    consumer_name: str
    match_score: float  # 0-100
    distance_km: float
    reason: str
    breakdown: Dict
    created_at: str


class FarmerConsumerMatcher:
    """농부-소비자 매칭 엔진"""

    # 가중치 설정 (합계 = 1.0)
    WEIGHTS = {
        'distance': 0.25,      # 거리
        'price': 0.20,         # 가격
        'esg_score': 0.20,     # ESG 점수
        'farming_method': 0.15,  # 재배 방식
        'product_match': 0.10,   # 제품 일치도
        'certification': 0.10    # 인증서
    }

    def __init__(self):
        self.match_history = []

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        두 지점 간 거리 계산 (Haversine formula)
        Returns: 거리 (km)
        """
        R = 6371  # 지구 반지름 (km)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return round(distance, 2)

    def score_distance(self, distance_km: float, max_distance: float) -> float:
        """
        거리 점수 계산 (0-100)
        가까울수록 높은 점수
        """
        if distance_km > max_distance:
            return 0.0

        # 선형 감소
        score = 100 * (1 - distance_km / max_distance)
        return max(0.0, score)

    def score_price(self, farmer_price_range: tuple, consumer_max_price: float) -> float:
        """
        가격 점수 계산 (0-100)
        소비자 예산 내에서 저렴할수록 높은 점수
        """
        min_price, max_price = farmer_price_range

        if min_price > consumer_max_price:
            return 0.0  # 예산 초과

        # 평균 가격 계산
        avg_price = (min_price + max_price) / 2

        if avg_price <= consumer_max_price * 0.7:
            return 100.0  # 예산의 70% 이하면 만점
        elif avg_price <= consumer_max_price:
            # 70% ~ 100% 범위에서 선형 감소
            score = 100 * (consumer_max_price - avg_price) / (consumer_max_price * 0.3)
            return score
        else:
            return 0.0

    def score_esg(self, farmer_esg: float, consumer_min_esg: float) -> float:
        """
        ESG 점수 비교 (0-100)
        """
        if farmer_esg < consumer_min_esg:
            return 0.0

        # ESG 점수가 높을수록 높은 점수
        # 기준치 이상이면 그에 비례하여 점수 부여
        if farmer_esg >= 90:
            return 100.0
        elif farmer_esg >= consumer_min_esg:
            score = 50 + (farmer_esg - consumer_min_esg) * 50 / (90 - consumer_min_esg)
            return min(100.0, score)
        else:
            return 0.0

    def score_farming_method(self, farmer_method: str, consumer_preference: str) -> float:
        """
        재배 방식 점수 (0-100)
        """
        method_scores = {
            'organic': {'organic': 100, 'sustainable': 60, 'conventional': 20},
            'sustainable': {'organic': 80, 'sustainable': 100, 'conventional': 40},
            'conventional': {'organic': 50, 'sustainable': 70, 'conventional': 100}
        }

        if consumer_preference not in method_scores:
            return 50.0  # 선호도 없으면 중간 점수

        return method_scores[consumer_preference].get(farmer_method, 0.0)

    def score_product_match(self, farmer_crops: List[str], consumer_products: List[str]) -> float:
        """
        제품 일치도 점수 (0-100)
        """
        if not consumer_products:
            return 100.0  # 선호 제품 없으면 모두 매칭

        # 교집합 계산
        matched = set(farmer_crops) & set(consumer_products)

        if not matched:
            return 0.0

        # 일치 비율
        match_ratio = len(matched) / len(consumer_products)
        return 100 * match_ratio

    def score_certification(self, farmer_certs: List[str], consumer_required: List[str]) -> float:
        """
        인증서 점수 (0-100)
        """
        if not consumer_required:
            return 100.0  # 요구 인증서 없으면 만점

        # 필수 인증서 보유 확인
        farmer_certs_set = set(cert.lower() for cert in farmer_certs)
        required_set = set(cert.lower() for cert in consumer_required)

        matched = farmer_certs_set & required_set

        if not matched:
            return 0.0

        # 요구 인증서를 모두 보유하면 만점
        if matched == required_set:
            return 100.0

        # 일부만 보유하면 비율에 따라 점수
        return 100 * len(matched) / len(required_set)

    def match_single(self, farmer: FarmerProfile, consumer: ConsumerProfile) -> Optional[MatchResult]:
        """
        단일 농부-소비자 매칭
        """
        preferences = consumer.preferences

        # 1. 거리 계산
        distance_km = self.calculate_distance(
            farmer.latitude, farmer.longitude,
            consumer.latitude, consumer.longitude
        )

        # 2. 각 요소별 점수 계산
        scores = {}

        # 거리 점수
        max_distance = preferences.get('max_distance_km', 100)
        scores['distance'] = self.score_distance(distance_km, max_distance)

        # 가격 점수
        max_price = preferences.get('max_price_per_kg', 10000)
        scores['price'] = self.score_price(farmer.price_range, max_price)

        # ESG 점수
        min_esg = preferences.get('min_esg_score', 0)
        scores['esg_score'] = self.score_esg(farmer.esg_score, min_esg)

        # 재배 방식 점수
        preferred_method = preferences.get('farming_method', '')
        scores['farming_method'] = self.score_farming_method(
            farmer.farming_method, preferred_method
        )

        # 제품 일치도
        product_types = preferences.get('product_types', [])
        scores['product_match'] = self.score_product_match(farmer.crop_types, product_types)

        # 인증서 점수
        required_certs = preferences.get('certifications_required', [])
        scores['certification'] = self.score_certification(farmer.certifications, required_certs)

        # 3. 가중 평균 계산
        total_score = 0.0
        for key, weight in self.WEIGHTS.items():
            total_score += scores[key] * weight

        # 4. 최소 임계값 체크 (총점 40점 이상만 매칭)
        if total_score < 40.0:
            return None

        # 5. 매칭 사유 생성
        reason_parts = []
        if scores['distance'] >= 80:
            reason_parts.append(f"가까운 거리 ({distance_km}km)")
        if scores['esg_score'] >= 80:
            reason_parts.append(f"높은 ESG 점수 ({farmer.esg_score})")
        if scores['farming_method'] >= 90:
            reason_parts.append(f"선호 재배 방식 ({farmer.farming_method})")
        if scores['product_match'] == 100:
            reason_parts.append("원하는 제품 모두 보유")

        reason = ", ".join(reason_parts) if reason_parts else "종합 점수 양호"

        # 6. 매칭 결과 생성
        result = MatchResult(
            farmer_id=farmer.farmer_id,
            farmer_name=farmer.name,
            consumer_id=consumer.consumer_id,
            consumer_name=consumer.name,
            match_score=round(total_score, 2),
            distance_km=distance_km,
            reason=reason,
            breakdown=scores,
            created_at=datetime.now().isoformat()
        )

        # 히스토리 저장
        self.match_history.append(result)

        return result

    def find_matches(
        self,
        farmers: List[FarmerProfile],
        consumer: ConsumerProfile,
        top_n: int = 10
    ) -> List[MatchResult]:
        """
        소비자에게 가장 적합한 농부 찾기
        """
        matches = []

        for farmer in farmers:
            result = self.match_single(farmer, consumer)
            if result:
                matches.append(result)

        # 점수순 정렬
        matches.sort(key=lambda x: x.match_score, reverse=True)

        logger.info(
            f"Consumer {consumer.consumer_id} matched with {len(matches)} farmers. "
            f"Returning top {top_n}."
        )

        return matches[:top_n]

    def find_consumers_for_farmer(
        self,
        farmer: FarmerProfile,
        consumers: List[ConsumerProfile],
        top_n: int = 10
    ) -> List[MatchResult]:
        """
        농부에게 가장 적합한 소비자 찾기
        """
        matches = []

        for consumer in consumers:
            result = self.match_single(farmer, consumer)
            if result:
                matches.append(result)

        # 점수순 정렬
        matches.sort(key=lambda x: x.match_score, reverse=True)

        logger.info(
            f"Farmer {farmer.farmer_id} matched with {len(matches)} consumers. "
            f"Returning top {top_n}."
        )

        return matches[:top_n]

    def mutual_best_matches(
        self,
        farmers: List[FarmerProfile],
        consumers: List[ConsumerProfile],
        threshold: float = 60.0
    ) -> List[MatchResult]:
        """
        상호 최적 매칭 찾기
        (양방향에서 모두 높은 점수를 받는 매칭)
        """
        all_matches = []

        for farmer in farmers:
            for consumer in consumers:
                result = self.match_single(farmer, consumer)
                if result and result.match_score >= threshold:
                    all_matches.append(result)

        # 점수순 정렬
        all_matches.sort(key=lambda x: x.match_score, reverse=True)

        logger.info(
            f"Found {len(all_matches)} mutual matches above {threshold} threshold"
        )

        return all_matches


# 예제 사용법
if __name__ == "__main__":
    # 테스트 데이터
    farmer1 = FarmerProfile(
        farmer_id="F001",
        name="김농부",
        region="경기도 용인",
        farm_type="유기농 채소농장",
        crop_types=["tomato", "lettuce", "cucumber"],
        certifications=["organic", "gmo_free"],
        esg_score=85.0,
        latitude=37.2411,
        longitude=127.1776,
        farming_method="organic",
        available_quantity=500.0,
        price_range=(3000, 5000)
    )

    consumer1 = ConsumerProfile(
        consumer_id="C001",
        name="이소비",
        region="서울 강남",
        latitude=37.4979,
        longitude=127.0276,
        preferences={
            'product_types': ['tomato', 'lettuce'],
            'farming_method': 'organic',
            'max_distance_km': 50,
            'max_price_per_kg': 6000,
            'min_esg_score': 70,
            'certifications_required': ['organic']
        }
    )

    # 매칭 수행
    matcher = FarmerConsumerMatcher()
    result = matcher.match_single(farmer1, consumer1)

    if result:
        print(f"\n=== 매칭 결과 ===")
        print(f"농부: {result.farmer_name}")
        print(f"소비자: {result.consumer_name}")
        print(f"매칭 점수: {result.match_score}/100")
        print(f"거리: {result.distance_km}km")
        print(f"사유: {result.reason}")
        print(f"\n상세 점수:")
        for key, score in result.breakdown.items():
            print(f"  - {key}: {score:.1f}/100")
    else:
        print("매칭 실패")
