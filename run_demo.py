#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 시스템 전체 실행 및 데모 스크립트
모든 컴포넌트를 순차적으로 시작하고 데모를 실행합니다.
"""

import os
import sys
import time
import subprocess
import webbrowser
import requests
import json
from datetime import datetime
from pathlib import Path
import threading
import signal


class PAMTalkDemo:
    """PAM-TALK 데모 실행 시스템"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.api_process = None
        self.demo_running = False
        self.demo_results = []

    def print_banner(self):
        """배너 출력"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 PAM-TALK 데모 시스템                    ║
║          블록체인 기반 AI 농업 예측 플랫폼 데모                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def check_dependencies(self):
        """의존성 확인"""
        print("📦 1단계: 의존성 확인 중...")

        # Python 버전 확인
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 이상이 필요합니다.")
            return False

        print(f"✅ Python {sys.version.split()[0]} 확인")

        # 필수 패키지 확인
        required_packages = [
            'flask', 'requests', 'pandas', 'numpy', 'scikit-learn', 'prophet'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} 설치됨")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} 누락")

        if missing_packages:
            print(f"\n❌ 누락된 패키지: {', '.join(missing_packages)}")
            print("다음 명령으로 설치하세요:")
            print("pip install -r requirements.txt")
            return False

        print("✅ 모든 의존성 확인 완료")
        return True

    def generate_mock_data(self):
        """모의 데이터 생성"""
        print("\n📊 2단계: 모의 데이터 생성 중...")

        try:
            # 데이터 디렉토리 생성
            data_dir = self.base_path / "data"
            data_dir.mkdir(exist_ok=True)

            # 농장 데이터 생성
            farms_data = [
                {
                    "farm_id": f"FARM_{i:03d}",
                    "name": f"농장 {i}",
                    "location": ["경기도", "충청도", "전라도", "경상도"][i % 4],
                    "crop_type": ["rice", "wheat", "corn", "soybean"][i % 4],
                    "area": 50 + (i * 10) % 200,
                    "organic_certified": i % 3 == 0,
                    "esg_score": 65 + (i * 5) % 35,
                    "token_balance": (i + 1) * 100
                }
                for i in range(20)
            ]

            with open(data_dir / "farms.json", "w", encoding="utf-8") as f:
                json.dump(farms_data, f, indent=2, ensure_ascii=False)

            # 거래 데이터 생성
            trades_data = [
                {
                    "trade_id": f"TRADE_{i:03d}",
                    "crop_type": ["rice", "wheat", "corn"][i % 3],
                    "quantity": 100 + (i * 50) % 500,
                    "price_per_kg": 2.0 + (i * 0.1) % 1.5,
                    "status": ["completed", "pending", "cancelled"][i % 3],
                    "timestamp": datetime.now().isoformat()
                }
                for i in range(15)
            ]

            with open(data_dir / "trades.json", "w", encoding="utf-8") as f:
                json.dump(trades_data, f, indent=2, ensure_ascii=False)

            # 시계열 데이터 생성 (수요 예측용)
            import pandas as pd
            dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
            demand_data = {
                "ds": dates.strftime('%Y-%m-%d').tolist(),
                "y": [1000 + i * 2 + (i % 30) * 10 for i in range(365)]
            }

            with open(data_dir / "demand_history.json", "w") as f:
                json.dump(demand_data, f, indent=2)

            print("✅ 농장 데이터 생성 완료")
            print("✅ 거래 데이터 생성 완료")
            print("✅ 수요 예측 데이터 생성 완료")

            return True

        except Exception as e:
            print(f"❌ 모의 데이터 생성 실패: {e}")
            return False

    def start_api_server(self):
        """API 서버 시작"""
        print("\n🚀 3단계: API 서버 시작 중...")

        try:
            # 기존 서버 프로세스 확인
            try:
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API 서버가 이미 실행 중입니다.")
                    return True
            except requests.RequestException:
                pass

            # API 서버 시작
            api_path = self.base_path / "api"
            if not api_path.exists():
                print("❌ API 디렉토리를 찾을 수 없습니다.")
                return False

            print("API 서버 시작 중... (백그라운드 실행)")

            # 환경 변수 설정
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            env['FLASK_DEBUG'] = '0'

            # API 서버 프로세스 시작
            self.api_process = subprocess.Popen([
                sys.executable, "app.py"
            ], cwd=api_path, env=env,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE)

            # 서버 시작 대기
            print("서버 시작 대기 중...")
            for i in range(30):  # 30초 대기
                try:
                    response = requests.get("http://localhost:5000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ API 서버 시작 완료!")
                        return True
                except requests.RequestException:
                    pass

                time.sleep(1)
                if i % 5 == 0:
                    print(f"  대기 중... ({i}/30초)")

            print("❌ API 서버 시작 실패 (시간 초과)")
            return False

        except Exception as e:
            print(f"❌ API 서버 시작 실패: {e}")
            return False

    def open_dashboard(self):
        """웹 브라우저에서 대시보드 열기"""
        print("\n🌐 4단계: 대시보드 열기...")

        try:
            dashboard_url = "http://localhost:5000"
            print(f"대시보드 URL: {dashboard_url}")

            # 대시보드 접근 가능 확인
            response = requests.get(dashboard_url, timeout=10)
            if response.status_code == 200:
                print("✅ 대시보드 접근 가능")

                # 웹 브라우저 열기
                webbrowser.open(dashboard_url)
                print("✅ 웹 브라우저에서 대시보드 열기 완료")
                return True
            else:
                print(f"❌ 대시보드 접근 실패 (상태 코드: {response.status_code})")
                return False

        except Exception as e:
            print(f"❌ 대시보드 열기 실패: {e}")
            return False

    def run_demo_scenarios(self):
        """데모 시나리오 실행"""
        print("\n🎭 5단계: 데모 시나리오 선택")
        print("=" * 50)

        scenarios = [
            "1. 농장 등록 및 ESG 토큰 발행 데모",
            "2. 수요 예측 및 거래 생성 데모",
            "3. 전체 시스템 통합 데모"
        ]

        for scenario in scenarios:
            print(scenario)

        print("0. 데모 스킵")
        print("=" * 50)

        try:
            choice = input("\n실행할 데모를 선택하세요 (0-3): ").strip()

            if choice == "0":
                print("데모를 스킵합니다.")
                return True
            elif choice in ["1", "2", "3"]:
                # demo_scenarios.py 실행
                from demo_scenarios import DemoScenarios
                demo = DemoScenarios()

                if choice == "1":
                    success = demo.run_farm_registration_demo()
                elif choice == "2":
                    success = demo.run_demand_prediction_demo()
                else:
                    success = demo.run_full_integration_demo()

                if success:
                    print("✅ 데모 실행 성공!")
                else:
                    print("❌ 데모 실행 실패!")

                return success
            else:
                print("❌ 잘못된 선택입니다.")
                return False

        except Exception as e:
            print(f"❌ 데모 실행 중 오류: {e}")
            return False

    def show_results_summary(self):
        """결과 요약 표시"""
        print("\n📋 데모 결과 요약")
        print("=" * 60)

        # 시스템 상태 확인
        try:
            # API 서버 상태
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API 서버: 정상 운영 중")
            else:
                print("❌ API 서버: 문제 발생")

            # 데이터베이스 상태 확인
            response = requests.get("http://localhost:5000/api/dashboard/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"📊 등록된 농장 수: {stats.get('total_farms', 0)}")
                print(f"💰 총 거래 수: {stats.get('total_transactions', 0)}")
                print(f"🪙 발행된 토큰: {stats.get('total_tokens', 0)}")
                print(f"🌱 평균 ESG 점수: {stats.get('avg_esg_score', 0):.1f}")

        except Exception as e:
            print(f"⚠️  상태 확인 중 오류: {e}")

        print("\n🌐 접속 정보:")
        print("  - 대시보드: http://localhost:5000")
        print("  - API 문서: http://localhost:5000/api/docs")
        print("  - 상태 확인: http://localhost:5000/health")

        print("\n📁 생성된 파일:")
        print("  - data/farms.json (농장 데이터)")
        print("  - data/trades.json (거래 데이터)")
        print("  - data/demand_history.json (수요 예측 데이터)")

        print("\n🔧 다음 단계:")
        print("  - 추가 농장 등록: POST /api/farms/register")
        print("  - 수요 예측 실행: POST /api/predict/demand")
        print("  - 거래 생성: POST /api/trades/create")
        print("  - 통합 테스트 실행: python run_tests.py")

    def cleanup(self):
        """정리 작업"""
        print("\n🧹 정리 작업 중...")

        # API 서버 프로세스 종료
        if self.api_process and self.api_process.poll() is None:
            print("API 서버 종료 중...")
            self.api_process.terminate()

            try:
                self.api_process.wait(timeout=10)
                print("✅ API 서버 정상 종료")
            except subprocess.TimeoutExpired:
                print("⚠️  강제 종료...")
                self.api_process.kill()

    def handle_interrupt(self, signum, frame):
        """인터럽트 처리"""
        print("\n\n🛑 사용자 중단 요청...")
        self.cleanup()
        sys.exit(0)

    def run(self):
        """메인 실행 함수"""
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)

        try:
            self.print_banner()

            # 1. 의존성 확인
            if not self.check_dependencies():
                self.show_error_solutions("dependencies")
                return False

            # 2. 모의 데이터 생성
            if not self.generate_mock_data():
                self.show_error_solutions("mock_data")
                return False

            # 3. API 서버 시작
            if not self.start_api_server():
                self.show_error_solutions("api_server")
                return False

            # 4. 대시보드 열기
            if not self.open_dashboard():
                self.show_error_solutions("dashboard")
                return False

            # 5. 데모 시나리오 실행
            if not self.run_demo_scenarios():
                print("⚠️  데모 시나리오 실행 중 문제가 발생했습니다.")

            # 6. 결과 요약
            self.show_results_summary()

            # 사용자 입력 대기
            input("\n계속하려면 Enter를 누르세요... (Ctrl+C로 종료)")

            return True

        except KeyboardInterrupt:
            print("\n\n🛑 사용자에 의해 중단되었습니다.")
            return False
        except Exception as e:
            print(f"\n❌ 예기치 못한 오류: {e}")
            return False
        finally:
            self.cleanup()

    def show_error_solutions(self, error_type):
        """에러별 해결 방법 제시"""
        solutions = {
            "dependencies": [
                "pip install -r requirements.txt",
                "python -m pip install --upgrade pip",
                "가상환경 생성: python -m venv venv",
                "가상환경 활성화 후 재시도"
            ],
            "mock_data": [
                "data 디렉토리 권한 확인",
                "디스크 공간 확인",
                "pandas 패키지 설치 확인: pip install pandas"
            ],
            "api_server": [
                "포트 5000 사용 중인지 확인: netstat -an | findstr :5000",
                "방화벽 설정 확인",
                "api/app.py 파일 존재 확인",
                "Flask 설치 확인: pip install flask"
            ],
            "dashboard": [
                "브라우저에서 직접 접속: http://localhost:5000",
                "방화벽 설정 확인",
                "다른 브라우저로 시도"
            ]
        }

        if error_type in solutions:
            print(f"\n💡 해결 방법 ({error_type}):")
            for i, solution in enumerate(solutions[error_type], 1):
                print(f"  {i}. {solution}")


def main():
    """메인 함수"""
    demo = PAMTalkDemo()
    success = demo.run()

    if success:
        print("\n🎉 PAM-TALK 데모가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 데모 실행 중 문제가 발생했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()