#!/usr/bin/env python3
"""
PAM-TALK 기준 성능 측정 스크립트
현재 시스템의 기본 성능을 측정하여 최적화 전후 비교용 기준점을 제공
"""

import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import os
from datetime import datetime
from typing import List, Dict


class BaselineTester:
    """기준 성능 측정기"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.system_stats = {}

    async def test_single_request(self, session, endpoint, method="GET"):
        """단일 요청 성능 측정"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with session.request(method, url) as response:
                await response.text()
                end_time = time.time()
                return {
                    'endpoint': endpoint,
                    'response_time': end_time - start_time,
                    'status_code': response.status,
                    'success': 200 <= response.status < 400
                }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'response_time': time.time() - start_time,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }

    def get_system_stats(self):
        """시스템 리소스 사용량 측정"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_mb': memory.used / 1024 / 1024,
            'disk_percent': disk.percent,
            'python_process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024
        }

    async def run_baseline_test(self):
        """기준 성능 테스트 실행"""
        print("PAM-TALK 기준 성능 측정 시작")
        print("=" * 50)

        # 시스템 정보
        print(f"시스템 정보:")
        print(f"   CPU 코어: {psutil.cpu_count()} 개")
        print(f"   총 메모리: {psutil.virtual_memory().total / 1024**3:.1f} GB")
        print(f"   Python 버전: {os.sys.version.split()[0]}")

        start_stats = self.get_system_stats()
        print(f"   시작 CPU 사용률: {start_stats['cpu_percent']}%")
        print(f"   시작 메모리 사용률: {start_stats['memory_percent']}%")

        # 테스트 엔드포인트들
        test_endpoints = [
            "/api/health",
            "/api/farms",
            "/api/transactions",
            "/api/dashboard",
            "/api/scenarios"
        ]

        print(f"\n🧪 테스트 엔드포인트: {len(test_endpoints)}개")
        for endpoint in test_endpoints:
            print(f"   - {endpoint}")

        # 단일 요청 성능 테스트
        print(f"\n📏 1. 단일 요청 성능 측정")
        connector = aiohttp.TCPConnector(limit=1)
        async with aiohttp.ClientSession(connector=connector) as session:
            for endpoint in test_endpoints:
                result = await self.test_single_request(session, endpoint)
                self.results.append(result)
                status = "✅" if result['success'] else "❌"
                print(f"   {status} {endpoint}: {result['response_time']:.3f}초")

        # 동시 요청 성능 테스트
        print(f"\n🔄 2. 동시 요청 성능 측정")
        concurrent_levels = [1, 5, 10, 20]

        for level in concurrent_levels:
            print(f"\n   📈 동시 요청 {level}개:")

            start_time = time.time()
            connector = aiohttp.TCPConnector(limit=level * 2)

            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for i in range(level):
                    endpoint = test_endpoints[i % len(test_endpoints)]
                    task = self.test_single_request(session, endpoint)
                    tasks.append(task)

                concurrent_results = await asyncio.gather(*tasks)

                end_time = time.time()
                total_time = end_time - start_time

                successful = [r for r in concurrent_results if r['success']]
                avg_response_time = statistics.mean([r['response_time'] for r in successful]) if successful else 0
                success_rate = len(successful) / len(concurrent_results) * 100
                rps = len(concurrent_results) / total_time if total_time > 0 else 0

                print(f"      ⏱️  총 처리시간: {total_time:.3f}초")
                print(f"      📊 평균 응답시간: {avg_response_time:.3f}초")
                print(f"      ✅ 성공률: {success_rate:.1f}%")
                print(f"      🚀 RPS (초당 요청): {rps:.1f}")

                # 시스템 리소스 확인
                current_stats = self.get_system_stats()
                print(f"      💻 CPU 사용률: {current_stats['cpu_percent']:.1f}%")
                print(f"      🧠 메모리 사용률: {current_stats['memory_percent']:.1f}%")

        # 지속 부하 테스트
        print(f"\n⏰ 3. 지속 부하 테스트 (30초)")

        duration = 30  # 30초
        concurrent_users = 10

        end_time = time.time() + duration
        sustained_results = []

        print(f"   👥 동시 사용자 {concurrent_users}명으로 {duration}초간 테스트...")

        connector = aiohttp.TCPConnector(limit=concurrent_users * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            while time.time() < end_time:
                tasks = []
                for i in range(concurrent_users):
                    endpoint = test_endpoints[i % len(test_endpoints)]
                    task = self.test_single_request(session, endpoint)
                    tasks.append(task)

                batch_results = await asyncio.gather(*tasks)
                sustained_results.extend(batch_results)

                await asyncio.sleep(1)  # 1초 간격

        # 지속 테스트 결과 분석
        successful_sustained = [r for r in sustained_results if r['success']]

        if successful_sustained:
            avg_sustained_response = statistics.mean([r['response_time'] for r in successful_sustained])
            max_sustained_response = max([r['response_time'] for r in successful_sustained])
            min_sustained_response = min([r['response_time'] for r in successful_sustained])
            sustained_success_rate = len(successful_sustained) / len(sustained_results) * 100
            sustained_rps = len(sustained_results) / duration

            print(f"   📊 지속 테스트 결과:")
            print(f"      총 요청: {len(sustained_results)}개")
            print(f"      평균 응답시간: {avg_sustained_response:.3f}초")
            print(f"      최소/최대 응답시간: {min_sustained_response:.3f}초 / {max_sustained_response:.3f}초")
            print(f"      성공률: {sustained_success_rate:.1f}%")
            print(f"      평균 RPS: {sustained_rps:.1f}")

        # 최종 시스템 상태
        final_stats = self.get_system_stats()
        print(f"\n💻 최종 시스템 상태:")
        print(f"   CPU 사용률: {final_stats['cpu_percent']:.1f}%")
        print(f"   메모리 사용률: {final_stats['memory_percent']:.1f}%")
        print(f"   Python 프로세스 메모리: {final_stats['python_process_memory_mb']:.1f} MB")

        return {
            'single_request': {
                'avg_response_time': statistics.mean([r['response_time'] for r in self.results if r['success']]),
                'success_rate': len([r for r in self.results if r['success']]) / len(self.results) * 100
            },
            'concurrent': {
                'max_tested': max(concurrent_levels),
                'recommended_limit': 10  # 현재 시스템 추정 한계
            },
            'sustained': {
                'duration': duration,
                'avg_rps': sustained_rps if 'sustained_rps' in locals() else 0,
                'success_rate': sustained_success_rate if 'sustained_success_rate' in locals() else 0
            },
            'system': final_stats
        }


async def main():
    """메인 실행 함수"""
    print("🚀 PAM-TALK 기준 성능 측정 도구")
    print("=" * 50)

    # API 서버 연결 확인
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API 서버가 응답하지 않습니다.")
            print("   다음 명령으로 서버를 시작해주세요:")
            print("   cd api && python app.py")
            return
        print("✅ API 서버 연결 확인")
    except:
        print("❌ API 서버에 연결할 수 없습니다.")
        print("   다음 명령으로 서버를 시작해주세요:")
        print("   cd api && python app.py")
        return

    tester = BaselineTester()
    results = await tester.run_baseline_test()

    print("\n" + "=" * 50)
    print("📋 기준 성능 측정 완료!")
    print("=" * 50)

    print(f"🎯 주요 지표:")
    print(f"   단일 요청 평균 응답시간: {results['single_request']['avg_response_time']:.3f}초")
    print(f"   단일 요청 성공률: {results['single_request']['success_rate']:.1f}%")
    print(f"   지속 평균 RPS: {results['sustained']['avg_rps']:.1f}")
    print(f"   지속 테스트 성공률: {results['sustained']['success_rate']:.1f}%")

    print(f"\n💡 현재 성능 평가:")
    avg_rps = results['sustained']['avg_rps']
    if avg_rps >= 50:
        print(f"   🟢 우수 (50+ RPS)")
    elif avg_rps >= 20:
        print(f"   🟡 양호 (20-49 RPS)")
    elif avg_rps >= 10:
        print(f"   🟠 보통 (10-19 RPS)")
    else:
        print(f"   🔴 개선 필요 (<10 RPS)")

    print(f"\n🎯 목표 대비 현황:")
    target_rps = 50  # Phase 1 목표
    achievement = (avg_rps / target_rps) * 100
    print(f"   현재 RPS: {avg_rps:.1f} / 목표: {target_rps}")
    print(f"   달성률: {achievement:.1f}%")

    if achievement < 50:
        print(f"   📈 권장사항: 최적화가 시급합니다 (Gunicorn + 캐싱)")
    elif achievement < 80:
        print(f"   📈 권장사항: 추가 최적화 권장 (Redis + 비동기 처리)")
    else:
        print(f"   ✅ 현재 성능이 목표에 근접합니다!")

    # 기준점 데이터 저장
    baseline_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'recommendations': [
            "Gunicorn 멀티프로세서 도입",
            "Redis 캐싱 레이어 추가",
            "비동기 요청 처리 구현",
            "데이터베이스 연결 풀링"
        ]
    }

    with open('baseline_results.json', 'w', encoding='utf-8') as f:
        json.dump(baseline_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 결과가 'baseline_results.json'에 저장되었습니다.")
    print(f"🔧 다음 단계: 최적화 구현 후 성능 비교 테스트")


if __name__ == "__main__":
    asyncio.run(main())