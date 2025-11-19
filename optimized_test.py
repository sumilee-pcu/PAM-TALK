#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 최적화 성능 테스트
기존 서버 vs 최적화 서버 성능 비교
"""

import requests
import time
import threading
import statistics
import json
from datetime import datetime


class OptimizedTester:
    """최적화 서버 성능 테스트"""

    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = []

    def test_single_request(self, endpoint, timeout=10):
        """단일 요청 성능 측정"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 400,
                'cached': 'cached' in response.text.lower()
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'response_time': time.time() - start_time,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }

    def concurrent_test(self, endpoint, num_requests):
        """동시 요청 테스트"""
        results = []
        threads = []

        def worker():
            result = self.test_single_request(endpoint)
            results.append(result)

        start_time = time.time()

        for _ in range(num_requests):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()

        return results, end_time - start_time

    def cache_test(self):
        """캐싱 효과 테스트"""
        print("  캐시 효과 테스트:")

        # 첫 번째 요청 (캐시 미스)
        result1 = self.test_single_request("/api/farms")
        print(f"    첫 요청 (캐시 미스): {result1['response_time']:.3f}s")

        # 두 번째 요청 (캐시 히트)
        result2 = self.test_single_request("/api/farms")
        print(f"    둘째 요청 (캐시 히트): {result2['response_time']:.3f}s")

        improvement = (result1['response_time'] - result2['response_time']) / result1['response_time'] * 100
        print(f"    캐시 개선율: {improvement:.1f}%")

        return result1, result2

    def run_optimized_test(self):
        """최적화 성능 테스트 실행"""
        print("PAM-TALK 최적화 성능 테스트")
        print("=" * 40)

        # 기본 연결 확인
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code != 200:
                print("ERROR: 최적화 서버 연결 실패")
                return None
            print("최적화 서버 연결 OK")
            print(f"서버 버전: {response.json().get('version', 'Unknown')}")
            print(f"캐시 상태: {response.json().get('cache_status', 'Unknown')}")
        except Exception as e:
            print(f"ERROR: {e}")
            return None

        # 1. 단일 요청 테스트
        print(f"\n1. 단일 요청 성능")
        endpoints = ["/api/health", "/api/farms", "/api/transactions", "/api/dashboard"]
        single_results = []

        for endpoint in endpoints:
            result = self.test_single_request(endpoint)
            single_results.append(result)
            status = "OK" if result['success'] else "FAIL"
            cached = " [CACHED]" if result.get('cached', False) else ""
            print(f"   {endpoint}: {result['response_time']:.3f}s [{status}]{cached}")

        # 2. 캐시 효과 테스트
        print(f"\n2. 캐싱 시스템 효과")
        cache_result1, cache_result2 = self.cache_test()

        # 3. 동시 요청 테스트
        print(f"\n3. 동시 요청 성능")
        concurrent_levels = [10, 20, 50, 100]

        best_rps = 0
        for level in concurrent_levels:
            results, total_time = self.concurrent_test("/api/health", level)
            successful = [r for r in results if r['success']]

            if successful:
                avg_response = statistics.mean([r['response_time'] for r in successful])
                success_rate = len(successful) / len(results) * 100
                rps = len(results) / total_time if total_time > 0 else 0

                print(f"   {level}개 동시요청:")
                print(f"     평균응답: {avg_response:.3f}s")
                print(f"     성공률: {success_rate:.1f}%")
                print(f"     RPS: {rps:.1f}")

                if success_rate > 95:  # 95% 이상 성공시에만 기록
                    best_rps = max(best_rps, rps)

        # 4. 지속 부하 테스트
        print(f"\n4. 지속 부하 테스트 (30초)")
        duration = 30
        end_time = time.time() + duration
        sustained_results = []

        while time.time() < end_time:
            result = self.test_single_request("/api/health")
            sustained_results.append(result)
            time.sleep(0.1)  # 0.1초 간격으로 증가

        successful_sustained = [r for r in sustained_results if r['success']]

        if successful_sustained:
            avg_sustained = statistics.mean([r['response_time'] for r in successful_sustained])
            sustained_success_rate = len(successful_sustained) / len(sustained_results) * 100
            sustained_rps = len(sustained_results) / duration

            print(f"   총 요청: {len(sustained_results)}개")
            print(f"   평균응답: {avg_sustained:.3f}s")
            print(f"   성공률: {sustained_success_rate:.1f}%")
            print(f"   지속 RPS: {sustained_rps:.1f}")

        # 5. 성능 평가
        print(f"\n최적화 성능 평가:")

        single_avg = statistics.mean([r['response_time'] for r in single_results if r['success']])
        print(f"  평균 응답시간: {single_avg:.3f}s")
        print(f"  최대 동시 RPS: {best_rps:.1f}")
        print(f"  지속 평균 RPS: {sustained_rps:.1f}")

        # Phase 1 목표 달성도
        target_rps = 50
        achievement = (sustained_rps / target_rps) * 100
        print(f"  Phase 1 목표 달성: {achievement:.1f}% ({sustained_rps:.1f}/{target_rps} RPS)")

        if achievement >= 80:
            print("  상태: 목표 달성 (Phase 1 완료)")
        elif achievement >= 50:
            print("  상태: 목표 근접 (추가 최적화 권장)")
        else:
            print("  상태: 추가 최적화 필요")

        # 결과 반환
        return {
            'single_avg_response': single_avg,
            'best_concurrent_rps': best_rps,
            'sustained_rps': sustained_rps,
            'sustained_success_rate': sustained_success_rate,
            'achievement_percent': achievement,
            'cache_improvement': (cache_result1['response_time'] - cache_result2['response_time']) / cache_result1['response_time'] * 100
        }


def compare_with_baseline():
    """기존 기준점과 비교"""
    print("\n" + "=" * 50)
    print("기준점 vs 최적화 성능 비교")
    print("=" * 50)

    # 기준점 데이터 로드
    try:
        with open('simple_baseline_results.json', 'r') as f:
            baseline = json.load(f)
    except FileNotFoundError:
        print("기준점 데이터가 없습니다. 먼저 baseline 테스트를 실행하세요.")
        return

    # 최적화 테스트 실행
    tester = OptimizedTester()
    optimized = tester.run_optimized_test()

    if not optimized:
        return

    print(f"\n성능 비교 결과:")
    print(f"{'항목':<15} {'기존':<10} {'최적화':<10} {'개선도':<10}")
    print("-" * 50)

    # RPS 비교
    baseline_rps = baseline.get('sustained_rps', 0)
    optimized_rps = optimized['sustained_rps']
    rps_improvement = (optimized_rps - baseline_rps) / baseline_rps * 100 if baseline_rps > 0 else float('inf')
    print(f"{'RPS':<15} {baseline_rps:<10.1f} {optimized_rps:<10.1f} {rps_improvement:<9.1f}%")

    # 응답시간 비교
    baseline_response = baseline.get('single_request_avg', 0)
    optimized_response = optimized['single_avg_response']
    response_improvement = (baseline_response - optimized_response) / baseline_response * 100 if baseline_response > 0 else 0
    print(f"{'응답시간(s)':<15} {baseline_response:<10.3f} {optimized_response:<10.3f} {response_improvement:<9.1f}%")

    # 목표 달성도 비교
    baseline_achievement = baseline.get('achievement_percent', 0)
    optimized_achievement = optimized['achievement_percent']
    print(f"{'목표달성%':<15} {baseline_achievement:<10.1f} {optimized_achievement:<10.1f} +{optimized_achievement-baseline_achievement:<8.1f}%")

    # 전체 평가
    print(f"\n종합 평가:")
    if optimized_rps > baseline_rps * 5:
        print("  🟢 우수한 성능 개선 (5배 이상)")
    elif optimized_rps > baseline_rps * 2:
        print("  🟡 양호한 성능 개선 (2-5배)")
    elif optimized_rps > baseline_rps:
        print("  🟠 보통 성능 개선 (향상됨)")
    else:
        print("  🔴 성능 개선 효과 없음")

    # 결과 저장
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'baseline': baseline,
        'optimized': optimized,
        'improvements': {
            'rps_improvement_percent': rps_improvement,
            'response_improvement_percent': response_improvement,
            'achievement_improvement': optimized_achievement - baseline_achievement
        }
    }

    with open('optimization_comparison.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print(f"\n비교 결과가 'optimization_comparison.json'에 저장됨")


if __name__ == "__main__":
    compare_with_baseline()