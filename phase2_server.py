#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Phase 2 고성능 서버
- Waitress 프로덕션 WSGI 서버
- 고급 캐싱 시스템
- 비동기 백그라운드 태스크
- 연결 풀링 최적화
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# 고급 캐시 시스템 import
from advanced_cache import global_cache, advanced_cache

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

# 백그라운드 작업을 위한 스레드 풀
background_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="PAMTalk-BG")

# 성능 미들웨어
@app.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = f"req_{int(time.time() * 1000)}"

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        response.headers['X-Cache-Status'] = getattr(g, 'cache_status', 'miss')

        # 느린 요청 로깅
        if duration > 1.0:
            logger.warning(f"Slow request: {request.path} took {duration:.3f}s")

    return response

# 백그라운드 태스크 데코레이터
def background_task(func):
    """백그라운드에서 실행할 작업 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        future = background_executor.submit(func, *args, **kwargs)
        return future
    return wrapper

# 최적화된 모의 데이터 (더 작고 빠른 데이터셋)
class OptimizedDataStore:
    def __init__(self):
        self._farms = self._generate_farms_data()
        self._transactions = self._generate_transactions_data()
        self._lock = threading.RLock()

    def _generate_farms_data(self):
        return [
            {
                "farm_id": f"FARM_{i:03d}",
                "name": f"농장 {i}",
                "location": ["경기도", "충청도", "전라도", "경상도"][i % 4],
                "crop_type": ["rice", "wheat", "corn", "soybean"][i % 4],
                "area": 50 + (i * 10) % 200,
                "esg_score": 65 + (i * 5) % 35,
                "status": "active"
            }
            for i in range(20)  # 더 작은 데이터셋
        ]

    def _generate_transactions_data(self):
        return [
            {
                "transaction_id": f"TX_{i:03d}",
                "crop_type": ["rice", "wheat", "corn"][i % 3],
                "quantity": 100 + (i * 50) % 500,
                "price": 2.0 + (i * 0.1) % 1.5,
                "status": ["completed", "pending"][i % 2],
                "timestamp": datetime.now().isoformat()
            }
            for i in range(10)  # 더 작은 데이터셋
        ]

    def get_farms(self, limit=None):
        with self._lock:
            return self._farms[:limit] if limit else self._farms.copy()

    def get_transactions(self, limit=None):
        with self._lock:
            return self._transactions[:limit] if limit else self._transactions.copy()

    def add_farm(self, farm_data):
        with self._lock:
            farm_data['farm_id'] = f"FARM_{len(self._farms):03d}"
            self._farms.append(farm_data)
            return farm_data

    def add_transaction(self, tx_data):
        with self._lock:
            tx_data['transaction_id'] = f"TX_{len(self._transactions):03d}"
            self._transactions.append(tx_data)
            return tx_data

# 전역 데이터 저장소
data_store = OptimizedDataStore()

# 백그라운드 AI 처리 시뮬레이션
@background_task
def process_esg_calculation(farm_data):
    """ESG 점수 계산 (백그라운드)"""
    time.sleep(0.1)  # AI 처리 시뮬레이션

    score = 75 + hash(farm_data.get('name', '')) % 25
    logger.info(f"ESG calculation completed for {farm_data.get('name')}: {score}")
    return score

@background_task
def process_demand_prediction(crop_data):
    """수요 예측 처리 (백그라운드)"""
    time.sleep(0.2)  # AI 모델 실행 시뮬레이션

    prediction = {
        'crop_type': crop_data.get('crop_type', 'rice'),
        'predicted_demand': 1000 + hash(str(crop_data)) % 500,
        'confidence': 0.85,
        'processed_at': datetime.now().isoformat()
    }

    logger.info(f"Demand prediction completed for {crop_data.get('crop_type')}")
    return prediction

# API 엔드포인트들

@app.route('/api/health', methods=['GET'])
def health_check():
    cache_stats = global_cache.get_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-phase2",
        "server_type": "waitress",
        "cache_stats": cache_stats,
        "background_workers": background_executor._max_workers
    }

@app.route('/api/farms', methods=['GET'])
def get_farms():
    # 수동 캐싱 구현
    cache_key = 'farms_list'
    cached_result = global_cache.get(cache_key)

    if cached_result is not None:
        g.cache_status = 'hit'
        return cached_result

    g.cache_status = 'miss'
    farms = data_store.get_farms()

    result = {
        "success": True,
        "farms": farms,
        "total": len(farms),
        "cached": False
    }

    global_cache.set(cache_key, result, ttl=120)  # 2분 캐싱
    return result

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    cache_key = 'transactions_list'
    cached_result = global_cache.get(cache_key)

    if cached_result is not None:
        g.cache_status = 'hit'
        return cached_result

    g.cache_status = 'miss'
    transactions = data_store.get_transactions()

    result = {
        "success": True,
        "transactions": transactions,
        "total": len(transactions),
        "cached": False
    }

    global_cache.set(cache_key, result, ttl=60)
    return result

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    cache_key = 'dashboard_stats'
    cached_result = global_cache.get(cache_key)

    if cached_result is not None:
        g.cache_status = 'hit'
        return cached_result

    g.cache_status = 'miss'
    farms = data_store.get_farms()
    transactions = data_store.get_transactions()

    stats = {
        "total_farms": len(farms),
        "total_transactions": len(transactions),
        "avg_esg_score": sum(f['esg_score'] for f in farms) / len(farms) if farms else 0,
        "completed_transactions": len([t for t in transactions if t['status'] == 'completed']),
        "active_farms": len([f for f in farms if f.get('status') == 'active']),
        "system_performance": {
            "cache_hit_rate": global_cache.get_stats()['hit_rate'],
            "background_queue_size": 0  # 단순화
        }
    }

    result = {
        "success": True,
        "data": stats,
        "cached": False,
        "generated_at": datetime.now().isoformat()
    }

    global_cache.set(cache_key, result, ttl=30)
    return result

@app.route('/api/farms', methods=['POST'])
def create_farm():
    data = request.get_json()

    # 기본 농장 생성
    new_farm = data_store.add_farm({
        "name": data.get('name', 'Unknown Farm'),
        "location": data.get('location', 'Unknown'),
        "crop_type": data.get('crop_type', 'rice'),
        "area": data.get('area', 100),
        "status": "active",
        "created_at": datetime.now().isoformat()
    })

    # ESG 계산을 백그라운드에서 처리
    esg_future = process_esg_calculation(new_farm)

    # 관련 캐시 무효화
    global_cache.delete('get_farms')
    global_cache.delete('get_dashboard')

    return {
        "success": True,
        "data": new_farm,
        "message": "농장이 성공적으로 등록되었습니다",
        "esg_processing": "background",
        "request_id": g.request_id
    }, 201

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()

    new_transaction = data_store.add_transaction({
        "crop_type": data.get('crop_type', 'rice'),
        "quantity": data.get('quantity', 100),
        "price": data.get('price', 3.0),
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    })

    # 수요 예측을 백그라운드에서 처리
    prediction_future = process_demand_prediction(data)

    # 관련 캐시 무효화
    global_cache.delete('get_transactions')
    global_cache.delete('get_dashboard')

    return {
        "success": True,
        "data": new_transaction,
        "message": "거래가 성공적으로 생성되었습니다",
        "prediction_processing": "background",
        "request_id": g.request_id
    }, 201

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    stats = global_cache.get_stats()

    return {
        "cache_stats": stats,
        "server_info": {
            "version": "2.0.0-phase2",
            "background_workers": background_executor._max_workers,
            "active_threads": threading.active_count()
        }
    }

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    global_cache.clear()
    return {
        "success": True,
        "message": "캐시가 클리어되었습니다",
        "timestamp": datetime.now().isoformat()
    }

# 성능 테스트용 엔드포인트
@app.route('/api/stress-test', methods=['GET'])
def stress_test():
    """성능 테스트용 가벼운 엔드포인트"""
    return {
        "message": "OK",
        "timestamp": time.time(),
        "request_id": g.request_id
    }

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return {
        "success": False,
        "error": "Not Found",
        "message": "요청한 엔드포인트를 찾을 수 없습니다"
    }, 404

@app.errorhandler(500)
def internal_error(error):
    return {
        "success": False,
        "error": "Internal Server Error",
        "message": "서버 내부 오류가 발생했습니다"
    }, 500

if __name__ == '__main__':
    print("Phase 2 서버는 start_phase2.py로 실행하세요")
    print("python start_phase2.py")