#!/usr/bin/env python3
"""
PAM-TALK 성능 및 부하 테스트 시스템
MAU 10만명, DAU 3만명 규모 검증을 위한 종합 테스트
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error_message: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LoadTestConfig:
    """부하 테스트 설정"""
    base_url: str = "http://localhost:5000"
    concurrent_users: int = 100
    test_duration: int = 60  # seconds
    ramp_up_time: int = 10   # seconds
    target_rps: int = 50     # requests per second
    timeout: int = 30        # seconds


class PAMTalkLoadTester:
    """PAM-TALK 부하 테스트 실행기"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'p95_response_time': 0,
            'p99_response_time': 0,
            'requests_per_second': 0,
            'error_rate': 0
        }
        self.test_data = self._generate_test_data()

    def _generate_test_data(self) -> Dict[str, List[Dict]]:
        """테스트용 데이터 생성"""
        farms_data = []
        for i in range(1000):  # 1000개 농장 데이터
            farms_data.append({
                "name": f"테스트농장_{i:04d}",
                "location": random.choice(["경기도", "충청도", "전라도", "경상도"]),
                "crop_type": random.choice(["rice", "wheat", "corn", "soybean"]),
                "area": round(random.uniform(10, 500), 2),
                "organic_certified": random.choice([True, False]),
                "sustainability_practices": [
                    "물 절약 시스템",
                    "태양광 에너지 활용",
                    "친환경 농약 사용"
                ]
            })

        transactions_data = []
        for i in range(5000):  # 5000개 거래 데이터
            transactions_data.append({
                "crop_type": random.choice(["rice", "wheat", "corn", "soybean"]),
                "quantity": random.randint(100, 2000),
                "price_per_kg": round(random.uniform(2.0, 5.0), 2),
                "delivery_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "quality_requirements": {
                    "organic": random.choice([True, False]),
                    "moisture_content": f"<{random.randint(12, 16)}%"
                }
            })

        predictions_data = []
        for crop in ["rice", "wheat", "corn", "soybean"]:
            predictions_data.append({
                "crop_type": crop,
                "prediction_period": random.randint(7, 90),
                "include_weather": random.choice([True, False]),
                "historical_period": random.randint(180, 365)
            })

        return {
            "farms": farms_data,
            "transactions": transactions_data,
            "predictions": predictions_data
        }

    async def _make_request(self, session: aiohttp.ClientSession,
                           endpoint: str, method: str = "GET",
                           data: Dict = None) -> TestResult:
        """비동기 HTTP 요청 실행"""
        url = f"{self.config.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                await response.text()  # 응답 본문 읽기
                response_time = time.time() - start_time

                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=response.status,
                    success=200 <= response.status < 400
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                success=False,
                error_message=str(e)
            )

    def _get_random_test_scenario(self) -> tuple:
        """랜덤 테스트 시나리오 선택"""
        scenarios = [
            # 읽기 작업 (70%)
            ("/api/health", "GET", None),
            ("/api/farms", "GET", None),
            ("/api/transactions", "GET", None),
            ("/api/dashboard", "GET", None),
            ("/api/scenarios", "GET", None),

            # 쓰기 작업 (20%)
            ("/api/farms", "POST", random.choice(self.test_data["farms"])),
            ("/api/transactions", "POST", random.choice(self.test_data["transactions"])),

            # AI 예측 작업 (10% - 리소스 집약적)
            ("/api/transactions/check", "POST", random.choice(self.test_data["transactions"])),
        ]

        # 가중치 적용 선택
        weights = [10, 10, 10, 10, 10, 5, 5, 2]  # 읽기가 더 빈번
        return random.choices(scenarios, weights=weights)[0]

    async def _run_user_session(self, session: aiohttp.ClientSession,
                               user_id: int, duration: int):
        """개별 사용자 세션 시뮬레이션"""
        end_time = time.time() + duration
        requests_made = 0

        while time.time() < end_time:
            endpoint, method, data = self._get_random_test_scenario()
            result = await self._make_request(session, endpoint, method, data)
            self.results.append(result)
            requests_made += 1

            # 사용자별 요청 간격 (실제 사용자 행동 시뮬레이션)
            await asyncio.sleep(random.uniform(1, 5))

        print(f"사용자 {user_id}: {requests_made}개 요청 완료")

    async def run_load_test(self):
        """메인 부하 테스트 실행"""
        print(f"🚀 부하 테스트 시작")
        print(f"   대상: {self.config.base_url}")
        print(f"   동시 사용자: {self.config.concurrent_users}")
        print(f"   테스트 시간: {self.config.test_duration}초")
        print(f"   목표 RPS: {self.config.target_rps}")
        print("-" * 50)

        connector = aiohttp.TCPConnector(limit=self.config.concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:

            # 점진적 사용자 증가 (Ramp-up)
            tasks = []
            users_per_step = max(1, self.config.concurrent_users // 10)

            for step in range(0, self.config.concurrent_users, users_per_step):
                step_users = min(users_per_step, self.config.concurrent_users - step)

                for user_id in range(step, step + step_users):
                    task = asyncio.create_task(
                        self._run_user_session(session, user_id, self.config.test_duration)
                    )
                    tasks.append(task)

                if step < self.config.concurrent_users - users_per_step:
                    await asyncio.sleep(self.config.ramp_up_time / 10)
                    print(f"📈 사용자 {step + step_users}명 활성화...")

            print(f"⚡ 모든 {self.config.concurrent_users}명 사용자 활성화 완료")

            # 모든 태스크 완료 대기
            await asyncio.gather(*tasks, return_exceptions=True)

        print("✅ 부하 테스트 완료")

    def calculate_statistics(self):
        """테스트 결과 통계 계산"""
        if not self.results:
            return

        response_times = [r.response_time for r in self.results if r.success]
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.success])

        self.stats.update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'average_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
            'requests_per_second': total_requests / self.config.test_duration,
            'error_rate': (total_requests - successful_requests) / total_requests * 100 if total_requests > 0 else 0
        })

    def generate_report(self) -> Dict:
        """상세 테스트 보고서 생성"""
        self.calculate_statistics()

        # 엔드포인트별 통계
        endpoint_stats = {}
        for result in self.results:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = {
                    'total': 0,
                    'success': 0,
                    'avg_response_time': 0,
                    'response_times': []
                }

            endpoint_stats[result.endpoint]['total'] += 1
            endpoint_stats[result.endpoint]['response_times'].append(result.response_time)
            if result.success:
                endpoint_stats[result.endpoint]['success'] += 1

        # 평균 응답 시간 계산
        for endpoint in endpoint_stats:
            times = endpoint_stats[endpoint]['response_times']
            endpoint_stats[endpoint]['avg_response_time'] = statistics.mean(times)
            endpoint_stats[endpoint]['success_rate'] = (
                endpoint_stats[endpoint]['success'] / endpoint_stats[endpoint]['total'] * 100
            )

        # 시간별 성능 분석
        time_buckets = {}
        for result in self.results:
            bucket = int(result.timestamp.timestamp() // 10) * 10  # 10초 단위
            if bucket not in time_buckets:
                time_buckets[bucket] = []
            time_buckets[bucket].append(result)

        return {
            'test_config': asdict(self.config),
            'overall_stats': self.stats,
            'endpoint_stats': endpoint_stats,
            'time_buckets': {
                str(bucket): {
                    'requests': len(results),
                    'avg_response_time': statistics.mean([r.response_time for r in results]),
                    'success_rate': len([r for r in results if r.success]) / len(results) * 100
                }
                for bucket, results in time_buckets.items()
            },
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """성능 기반 추천사항 생성"""
        recommendations = []

        if self.stats['error_rate'] > 5:
            recommendations.append("🔴 에러율이 5%를 초과합니다. 서버 안정성 개선이 필요합니다.")

        if self.stats['average_response_time'] > 2.0:
            recommendations.append("🟡 평균 응답 시간이 2초를 초과합니다. 성능 최적화가 필요합니다.")

        if self.stats['requests_per_second'] < self.config.target_rps * 0.8:
            recommendations.append("🔴 목표 RPS의 80% 미만입니다. 수평 확장을 고려하세요.")

        if self.stats['p95_response_time'] > 5.0:
            recommendations.append("🟡 95 퍼센타일 응답 시간이 5초를 초과합니다. 캐싱 전략을 검토하세요.")

        if not recommendations:
            recommendations.append("🟢 현재 성능이 양호합니다!")

        return recommendations


class ScalabilityTester:
    """확장성 테스트 실행기"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def run_scalability_test(self):
        """단계적 확장성 테스트"""
        print("🔍 확장성 테스트 시작")
        print("=" * 60)

        test_scenarios = [
            # 점진적 부하 증가
            (10, 30, 5),    # 10명, 30초, 5 RPS
            (50, 60, 25),   # 50명, 60초, 25 RPS
            (100, 90, 50),  # 100명, 90초, 50 RPS
            (200, 120, 100), # 200명, 120초, 100 RPS (목표)
        ]

        results = []

        for users, duration, target_rps in test_scenarios:
            print(f"\n📊 테스트 시나리오: {users}명 사용자, {duration}초, 목표 {target_rps} RPS")

            config = LoadTestConfig(
                base_url=self.base_url,
                concurrent_users=users,
                test_duration=duration,
                target_rps=target_rps
            )

            tester = PAMTalkLoadTester(config)

            try:
                asyncio.run(tester.run_load_test())
                report = tester.generate_report()
                results.append(report)

                print(f"✅ 결과:")
                print(f"   총 요청: {report['overall_stats']['total_requests']}")
                print(f"   성공률: {100 - report['overall_stats']['error_rate']:.1f}%")
                print(f"   평균 응답시간: {report['overall_stats']['average_response_time']:.3f}초")
                print(f"   실제 RPS: {report['overall_stats']['requests_per_second']:.1f}")

            except Exception as e:
                print(f"❌ 테스트 실패: {e}")
                break

            # 서버 복구 시간
            print("⏳ 서버 복구 대기 (10초)...")
            time.sleep(10)

        return results


def main():
    """메인 실행 함수"""
    print("🚀 PAM-TALK 성능 테스트 시스템")
    print("=" * 50)

    # 기본 서버 연결 확인
    import requests
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API 서버가 응답하지 않습니다. 서버를 먼저 시작해주세요.")
            return
        print("✅ API 서버 연결 확인")
    except:
        print("❌ API 서버에 연결할 수 없습니다. 서버를 먼저 시작해주세요.")
        print("   실행 명령: python run_demo.py")
        return

    # 사용자 선택
    print("\n테스트 유형을 선택하세요:")
    print("1. 기본 부하 테스트 (100명, 60초)")
    print("2. 확장성 테스트 (단계적 부하 증가)")
    print("3. 고부하 테스트 (200명, 100 RPS)")

    choice = input("선택 (1-3): ").strip()

    if choice == "1":
        config = LoadTestConfig(concurrent_users=100, test_duration=60, target_rps=50)
        tester = PAMTalkLoadTester(config)
        asyncio.run(tester.run_load_test())
        report = tester.generate_report()

        print("\n📋 최종 테스트 보고서")
        print("=" * 50)
        for key, value in report['overall_stats'].items():
            print(f"{key}: {value}")

        print("\n💡 추천사항:")
        for rec in report['recommendations']:
            print(f"  {rec}")

    elif choice == "2":
        tester = ScalabilityTester()
        results = tester.run_scalability_test()

        print("\n📈 확장성 테스트 요약")
        print("=" * 50)
        for i, result in enumerate(results):
            users = result['test_config']['concurrent_users']
            rps = result['overall_stats']['requests_per_second']
            error_rate = result['overall_stats']['error_rate']
            print(f"테스트 {i+1}: {users}명 → {rps:.1f} RPS (에러율: {error_rate:.1f}%)")

    elif choice == "3":
        config = LoadTestConfig(concurrent_users=200, test_duration=120, target_rps=100)
        tester = PAMTalkLoadTester(config)
        asyncio.run(tester.run_load_test())
        report = tester.generate_report()

        print(f"\n🎯 목표 달성 여부: {'✅ 성공' if report['overall_stats']['requests_per_second'] >= 80 else '❌ 실패'}")
        print(f"실제 RPS: {report['overall_stats']['requests_per_second']:.1f}/100")

    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()