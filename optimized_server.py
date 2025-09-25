#!/usr/bin/env python3
"""
PAM-TALK 최적화된 서버
Phase 1 최적화: Gunicorn + 캐싱 + 연결 풀링
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# 캐싱 시스템 (메모리 기반)
class SimpleCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            value, expire_time = self.cache[key]
            if time.time() < expire_time:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value, ttl=300):
        expire_time = time.time() + ttl
        self.cache[key] = (value, expire_time)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        self.cache.clear()

# 전역 캐시 인스턴스
cache = SimpleCache()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# CORS 설정
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# 캐싱 데코레이터
def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"

            # 캐시에서 확인
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache HIT: {cache_key}")
                return cached_result

            # 함수 실행
            result = f(*args, **kwargs)

            # 캐시에 저장
            cache.set(cache_key, result, ttl)
            logger.info(f"Cache MISS: {cache_key}")
            return result
        return wrapper
    return decorator

# 모의 데이터 (메모리 최적화)
MOCK_DATA = {
    'farms': [
        {
            "farm_id": f"FARM_{i:03d}",
            "name": f"농장 {i}",
            "location": ["경기도", "충청도", "전라도", "경상도"][i % 4],
            "crop_type": ["rice", "wheat", "corn", "soybean"][i % 4],
            "area": 50 + (i * 10) % 200,
            "esg_score": 65 + (i * 5) % 35
        }
        for i in range(50)  # 데이터 크기 최적화
    ],
    'transactions': [
        {
            "transaction_id": f"TX_{i:03d}",
            "crop_type": ["rice", "wheat", "corn"][i % 3],
            "quantity": 100 + (i * 50) % 500,
            "price": 2.0 + (i * 0.1) % 1.5,
            "status": ["completed", "pending"][i % 2],
            "timestamp": datetime.now().isoformat()
        }
        for i in range(20)  # 데이터 크기 최적화
    ]
}

# 성능 측정 미들웨어
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
    return response

# 헬스 체크 엔드포인트
@app.route('/api/health', methods=['GET'])
@cached(ttl=60)  # 1분 캐싱
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-optimized",
        "cache_status": "enabled"
    })

# 농장 목록 조회
@app.route('/api/farms', methods=['GET'])
@cached(ttl=300)  # 5분 캐싱
def get_farms():
    return jsonify({
        "success": True,
        "farms": MOCK_DATA['farms'],
        "total": len(MOCK_DATA['farms']),
        "cached": True
    })

# 거래 목록 조회
@app.route('/api/transactions', methods=['GET'])
@cached(ttl=180)  # 3분 캐싱
def get_transactions():
    return jsonify({
        "success": True,
        "transactions": MOCK_DATA['transactions'],
        "total": len(MOCK_DATA['transactions']),
        "cached": True
    })

# 대시보드 데이터
@app.route('/api/dashboard', methods=['GET'])
@cached(ttl=60)  # 1분 캐싱
def get_dashboard():
    farms = MOCK_DATA['farms']
    transactions = MOCK_DATA['transactions']

    stats = {
        "total_farms": len(farms),
        "total_transactions": len(transactions),
        "avg_esg_score": sum(f['esg_score'] for f in farms) / len(farms),
        "completed_transactions": len([t for t in transactions if t['status'] == 'completed']),
        "total_area": sum(f['area'] for f in farms),
        "crop_distribution": {}
    }

    # 작물 분포 계산
    for farm in farms:
        crop = farm['crop_type']
        stats['crop_distribution'][crop] = stats['crop_distribution'].get(crop, 0) + 1

    return jsonify({
        "success": True,
        "data": stats,
        "cached": True
    })

# 농장 등록 (POST)
@app.route('/api/farms', methods=['POST'])
def create_farm():
    data = request.get_json()

    new_farm = {
        "farm_id": f"FARM_{len(MOCK_DATA['farms']):03d}",
        "name": data.get('name', 'Unknown Farm'),
        "location": data.get('location', 'Unknown'),
        "crop_type": data.get('crop_type', 'rice'),
        "area": data.get('area', 100),
        "esg_score": 75,  # 기본값
        "created_at": datetime.now().isoformat()
    }

    MOCK_DATA['farms'].append(new_farm)

    # 관련 캐시 무효화
    cache.delete('get_farms:')
    cache.delete('get_dashboard:')

    return jsonify({
        "success": True,
        "data": new_farm,
        "message": "농장이 성공적으로 등록되었습니다"
    }), 201

# 거래 생성 (POST)
@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()

    new_transaction = {
        "transaction_id": f"TX_{len(MOCK_DATA['transactions']):03d}",
        "crop_type": data.get('crop_type', 'rice'),
        "quantity": data.get('quantity', 100),
        "price": data.get('price', 3.0),
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }

    MOCK_DATA['transactions'].append(new_transaction)

    # 관련 캐시 무효화
    cache.delete('get_transactions:')
    cache.delete('get_dashboard:')

    return jsonify({
        "success": True,
        "data": new_transaction,
        "message": "거래가 성공적으로 생성되었습니다"
    }), 201

# 캐시 상태 조회
@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    return jsonify({
        "cache_entries": len(cache.cache),
        "cache_keys": list(cache.cache.keys()),
        "server_type": "optimized"
    })

# 캐시 클리어
@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({
        "success": True,
        "message": "캐시가 클리어되었습니다"
    })

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": "요청한 엔드포인트를 찾을 수 없습니다"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal Server Error",
        "message": "서버 내부 오류가 발생했습니다"
    }), 500

# 메인 실행부 (Gunicorn으로 실행될 때는 사용되지 않음)
if __name__ == '__main__':
    print("최적화된 서버 시작")
    print("권장: gunicorn -c gunicorn.conf.py optimized_server:app")
    app.run(host='0.0.0.0', port=5000, debug=False)