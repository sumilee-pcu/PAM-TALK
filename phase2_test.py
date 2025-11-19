#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Phase 2 성능 테스트
Waitress + 고급 캐싱 vs 기존 시스템 성능 비교
"""

import requests
import time
import threading
import statistics
import json
from datetime import datetime


class Phase2Tester:
    """Phase 2 성능 테스트"""

    def __init__(self, base_url="http://localhost:5002"):
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
                'server_version': response.json().get('version', 'Unknown') if response.headers.get('content-type', '').startswith('application/json') else 'Unknown',
                'cache_status': response.headers.get('X-Cache-Status', 'unknown')
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

    def stress_test(self, duration=30):
        """지속 스트레스 테스트"""
        end_time = time.time() + duration
        results = []

        while time.time() < end_time:
            result = self.test_single_request("/api/stress-test")
            results.append(result)
            time.sleep(0.05)  # 0.05초 간격 (초당 20회)

        return results

    def cache_effectiveness_test(self):
        """캐싱 효과 테스트"""
        print("  캐시 효과 분석:")

        # 캐시 클리어
        try:
            requests.post(f"{self.base_url}/api/cache/clear")
            print("    캐시 초기화 완료")
        except:
            pass

        # 첫 번째 요청들 (캐시 미스)
        endpoints = ["/api/farms", "/api/transactions", "/api/dashboard"]
        first_times = []

        for endpoint in endpoints:
            result = self.test_single_request(endpoint)
            first_times.append(result['response_time'])
            print(f"    {endpoint} 첫 요청: {result['response_time']:.3f}s [{result.get('cache_status', 'unknown')}]")

        time.sleep(0.5)  # 잠시 대기

        # 두 번째 요청들 (캐시 히트)
        second_times = []
        for endpoint in endpoints:
            result = self.test_single_request(endpoint)
            second_times.append(result['response_time'])
            print(f"    {endpoint} 둘 요청: {result['response_time']:.3f}s [{result.get('cache_status', 'unknown')}]")

        # 개선율 계산
        avg_first = statistics.mean(first_times)
        avg_second = statistics.mean(second_times)
        improvement = (avg_first - avg_second) / avg_first * 100 if avg_first > 0 else 0

        print(f"    평균 개선율: {improvement:.1f}%")
        return improvement

    def run_phase2_test(self):
        """Phase 2 종합 성능 테스트"""
        print("PAM-TALK Phase 2 성능 테스트")
        print("=" * 50)

        # 연결 확인
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code != 200:
                print("ERROR: Phase 2 서버 연결 실패")
                return None

            health_data = response.json()
            print("Phase 2 서버 연결 OK")
            print(f"서버 버전: {health_data.get('version', 'Unknown')}")
            print(f"서버 타입: {health_data.get('server_type', 'Unknown')}")
            print(f"백그라운드 워커: {health_data.get('background_workers', 0)}개")

        except Exception as e:
            print(f"ERROR: {e}")
            return None

        # 1. 단일 요청 성능
        print(f"\n1. 단일 요청 성능 (Waitress 서버)")
        endpoints = ["/api/health", "/api/farms", "/api/transactions", "/api/dashboard"]
        single_results = []

        for endpoint in endpoints:
            result = self.test_single_request(endpoint)
            single_results.append(result)
            status = "OK" if result['success'] else "FAIL"
            cache = f" [{result.get('cache_status', 'unknown')}]"
            print(f"   {endpoint}: {result['response_time']:.3f}s [{status}]{cache}")

        # 2. 캐싱 효과
        print(f"\n2. 고급 캐싱 시스템 효과")
        cache_improvement = self.cache_effectiveness_test()

        # 3. 동시 요청 성능 (대폭 증가)
        print(f"\n3. 동시 요청 성능 (Waitress + 멀티스레드)")
        concurrent_levels = [50, 100, 200, 500]  # 더 높은 동시 요청 수

        best_rps = 0
        for level in concurrent_levels:
            results, total_time = self.concurrent_test("/api/stress-test", level)
            successful = [r for r in results if r['success']]

            if successful:
                avg_response = statistics.mean([r['response_time'] for r in successful])
                success_rate = len(successful) / len(results) * 100
                rps = len(results) / total_time if total_time > 0 else 0

                print(f"   {level}개 동시요청:")
                print(f"     평균응답: {avg_response:.3f}s")
                print(f"     성공률: {success_rate:.1f}%")
                print(f"     RPS: {rps:.1f}")

                if success_rate > 90:  # 90% 이상 성공시에만 기록
                    best_rps = max(best_rps, rps)

                if success_rate < 50:  # 성공률 50% 미만이면 중단
                    print(f"     성공률 저조로 테스트 중단")
                    break

        # 4. 지속 스트레스 테스트
        print(f"\n4. 지속 스트레스 테스트 (30초, 고강도)")
        sustained_results = self.stress_test(duration=30)

        successful_sustained = [r for r in sustained_results if r['success']]

        if successful_sustained:
            avg_sustained = statistics.mean([r['response_time'] for r in successful_sustained])
            sustained_success_rate = len(successful_sustained) / len(sustained_results) * 100
            sustained_rps = len(sustained_results) / 30  # 30초 테스트

            print(f"   총 요청: {len(sustained_results)}개")
            print(f"   평균응답: {avg_sustained:.3f}s")
            print(f"   성공률: {sustained_success_rate:.1f}%")
            print(f"   지속 RPS: {sustained_rps:.1f}")

        # 5. 캐시 통계 확인
        try:
            cache_stats = requests.get(f"{self.base_url}/api/cache/stats").json()
            print(f"\n5. 캐시 시스템 통계")
            stats = cache_stats.get('cache_stats', {})
            print(f"   캐시 항목 수: {stats.get('size', 0)}")
            print(f"   히트율: {stats.get('hit_rate', 0):.1f}%")
            print(f"   총 히트: {stats.get('hits', 0)}")
            print(f"   총 미스: {stats.get('misses', 0)}")
        except:
            print(f"   캐시 통계 조회 실패")

        # 성능 평가
        print(f"\nPhase 2 성능 평가:")
        single_avg = statistics.mean([r['response_time'] for r in single_results if r['success']])

        print(f"  평균 응답시간: {single_avg:.3f}s")
        print(f"  최고 동시 RPS: {best_rps:.1f}")
        print(f"  지속 평균 RPS: {sustained_rps:.1f}")
        print(f"  캐시 개선율: {cache_improvement:.1f}%")

        # Phase 2 목표 달성도
        target_rps = 50
        achievement = (sustained_rps / target_rps) * 100
        print(f"  Phase 2 목표 달성: {achievement:.1f}% ({sustained_rps:.1f}/{target_rps} RPS)")

        if achievement >= 100:
            print("  상태: 목표 초과 달성! (Phase 2 성공)")
        elif achievement >= 80:
            print("  상태: 목표 달성 (Phase 2 완료)")
        elif achievement >= 50:
            print("  상태: 목표 근접 (추가 최적화 권장)")
        else:
            print("  상태: 추가 최적화 필요")

        return {
            'single_avg_response': single_avg,
            'best_concurrent_rps': best_rps,
            'sustained_rps': sustained_rps,
            'sustained_success_rate': sustained_success_rate,
            'achievement_percent': achievement,
            'cache_improvement': cache_improvement,
            'server_type': 'waitress-phase2'
        }


def compare_all_phases():
    """모든 단계 성능 비교"""
    print("\n" + "=" * 60)
    print("전체 성능 향상 비교 (기준점 → Phase 1 → Phase 2)")
    print("=" * 60)

    # Phase 2 테스트 실행
    tester = Phase2Tester()
    phase2_result = tester.run_phase2_test()

    if not phase2_result:
        return

    # 기존 결과들 로드
    try:
        with open('simple_baseline_results.json', 'r') as f:
            baseline = json.load(f)
    except FileNotFoundError:
        print("기준점 데이터 없음")
        baseline = {'sustained_rps': 0.4, 'single_request_avg': 2.7}

    try:
        with open('optimization_comparison.json', 'r') as f:
            phase1_data = json.load(f)
            phase1 = phase1_data.get('optimized', {})
    except FileNotFoundError:
        print("Phase 1 데이터 없음")
        phase1 = {'sustained_rps': 0.5, 'single_avg_response': 2.0}

    print(f"\n최종 성능 비교:")
    print(f"{'단계':<15} {'RPS':<10} {'응답시간(s)':<12} {'개선도':<10}")
    print("-" * 50)

    baseline_rps = baseline.get('sustained_rps', 0.4)
    baseline_response = baseline.get('single_request_avg', 2.7)

    phase1_rps = phase1.get('sustained_rps', 0.5)
    phase1_response = phase1.get('single_avg_response', 2.0)

    phase2_rps = phase2_result['sustained_rps']
    phase2_response = phase2_result['single_avg_response']

    print(f"{'기준점':<15} {baseline_rps:<10.1f} {baseline_response:<12.3f} {'0%':<10}")

    phase1_improvement = (phase1_rps - baseline_rps) / baseline_rps * 100 if baseline_rps > 0 else 0
    print(f"{'Phase 1':<15} {phase1_rps:<10.1f} {phase1_response:<12.3f} {phase1_improvement:<9.1f}%")

    phase2_improvement = (phase2_rps - baseline_rps) / baseline_rps * 100 if baseline_rps > 0 else 0
    print(f"{'Phase 2':<15} {phase2_rps:<10.1f} {phase2_response:<12.3f} {phase2_improvement:<9.1f}%")

    # 최종 평가
    print(f"\n최종 평가:")
    if phase2_rps >= 50:
        print("  🟢 Phase 2 목표 달성! (50+ RPS)")
        print("  🎯 MAU 10만명 처리 가능한 기반 완성")
    elif phase2_rps >= 20:
        print("  🟡 Phase 2 부분 달성 (20+ RPS)")
        print("  📈 Phase 3 최적화로 목표 달성 가능")
    else:
        print("  🔴 추가 최적화 필요")

    # 결과 저장
    final_comparison = {
        'timestamp': datetime.now().isoformat(),
        'baseline': baseline,
        'phase1': phase1,
        'phase2': phase2_result,
        'improvements': {
            'phase1_vs_baseline': phase1_improvement,
            'phase2_vs_baseline': phase2_improvement,
            'phase2_vs_phase1': (phase2_rps - phase1_rps) / phase1_rps * 100 if phase1_rps > 0 else 0
        }
    }

    with open('final_performance_comparison.json', 'w') as f:
        json.dump(final_comparison, f, indent=2)

    print(f"\n전체 비교 결과가 'final_performance_comparison.json'에 저장됨")


if __name__ == "__main__":
    compare_all_phases()