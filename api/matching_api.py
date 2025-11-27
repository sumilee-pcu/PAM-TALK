#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
농부-소비자 매칭 REST API
PAM-TALK Matching API
"""

import logging
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict

from api.matching_algorithm import (
    FarmerConsumerMatcher,
    FarmerProfile,
    ConsumerProfile
)
from api.auth_middleware import require_auth

logger = logging.getLogger(__name__)

# Blueprint 생성
matching_bp = Blueprint('matching', __name__, url_prefix='/api/matching')

# 매칭 엔진 인스턴스
matcher = FarmerConsumerMatcher()


def create_error_response(message: str, status_code: int = 400):
    """에러 응답 생성"""
    return {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    }


def create_success_response(data: any, message: str = None):
    """성공 응답 생성"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    if message:
        response["message"] = message
    return response


@matching_bp.route('/find-farmers', methods=['POST'])
@require_auth
def find_farmers_for_consumer():
    """
    소비자에게 적합한 농부 찾기

    POST /api/matching/find-farmers
    {
        "consumer_id": "C001",
        "consumer_name": "이소비",
        "region": "서울 강남",
        "latitude": 37.4979,
        "longitude": 127.0276,
        "preferences": {
            "product_types": ["tomato", "lettuce"],
            "farming_method": "organic",
            "max_distance_km": 50,
            "max_price_per_kg": 6000,
            "min_esg_score": 70,
            "certifications_required": ["organic"]
        },
        "top_n": 10
    }
    """
    try:
        data = request.get_json()

        # 필수 필드 확인
        required_fields = ['consumer_id', 'consumer_name', 'latitude', 'longitude']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing)}"
            )), 400

        # 소비자 프로필 생성
        consumer = ConsumerProfile(
            consumer_id=data['consumer_id'],
            name=data['consumer_name'],
            region=data.get('region', ''),
            latitude=data['latitude'],
            longitude=data['longitude'],
            preferences=data.get('preferences', {})
        )

        # 농부 데이터 가져오기 (DB에서 조회 - 여기서는 예제 데이터)
        farmers = get_all_farmers()

        # 매칭 수행
        top_n = data.get('top_n', 10)
        matches = matcher.find_matches(farmers, consumer, top_n)

        # 결과 포맷팅
        results = []
        for match in matches:
            results.append({
                'farmer_id': match.farmer_id,
                'farmer_name': match.farmer_name,
                'match_score': match.match_score,
                'distance_km': match.distance_km,
                'reason': match.reason,
                'breakdown': match.breakdown
            })

        return jsonify(create_success_response(
            {
                'consumer_id': consumer.consumer_id,
                'total_matches': len(results),
                'matches': results
            },
            f"{len(results)}명의 농부를 찾았습니다"
        )), 200

    except Exception as e:
        logger.error(f"Find farmers error: {e}")
        return jsonify(create_error_response(f"매칭 실패: {str(e)}")), 500


@matching_bp.route('/find-consumers', methods=['POST'])
@require_auth
def find_consumers_for_farmer():
    """
    농부에게 적합한 소비자 찾기

    POST /api/matching/find-consumers
    {
        "farmer_id": "F001",
        "farmer_name": "김농부",
        "region": "경기도 용인",
        "farm_type": "유기농 채소농장",
        "crop_types": ["tomato", "lettuce"],
        "certifications": ["organic", "gmo_free"],
        "esg_score": 85.0,
        "latitude": 37.2411,
        "longitude": 127.1776,
        "farming_method": "organic",
        "available_quantity": 500.0,
        "price_range": [3000, 5000],
        "top_n": 10
    }
    """
    try:
        data = request.get_json()

        # 필수 필드 확인
        required_fields = ['farmer_id', 'farmer_name', 'latitude', 'longitude']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing)}"
            )), 400

        # 농부 프로필 생성
        price_range = data.get('price_range', [0, 10000])
        farmer = FarmerProfile(
            farmer_id=data['farmer_id'],
            name=data['farmer_name'],
            region=data.get('region', ''),
            farm_type=data.get('farm_type', ''),
            crop_types=data.get('crop_types', []),
            certifications=data.get('certifications', []),
            esg_score=data.get('esg_score', 0.0),
            latitude=data['latitude'],
            longitude=data['longitude'],
            farming_method=data.get('farming_method', 'conventional'),
            available_quantity=data.get('available_quantity', 0.0),
            price_range=(price_range[0], price_range[1])
        )

        # 소비자 데이터 가져오기 (DB에서 조회)
        consumers = get_all_consumers()

        # 매칭 수행
        top_n = data.get('top_n', 10)
        matches = matcher.find_consumers_for_farmer(farmer, consumers, top_n)

        # 결과 포맷팅
        results = []
        for match in matches:
            results.append({
                'consumer_id': match.consumer_id,
                'consumer_name': match.consumer_name,
                'match_score': match.match_score,
                'distance_km': match.distance_km,
                'reason': match.reason,
                'breakdown': match.breakdown
            })

        return jsonify(create_success_response(
            {
                'farmer_id': farmer.farmer_id,
                'total_matches': len(results),
                'matches': results
            },
            f"{len(results)}명의 소비자를 찾았습니다"
        )), 200

    except Exception as e:
        logger.error(f"Find consumers error: {e}")
        return jsonify(create_error_response(f"매칭 실패: {str(e)}")), 500


@matching_bp.route('/mutual-matches', methods=['POST'])
@require_auth
def get_mutual_matches():
    """
    상호 최적 매칭 찾기

    POST /api/matching/mutual-matches
    {
        "threshold": 60.0,
        "limit": 50
    }
    """
    try:
        data = request.get_json() or {}

        # 농부 및 소비자 데이터 가져오기
        farmers = get_all_farmers()
        consumers = get_all_consumers()

        # 상호 매칭 수행
        threshold = data.get('threshold', 60.0)
        matches = matcher.mutual_best_matches(farmers, consumers, threshold)

        # 결과 제한
        limit = data.get('limit', 50)
        matches = matches[:limit]

        # 결과 포맷팅
        results = []
        for match in matches:
            results.append({
                'farmer_id': match.farmer_id,
                'farmer_name': match.farmer_name,
                'consumer_id': match.consumer_id,
                'consumer_name': match.consumer_name,
                'match_score': match.match_score,
                'distance_km': match.distance_km,
                'reason': match.reason,
                'breakdown': match.breakdown,
                'created_at': match.created_at
            })

        return jsonify(create_success_response(
            {
                'total_matches': len(results),
                'threshold': threshold,
                'matches': results
            },
            f"{len(results)}개의 상호 매칭을 찾았습니다"
        )), 200

    except Exception as e:
        logger.error(f"Mutual matches error: {e}")
        return jsonify(create_error_response(f"매칭 실패: {str(e)}")), 500


@matching_bp.route('/match-history', methods=['GET'])
@require_auth
def get_match_history():
    """매칭 히스토리 조회"""
    try:
        # 히스토리 조회
        history = matcher.match_history

        # 최근 N개만 반환
        limit = request.args.get('limit', 100, type=int)
        history = history[-limit:]

        results = []
        for match in history:
            results.append({
                'farmer_id': match.farmer_id,
                'farmer_name': match.farmer_name,
                'consumer_id': match.consumer_id,
                'consumer_name': match.consumer_name,
                'match_score': match.match_score,
                'distance_km': match.distance_km,
                'reason': match.reason,
                'created_at': match.created_at
            })

        return jsonify(create_success_response(
            {
                'total_count': len(results),
                'matches': results
            }
        )), 200

    except Exception as e:
        logger.error(f"Match history error: {e}")
        return jsonify(create_error_response(f"히스토리 조회 실패: {str(e)}")), 500


# ==================== 데모 데이터 함수 ====================

def get_all_farmers() -> List[FarmerProfile]:
    """
    모든 농부 데이터 조회 (DB에서 가져와야 함)
    여기서는 데모 데이터 반환
    """
    # TODO: 실제로는 DB에서 조회
    return [
        FarmerProfile(
            farmer_id="F001",
            name="김유기",
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
        ),
        FarmerProfile(
            farmer_id="F002",
            name="이친환",
            region="강원도 홍천",
            farm_type="지속가능 과수원",
            crop_types=["apple", "pear"],
            certifications=["sustainable", "carbon_neutral"],
            esg_score=90.0,
            latitude=37.6972,
            longitude=127.8886,
            farming_method="sustainable",
            available_quantity=1000.0,
            price_range=(4000, 7000)
        ),
        FarmerProfile(
            farmer_id="F003",
            name="박일반",
            region="충청남도 천안",
            farm_type="일반 농장",
            crop_types=["rice", "corn"],
            certifications=[],
            esg_score=60.0,
            latitude=36.8151,
            longitude=127.1139,
            farming_method="conventional",
            available_quantity=2000.0,
            price_range=(1500, 3000)
        )
    ]


def get_all_consumers() -> List[ConsumerProfile]:
    """
    모든 소비자 데이터 조회 (DB에서 가져와야 함)
    여기서는 데모 데이터 반환
    """
    # TODO: 실제로는 DB에서 조회
    return [
        ConsumerProfile(
            consumer_id="C001",
            name="이서울",
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
        ),
        ConsumerProfile(
            consumer_id="C002",
            name="김과일",
            region="경기도 성남",
            latitude=37.4201,
            longitude=127.1262,
            preferences={
                'product_types': ['apple', 'pear'],
                'farming_method': 'sustainable',
                'max_distance_km': 100,
                'max_price_per_kg': 8000,
                'min_esg_score': 80,
                'certifications_required': ['sustainable']
            }
        ),
        ConsumerProfile(
            consumer_id="C003",
            name="박저렴",
            region="인천 남동",
            latitude=37.4481,
            longitude=126.7319,
            preferences={
                'product_types': ['rice', 'corn'],
                'farming_method': 'conventional',
                'max_distance_km': 150,
                'max_price_per_kg': 3500,
                'min_esg_score': 50,
                'certifications_required': []
            }
        )
    ]


# Health check
@matching_bp.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        'status': 'ok',
        'service': 'matching-api',
        'timestamp': datetime.now().isoformat(),
        'match_history_count': len(matcher.match_history)
    }), 200


if __name__ == '__main__':
    # 개발 모드 테스트
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(matching_bp)

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Matching API Server")
    app.run(debug=True, host='0.0.0.0', port=5002)
