#!/usr/bin/env python3
"""
PAM-TALK 고급 캐싱 시스템
Redis 대신 고성능 메모리 캐시 구현
"""

import time
import threading
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class AdvancedCache:
    """고성능 메모리 캐시 시스템"""

    def __init__(self, max_size: int = 10000, cleanup_interval: int = 300):
        self.cache: Dict[str, tuple] = {}  # {key: (value, expire_time, access_count, last_access)}
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_sets': 0
        }
        self.lock = threading.RLock()

        # 백그라운드 정리 스레드 시작
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """백그라운드 캐시 정리 스레드"""
        def cleanup():
            while True:
                time.sleep(self.cleanup_interval)
                self._cleanup_expired()
                self._evict_if_full()

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _generate_key(self, key: str, **kwargs) -> str:
        """키 생성 최적화"""
        if kwargs:
            key_data = f"{key}:{json.dumps(kwargs, sort_keys=True)}"
            return hashlib.md5(key_data.encode()).hexdigest()
        return key

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """캐시에서 값 조회"""
        cache_key = self._generate_key(key, **kwargs)

        with self.lock:
            if cache_key in self.cache:
                value, expire_time, access_count, _ = self.cache[cache_key]

                if time.time() < expire_time:
                    # 히트 - 접근 통계 업데이트
                    self.cache[cache_key] = (value, expire_time, access_count + 1, time.time())
                    self.stats['hits'] += 1
                    return value
                else:
                    # 만료된 키 삭제
                    del self.cache[cache_key]

            self.stats['misses'] += 1
            return None

    def set(self, key: str, value: Any, ttl: int = 300, **kwargs):
        """캐시에 값 저장"""
        cache_key = self._generate_key(key, **kwargs)
        expire_time = time.time() + ttl

        with self.lock:
            # 캐시 크기 확인 후 필요시 정리
            if len(self.cache) >= self.max_size:
                self._evict_lru()

            self.cache[cache_key] = (value, expire_time, 1, time.time())
            self.stats['total_sets'] += 1

    def delete(self, key: str, **kwargs):
        """캐시에서 키 삭제"""
        cache_key = self._generate_key(key, **kwargs)

        with self.lock:
            if cache_key in self.cache:
                del self.cache[cache_key]

    def clear(self):
        """전체 캐시 클리어"""
        with self.lock:
            self.cache.clear()

    def _cleanup_expired(self):
        """만료된 키들 정리"""
        current_time = time.time()
        expired_keys = []

        with self.lock:
            for key, (_, expire_time, _, _) in self.cache.items():
                if current_time >= expire_time:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

    def _evict_lru(self):
        """LRU 방식으로 캐시 정리"""
        if not self.cache:
            return

        with self.lock:
            # 가장 오래된 접근 시간을 가진 키 찾기
            oldest_key = min(self.cache.keys(),
                           key=lambda k: self.cache[k][3])  # last_access 기준

            del self.cache[oldest_key]
            self.stats['evictions'] += 1

    def _evict_if_full(self):
        """캐시가 가득 찬 경우 정리"""
        while len(self.cache) > self.max_size * 0.8:  # 80% 수준까지 정리
            self._evict_lru()

    def get_stats(self) -> Dict:
        """캐시 통계 반환"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self.stats['evictions'],
                'total_sets': self.stats['total_sets']
            }


# 고성능 캐시 데코레이터
def advanced_cache(ttl: int = 300, cache_instance: AdvancedCache = None):
    """고급 캐시 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 캐시 인스턴스
            cache = cache_instance or getattr(wrapper, '_cache', None)
            if cache is None:
                cache = AdvancedCache()
                wrapper._cache = cache

            # 캐시 키 생성
            func_key = f"{func.__name__}"

            # 캐시에서 확인
            cached_result = cache.get(func_key, args=args, kwargs=kwargs)
            if cached_result is not None:
                return cached_result

            # 함수 실행
            result = func(*args, **kwargs)

            # 캐시에 저장
            cache.set(func_key, result, ttl, args=args, kwargs=kwargs)

            return result

        return wrapper
    return decorator


# 전역 캐시 인스턴스
global_cache = AdvancedCache(max_size=50000, cleanup_interval=60)


if __name__ == "__main__":
    # 캐시 테스트
    cache = AdvancedCache(max_size=1000)

    # 테스트 데이터 저장
    for i in range(100):
        cache.set(f"test_{i}", f"value_{i}", ttl=60)

    # 테스트 데이터 조회
    hits = 0
    for i in range(150):  # 일부는 존재하지 않음
        result = cache.get(f"test_{i}")
        if result:
            hits += 1

    print("Advanced Cache Test Results:")
    print(f"Cache Stats: {cache.get_stats()}")
    print(f"Test Hits: {hits}/150")