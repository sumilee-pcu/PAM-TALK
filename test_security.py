#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 보안 강화 테스트 스크립트
쿠폰 발행 API의 권한 체크가 올바르게 작동하는지 검증
"""

import requests
import json
from datetime import datetime

# API 엔드포인트
BASE_URL = "http://localhost:5000"
TOKEN_API_URL = f"{BASE_URL}/api/token"
AUTH_API_URL = f"{BASE_URL}/api/auth"
GIVE_COUPON_URL = f"{BASE_URL}/api/give-coupon"

# 테스트 사용자
TEST_USERS = {
    'admin': {
        'email': 'admin@pamtalk.com',
        'password': 'Admin123!'
    },
    'committee': {
        'email': 'committee@pamtalk.com',
        'password': 'Committee123!'
    },
    'consumer': {
        'email': 'consumer@pamtalk.com',
        'password': 'Consumer123!'
    },
    'supplier': {
        'email': 'supplier@pamtalk.com',
        'password': 'Supplier123!'
    }
}


def print_header(text):
    """테스트 섹션 헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test(test_name, passed):
    """테스트 결과 출력"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")


def login(user_type):
    """로그인하여 토큰 획득"""
    user = TEST_USERS[user_type]
    response = requests.post(f"{AUTH_API_URL}/login", json=user)

    if response.status_code == 200:
        data = response.json()
        return data['tokens']['accessToken']
    else:
        print(f"Login failed for {user_type}: {response.text}")
        return None


def test_unauthorized_access():
    """인증 없이 쿠폰 발행 시도 (실패해야 함)"""
    print_header("TEST 1: 인증 없이 쿠폰 발행 시도")

    # 토큰 없이 mint 엔드포인트 호출
    response = requests.post(
        f"{TOKEN_API_URL}/mint",
        json={
            "amount": 100,
            "description": "Unauthorized test",
            "unit_name": "TEST"
        }
    )

    # 401 Unauthorized 응답을 받아야 성공
    passed = response.status_code == 401
    print_test("토큰 없이 /mint 호출 -> 401 Unauthorized", passed)

    if not passed:
        print(f"  Expected 401, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")

    return passed


def test_consumer_unauthorized():
    """일반 사용자(CONSUMER)로 쿠폰 발행 시도 (실패해야 함)"""
    print_header("TEST 2: 일반 사용자 권한으로 쿠폰 발행 시도")

    # 소비자로 로그인
    token = login('consumer')
    if not token:
        print_test("Consumer 로그인 실패", False)
        return False

    print(f"Consumer 토큰 획득: {token[:30]}...")

    # mint 시도
    response = requests.post(
        f"{TOKEN_API_URL}/mint",
        json={
            "amount": 100,
            "description": "Consumer test",
            "unit_name": "TEST"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # 403 Forbidden 응답을 받아야 성공
    passed = response.status_code == 403
    print_test("CONSUMER 권한으로 /mint 호출 -> 403 Forbidden", passed)

    if not passed:
        print(f"  Expected 403, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")

    return passed


def test_admin_authorized():
    """관리자(ADMIN)로 쿠폰 발행 (성공해야 함)"""
    print_header("TEST 3: 관리자 권한으로 쿠폰 발행")

    # 관리자로 로그인
    token = login('admin')
    if not token:
        print_test("Admin 로그인 실패", False)
        return False

    print(f"Admin 토큰 획득: {token[:30]}...")

    # mint 시도
    response = requests.post(
        f"{TOKEN_API_URL}/mint",
        json={
            "amount": 10,
            "description": "Admin authorized test",
            "unit_name": "TADM"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # 200 OK 응답을 받아야 성공
    passed = response.status_code == 200
    print_test("ADMIN 권한으로 /mint 호출 -> 200 OK", passed)

    if not passed:
        print(f"  Expected 200, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    else:
        data = response.json()
        print(f"  ✓ {data.get('message')}")

    return passed


def test_committee_authorized():
    """위원회(COMMITTEE)로 쿠폰 발행 (성공해야 함)"""
    print_header("TEST 4: 위원회 권한으로 쿠폰 발행")

    # 위원회로 로그인
    token = login('committee')
    if not token:
        print_test("Committee 로그인 실패", False)
        return False

    print(f"Committee 토큰 획득: {token[:30]}...")

    # mint 시도
    response = requests.post(
        f"{TOKEN_API_URL}/mint",
        json={
            "amount": 10,
            "description": "Committee authorized test",
            "unit_name": "TCOM"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # 200 OK 응답을 받아야 성공
    passed = response.status_code == 200
    print_test("COMMITTEE 권한으로 /mint 호출 -> 200 OK", passed)

    if not passed:
        print(f"  Expected 200, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    else:
        data = response.json()
        print(f"  ✓ {data.get('message')}")

    return passed


def test_invalid_token():
    """유효하지 않은 토큰으로 접근 시도 (실패해야 함)"""
    print_header("TEST 5: 유효하지 않은 토큰으로 접근")

    # 가짜 토큰
    fake_token = "invalid_token_12345"

    response = requests.post(
        f"{TOKEN_API_URL}/mint",
        json={
            "amount": 100,
            "description": "Invalid token test",
            "unit_name": "TEST"
        },
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # 401 Unauthorized 응답을 받아야 성공
    passed = response.status_code == 401
    print_test("유효하지 않은 토큰으로 /mint 호출 -> 401 Unauthorized", passed)

    if not passed:
        print(f"  Expected 401, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")

    return passed


def run_all_tests():
    """모든 보안 테스트 실행"""
    print("\n" + "=" * 80)
    print("  PAM-TALK 보안 강화 테스트")
    print("  시작 시간:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    results = []

    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"\n서버 연결 확인: {BASE_URL}")
        print(f"  상태: {response.status_code} - {response.json().get('status')}")
    except Exception as e:
        print(f"\n❌ 서버 연결 실패: {e}")
        print("서버가 실행 중인지 확인하세요: python api/app.py")
        return

    # 테스트 실행
    try:
        results.append(("인증 없이 접근", test_unauthorized_access()))
        results.append(("CONSUMER 권한 제한", test_consumer_unauthorized()))
        results.append(("ADMIN 권한 허용", test_admin_authorized()))
        results.append(("COMMITTEE 권한 허용", test_committee_authorized()))
        results.append(("유효하지 않은 토큰", test_invalid_token()))
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

    # 결과 요약
    print_header("테스트 결과 요약")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")

    print("\n" + "-" * 80)
    print(f"  총 테스트: {total}")
    print(f"  통과: {passed}")
    print(f"  실패: {total - passed}")
    print(f"  성공률: {(passed/total*100):.1f}%")
    print("-" * 80)

    if passed == total:
        print("\n✅ 모든 보안 테스트를 통과했습니다!")
        print("   쿠폰 발행 API가 올바르게 보호되고 있습니다.")
    else:
        print("\n⚠️  일부 테스트가 실패했습니다.")
        print("   보안 설정을 다시 확인해주세요.")

    print("\n종료 시간:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()
