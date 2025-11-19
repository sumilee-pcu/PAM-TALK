#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 계정 잔액 확인"""

import sys
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

address = "PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE"

print("=" * 70)
print("Python 계정 잔액 확인")
print("=" * 70)
print()
print(f"주소: {address}")
print(f"탐색기: https://algoexplorer.io/address/{address}")
print()

api_url = f'https://mainnet-api.algonode.cloud/v2/accounts/{address}'
response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()
    balance = data.get('amount', 0) / 1000000

    print(f"💰 현재 잔액: {balance:.6f} ALGO")
    print()

    if balance >= 10:
        print("✅ 충분한 잔액! 토큰 발행 가능합니다.")
        print()
        print("다음 명령어로 토큰 발행:")
        print("  python create_digital_coupon_token.py")
    elif balance > 0:
        print("⚠️  잔액이 부족합니다. 최소 10 ALGO 권장")
        print(f"   현재: {balance:.6f} ALGO")
        print(f"   부족: {10 - balance:.6f} ALGO")
    else:
        print("❌ 아직 ALGO가 전송되지 않았습니다.")
        print()
        print("페라 월렛에서 전송 확인:")
        print(f"  받는 주소: {address}")
        print("  금액: 10 ALGO")
else:
    print(f"❌ 오류: API 응답 실패 ({response.status_code})")

print()
print("=" * 70)
