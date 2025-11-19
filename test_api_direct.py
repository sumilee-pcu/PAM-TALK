#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct API test without algosdk"""

import sys
import json
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 테스트 주소
address = "PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE"

print("=" * 70)
print("Direct API Test")
print("=" * 70)
print()

# requests 라이브러리로 직접 API 호출
api_url = f"https://mainnet-api.algonode.cloud/v2/accounts/{address}"

print(f"Calling: {api_url}")
print()

try:
    # User-Agent 헤더 추가
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(api_url, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()

    if response.status_code == 200:
        data = response.json()
        balance = data.get('amount', 0) / 1000000
        print(f"✅ Success!")
        print(f"Balance: {balance:.6f} ALGO")
        print(f"Address: {data.get('address', 'N/A')}")
    elif response.status_code == 404:
        print("❌ Account not found - 아직 거래 내역이 없는 계정입니다.")
        print("   첫 거래(ALGO 수신)가 완료되면 활성화됩니다.")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
