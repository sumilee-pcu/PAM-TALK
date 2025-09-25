#!/usr/bin/env python3
"""
PAM-TALK 간단 성능 측정 스크립트
"""

import requests
import time
import threading
import statistics
import psutil
import json
from datetime import datetime


class SimpleBaselineTester:
    """간단한 기준 성능 측정기"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []

    def test_single_request(self, endpoint, timeout=30):
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
                'success': 200 <= response.status_code < 400
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

    def run_test(self):
        """기준 성능 테스트 실행"""
        print("PAM-TALK 기준 성능 측정")
        print("=" * 40)

        # 시스템 정보
        print(f"CPU 코어: {psutil.cpu_count()}개")
        print(f"총 메모리: {psutil.virtual_memory().total / 1024**3:.1f}GB")

        # 테스트 엔드포인트
        endpoints = [
            "/api/health",
            "/api/farms",
            "/api/transactions",
            "/api/dashboard"
        ]

        print(f"\n1. 단일 요청 테스트")
        single_results = []

        for endpoint in endpoints:
            result = self.test_single_request(endpoint)
            single_results.append(result)
            status = "OK" if result['success'] else "FAIL"
            print(f"   {endpoint}: {result['response_time']:.3f}s [{status}]")

        # 동시 요청 테스트
        print(f"\n2. 동시 요청 테스트")
        concurrent_levels = [5, 10, 20]

        for level in concurrent_levels:
            results, total_time = self.concurrent_test("/api/health", level)
            successful = [r for r in results if r['success']]

            avg_response = statistics.mean([r['response_time'] for r in successful]) if successful else 0
            success_rate = len(successful) / len(results) * 100
            rps = len(results) / total_time if total_time > 0 else 0

            print(f"   {level}개 동시요청:")
            print(f"     평균응답: {avg_response:.3f}s")
            print(f"     성공률: {success_rate:.1f}%")
            print(f"     RPS: {rps:.1f}")

        # 지속 부하 테스트
        print(f"\n3. 지속 부하 테스트 (20초)")
        duration = 20
        end_time = time.time() + duration
        sustained_results = []

        while time.time() < end_time:
            result = self.test_single_request("/api/health")
            sustained_results.append(result)
            time.sleep(0.5)  # 0.5초 간격

        successful_sustained = [r for r in sustained_results if r['success']]

        if successful_sustained:
            avg_sustained = statistics.mean([r['response_time'] for r in successful_sustained])
            sustained_success_rate = len(successful_sustained) / len(sustained_results) * 100
            sustained_rps = len(sustained_results) / duration

            print(f"   총 요청: {len(sustained_results)}개")
            print(f"   평균응답: {avg_sustained:.3f}s")
            print(f"   성공률: {sustained_success_rate:.1f}%")
            print(f"   평균 RPS: {sustained_rps:.1f}")

        # 최종 결과
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        print(f"\n시스템 상태:")
        print(f"   CPU 사용률: {cpu_usage:.1f}%")
        print(f"   메모리 사용률: {memory_usage:.1f}%")

        # 성능 평가
        print(f"\n성능 평가:")
        if sustained_rps >= 20:
            print("   상태: 양호 (20+ RPS)")
        elif sustained_rps >= 10:
            print("   상태: 보통 (10-19 RPS)")
        else:
            print("   상태: 개선필요 (<10 RPS)")

        target_rps = 50
        achievement = (sustained_rps / target_rps) * 100
        print(f"   목표대비: {achievement:.1f}% ({sustained_rps:.1f}/{target_rps} RPS)")

        # 결과 저장
        baseline_data = {
            'timestamp': datetime.now().isoformat(),
            'single_request_avg': statistics.mean([r['response_time'] for r in single_results if r['success']]),
            'sustained_rps': sustained_rps,
            'sustained_success_rate': sustained_success_rate,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'achievement_percent': achievement
        }

        with open('simple_baseline_results.json', 'w') as f:
            json.dump(baseline_data, f, indent=2)

        print(f"\n결과가 'simple_baseline_results.json'에 저장됨")
        return baseline_data


def main():
    # API 서버 연결 확인
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: API 서버가 응답하지 않음")
            print("해결: cd api && python app.py")
            return
        print("API 서버 연결 OK")
    except:
        print("ERROR: API 서버에 연결할 수 없음")
        print("해결: cd api && python app.py")
        return

    tester = SimpleBaselineTester()
    results = tester.run_test()

    print("\n" + "=" * 40)
    print("기준 성능 측정 완료!")

    return results


if __name__ == "__main__":
    main()