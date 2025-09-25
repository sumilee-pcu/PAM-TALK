#!/usr/bin/env python3
"""
PAM-TALK 통합 테스트 실행 스크립트
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def check_dependencies():
    """필수 의존성 확인"""
    print("📦 의존성 확인 중...")

    try:
        import pytest
        import requests
        print("✅ pytest, requests 설치됨")
    except ImportError as e:
        print(f"❌ 의존성 누락: {e}")
        print("pip install -r requirements.txt 를 실행해주세요.")
        return False

    return True


def check_api_server():
    """API 서버 실행 상태 확인"""
    print("🔍 API 서버 상태 확인 중...")

    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API 서버가 실행 중입니다.")
            return True
    except requests.RequestException:
        pass

    print("⚠️  API 서버가 실행되지 않았습니다.")
    print("   다음 명령으로 서버를 시작해주세요:")
    print("   cd api && python app.py")
    return False


def run_unit_tests():
    """단위 테스트 실행"""
    print("\n🧪 단위 테스트 실행 중...")

    unit_test_files = [
        "ai_models/test_esg_calculator.py",
        "ai_models/test_demand_predictor.py",
        "ai_models/test_anomaly_detector.py",
        "data/test_data_processor.py",
        "contracts/contract_test.py",
        "api/test_api.py"
    ]

    passed = 0
    failed = 0

    for test_file in unit_test_files:
        if os.path.exists(test_file):
            print(f"  테스트 중: {test_file}")
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                passed += 1
                print(f"  ✅ {test_file} 통과")
            else:
                failed += 1
                print(f"  ❌ {test_file} 실패")
                print(f"     오류: {result.stderr[:200]}...")

    print(f"\n단위 테스트 결과: {passed}개 통과, {failed}개 실패")
    return failed == 0


def run_integration_tests():
    """통합 테스트 실행"""
    print("\n🚀 통합 테스트 실행 중...")

    # 통합 테스트 실행
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration_test.py",
        "-v",
        "--tb=short",
        "--html=test_report.html",
        "--self-contained-html"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ 통합 테스트 성공!")
    else:
        print("❌ 통합 테스트 실패!")
        print(f"오류 출력:\n{result.stderr}")
        print(f"표준 출력:\n{result.stdout}")

    return result.returncode == 0


def generate_coverage_report():
    """커버리지 보고서 생성"""
    print("\n📊 커버리지 보고서 생성 중...")

    try:
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term",
            "tests/"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 커버리지 보고서 생성 완료 (htmlcov/index.html)")
        else:
            print("⚠️  커버리지 보고서 생성 실패")
            print("pytest-cov가 설치되지 않았을 수 있습니다.")

    except Exception as e:
        print(f"⚠️  커버리지 보고서 생성 중 오류: {e}")


def main():
    """메인 실행 함수"""
    print("🎯 PAM-TALK 통합 테스트 시스템 시작")
    print("=" * 50)

    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)

    # API 서버 확인
    server_running = check_api_server()

    # 단위 테스트 실행
    unit_test_success = True
    if input("\n단위 테스트를 실행하시겠습니까? (y/n): ").lower() == 'y':
        unit_test_success = run_unit_tests()

    # 통합 테스트 실행
    integration_test_success = True
    if server_running:
        if input("\n통합 테스트를 실행하시겠습니까? (y/n): ").lower() == 'y':
            integration_test_success = run_integration_tests()
    else:
        print("API 서버가 실행되지 않아 통합 테스트를 건너뜁니다.")

    # 커버리지 보고서
    if input("\n커버리지 보고서를 생성하시겠습니까? (y/n): ").lower() == 'y':
        generate_coverage_report()

    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 테스트 실행 요약")
    print(f"단위 테스트: {'✅ 성공' if unit_test_success else '❌ 실패'}")
    print(f"통합 테스트: {'✅ 성공' if integration_test_success else '❌ 실패'}")

    if integration_test_success and os.path.exists("test_report.html"):
        print("📊 보고서: test_report.html")

    # 전체 성공 여부 반환
    overall_success = unit_test_success and integration_test_success

    if overall_success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")

    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()