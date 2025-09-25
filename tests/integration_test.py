"""
PAM-TALK 시스템 통합 테스트
모든 컴포넌트를 통합하여 전체 플로우를 검증합니다.
"""

import pytest
import requests
import time
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_models.esg_calculator import ESGCalculator
from ai_models.demand_predictor import DemandPredictor
from ai_models.anomaly_detector import AnomalyDetector
from algorand_utils import AlgorandUtils
from data.data_processor import DataProcessor


class IntegrationTestRunner:
    """통합 테스트 실행 및 결과 관리"""

    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = []
        self.performance_metrics = {}

    def log_result(self, test_name: str, success: bool, duration: float, details: str = ""):
        """테스트 결과 로깅"""
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)

    def generate_report(self):
        """테스트 보고서 생성"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "total_duration": sum(r["duration"] for r in self.test_results)
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }

        # JSON 보고서 저장
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # HTML 보고서 생성
        self._generate_html_report(report)

        return report

    def _generate_html_report(self, report: Dict):
        """HTML 테스트 보고서 생성"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PAM-TALK 통합 테스트 보고서</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 3px; }}
                .success {{ background: #d4edda; border-left: 4px solid #28a745; }}
                .failure {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
                .performance {{ background: #e2f3ff; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>PAM-TALK 통합 테스트 보고서</h1>
            <div class="summary">
                <h2>테스트 요약</h2>
                <p>총 테스트: {report['summary']['total_tests']}</p>
                <p>성공: {report['summary']['passed']}</p>
                <p>실패: {report['summary']['failed']}</p>
                <p>성공률: {report['summary']['success_rate']}</p>
                <p>총 실행 시간: {report['summary']['total_duration']:.2f}초</p>
                <p>실행 시간: {report['timestamp']}</p>
            </div>

            <h2>테스트 결과</h2>
            {''.join([
                f'<div class="test-result {"success" if r["success"] else "failure"}">
                    <strong>{r["test_name"]}</strong> - {"성공" if r["success"] else "실패"}
                    <br>실행 시간: {r["duration"]:.3f}초
                    {f"<br>세부사항: {r["details"]}" if r["details"] else ""}
                </div>'
                for r in report['test_results']
            ])}

            <div class="performance">
                <h2>성능 지표</h2>
                <pre>{json.dumps(report['performance_metrics'], indent=2, ensure_ascii=False)}</pre>
            </div>
        </body>
        </html>
        """

        with open("test_report.html", "w", encoding="utf-8") as f:
            f.write(html_template)


@pytest.fixture(scope="session")
def test_runner():
    """테스트 실행기 픽스처"""
    return IntegrationTestRunner()


@pytest.fixture(scope="session")
def api_server():
    """API 서버가 실행 중인지 확인"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pytest.skip("API 서버가 실행되지 않음")
    return False


class TestFarmRegistrationFlow:
    """농장 등록 → ESG 점수 계산 → 토큰 발행 플로우 테스트"""

    def test_complete_farm_registration_flow(self, test_runner, api_server):
        """농장 등록부터 토큰 발행까지 전체 플로우 테스트"""
        start_time = time.time()

        try:
            # 1. 농장 등록 데이터
            farm_data = {
                "farm_id": "TEST_FARM_001",
                "location": "경기도 이천시",
                "crop_type": "rice",
                "area": 100.5,
                "organic_certified": True,
                "irrigation_method": "drip",
                "renewable_energy": True,
                "carbon_footprint": 2.5
            }

            # 2. 농장 등록 API 호출
            registration_response = requests.post(
                f"{test_runner.base_url}/api/farms/register",
                json=farm_data,
                timeout=30
            )

            assert registration_response.status_code == 200, f"농장 등록 실패: {registration_response.text}"
            registration_result = registration_response.json()

            # 3. ESG 점수 계산 확인
            assert "esg_score" in registration_result, "ESG 점수가 응답에 없음"
            assert registration_result["esg_score"] > 0, "ESG 점수가 0 이하"

            # 4. 토큰 발행 확인
            assert "token_amount" in registration_result, "토큰 발행량이 응답에 없음"
            assert registration_result["token_amount"] > 0, "토큰 발행량이 0 이하"

            # 5. 블록체인 기록 확인
            if "transaction_id" in registration_result:
                # 트랜잭션 조회
                tx_response = requests.get(
                    f"{test_runner.base_url}/api/transaction/{registration_result['transaction_id']}",
                    timeout=10
                )
                assert tx_response.status_code == 200, "트랜잭션 조회 실패"

            duration = time.time() - start_time
            test_runner.log_result("농장 등록 플로우", True, duration,
                                 f"ESG 점수: {registration_result['esg_score']}, 토큰: {registration_result['token_amount']}")

        except Exception as e:
            duration = time.time() - start_time
            test_runner.log_result("농장 등록 플로우", False, duration, str(e))
            raise


class TestDemandPredictionFlow:
    """수요 예측 → 거래 생성 → 이상 탐지 플로우 테스트"""

    def test_demand_prediction_trading_flow(self, test_runner, api_server):
        """수요 예측부터 거래 생성까지 플로우 테스트"""
        start_time = time.time()

        try:
            # 1. 수요 예측 요청
            prediction_data = {
                "crop_type": "rice",
                "region": "경기도",
                "forecast_days": 30
            }

            prediction_response = requests.post(
                f"{test_runner.base_url}/api/predict/demand",
                json=prediction_data,
                timeout=30
            )

            assert prediction_response.status_code == 200, f"수요 예측 실패: {prediction_response.text}"
            prediction_result = prediction_response.json()

            # 2. 예측 결과 검증
            assert "predictions" in prediction_result, "예측 결과가 없음"
            assert len(prediction_result["predictions"]) > 0, "예측 데이터가 비어있음"

            # 3. 거래 생성 요청
            trade_data = {
                "crop_type": "rice",
                "quantity": 1000,
                "price_per_kg": 2.5,
                "delivery_date": (datetime.now() + timedelta(days=7)).isoformat()
            }

            trade_response = requests.post(
                f"{test_runner.base_url}/api/trades/create",
                json=trade_data,
                timeout=30
            )

            assert trade_response.status_code == 200, f"거래 생성 실패: {trade_response.text}"
            trade_result = trade_response.json()

            # 4. 이상 탐지 실행
            if "trade_id" in trade_result:
                anomaly_response = requests.post(
                    f"{test_runner.base_url}/api/detect/anomaly",
                    json={"trade_id": trade_result["trade_id"]},
                    timeout=20
                )

                assert anomaly_response.status_code == 200, "이상 탐지 실패"
                anomaly_result = anomaly_response.json()
                assert "is_anomaly" in anomaly_result, "이상 탐지 결과가 없음"

            duration = time.time() - start_time
            test_runner.log_result("수요 예측 거래 플로우", True, duration,
                                 f"예측 데이터 수: {len(prediction_result['predictions'])}")

        except Exception as e:
            duration = time.time() - start_time
            test_runner.log_result("수요 예측 거래 플로우", False, duration, str(e))
            raise


class TestBlockchainDataFlow:
    """블록체인 기록 → 데이터 조회 → 대시보드 표시 플로우 테스트"""

    def test_blockchain_dashboard_flow(self, test_runner, api_server):
        """블록체인 데이터 플로우 테스트"""
        start_time = time.time()

        try:
            # 1. 블록체인 데이터 조회
            blockchain_response = requests.get(
                f"{test_runner.base_url}/api/blockchain/transactions",
                params={"limit": 10},
                timeout=20
            )

            assert blockchain_response.status_code == 200, f"블록체인 조회 실패: {blockchain_response.text}"
            blockchain_data = blockchain_response.json()

            # 2. 대시보드 데이터 조회
            dashboard_response = requests.get(
                f"{test_runner.base_url}/api/dashboard/stats",
                timeout=15
            )

            assert dashboard_response.status_code == 200, f"대시보드 조회 실패: {dashboard_response.text}"
            dashboard_data = dashboard_response.json()

            # 3. 대시보드 데이터 검증
            expected_keys = ["total_farms", "total_transactions", "total_tokens", "avg_esg_score"]
            for key in expected_keys:
                assert key in dashboard_data, f"대시보드에 {key} 데이터가 없음"

            duration = time.time() - start_time
            test_runner.log_result("블록체인 대시보드 플로우", True, duration,
                                 f"거래수: {dashboard_data.get('total_transactions', 0)}")

        except Exception as e:
            duration = time.time() - start_time
            test_runner.log_result("블록체인 대시보드 플로우", False, duration, str(e))
            raise


class TestAPIEndpoints:
    """API 엔드포인트 전체 테스트"""

    def test_all_api_endpoints(self, test_runner, api_server):
        """모든 API 엔드포인트 테스트"""
        start_time = time.time()

        endpoints_to_test = [
            ("GET", "/health", None, 200),
            ("GET", "/api/farms", None, 200),
            ("GET", "/api/trades", None, 200),
            ("GET", "/api/dashboard/stats", None, 200),
            ("GET", "/api/blockchain/status", None, 200)
        ]

        failed_endpoints = []

        for method, endpoint, data, expected_status in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{test_runner.base_url}{endpoint}", timeout=10)
                elif method == "POST":
                    response = requests.post(f"{test_runner.base_url}{endpoint}", json=data, timeout=10)

                if response.status_code != expected_status:
                    failed_endpoints.append(f"{method} {endpoint}: {response.status_code}")

            except requests.RequestException as e:
                failed_endpoints.append(f"{method} {endpoint}: {str(e)}")

        duration = time.time() - start_time

        if failed_endpoints:
            test_runner.log_result("API 엔드포인트 테스트", False, duration,
                                 f"실패한 엔드포인트: {', '.join(failed_endpoints)}")
            assert False, f"API 엔드포인트 테스트 실패: {failed_endpoints}"
        else:
            test_runner.log_result("API 엔드포인트 테스트", True, duration,
                                 f"테스트된 엔드포인트: {len(endpoints_to_test)}개")


class TestPerformance:
    """성능 측정 테스트"""

    def test_response_time_performance(self, test_runner, api_server):
        """응답 시간 성능 테스트"""
        start_time = time.time()

        try:
            performance_results = {}

            # 1. 농장 등록 성능
            farm_data = {
                "farm_id": "PERF_TEST_001",
                "location": "성능테스트",
                "crop_type": "rice",
                "area": 50.0
            }

            registration_times = []
            for i in range(5):
                reg_start = time.time()
                response = requests.post(
                    f"{test_runner.base_url}/api/farms/register",
                    json={**farm_data, "farm_id": f"PERF_TEST_{i:03d}"},
                    timeout=30
                )
                reg_duration = time.time() - reg_start
                registration_times.append(reg_duration)

                assert response.status_code == 200, f"농장 등록 실패: {response.text}"

            performance_results["farm_registration"] = {
                "avg_response_time": sum(registration_times) / len(registration_times),
                "max_response_time": max(registration_times),
                "min_response_time": min(registration_times)
            }

            # 2. 데이터 조회 성능
            query_times = []
            for _ in range(10):
                query_start = time.time()
                response = requests.get(f"{test_runner.base_url}/api/farms", timeout=10)
                query_duration = time.time() - query_start
                query_times.append(query_duration)

                assert response.status_code == 200, "농장 조회 실패"

            performance_results["data_query"] = {
                "avg_response_time": sum(query_times) / len(query_times),
                "max_response_time": max(query_times),
                "min_response_time": min(query_times)
            }

            test_runner.performance_metrics = performance_results

            duration = time.time() - start_time
            test_runner.log_result("성능 테스트", True, duration,
                                 f"평균 등록 시간: {performance_results['farm_registration']['avg_response_time']:.3f}초")

        except Exception as e:
            duration = time.time() - start_time
            test_runner.log_result("성능 테스트", False, duration, str(e))
            raise


def run_integration_tests():
    """통합 테스트 실행 함수"""
    test_runner = IntegrationTestRunner()

    print("🚀 PAM-TALK 통합 테스트 시작...")

    # pytest 실행
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--html=pytest_report.html",
        "--self-contained-html"
    ]

    exit_code = pytest.main(pytest_args)

    # 보고서 생성
    print("\n📊 테스트 보고서 생성 중...")
    report = test_runner.generate_report()

    print(f"\n✅ 테스트 완료!")
    print(f"총 {report['summary']['total_tests']}개 테스트 중 {report['summary']['passed']}개 성공")
    print(f"성공률: {report['summary']['success_rate']}")
    print(f"보고서: test_report.html, test_report.json")

    return exit_code == 0


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)