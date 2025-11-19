#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인넷용 알고랜드 계정 생성
"""

import json
import sys
from datetime import datetime
from algosdk import account, mnemonic
import requests

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_mainnet_account():
    """새로운 알고랜드 메인넷 계정 생성"""
    private_key, address = account.generate_account()
    mn = mnemonic.from_private_key(private_key)

    account_info = {
        'address': address,
        'private_key': private_key,
        'mnemonic': mn,
        'created_for': 'PAM-TALK Mainnet Token',
        'purpose': 'Algorand mainnet token operations',
        'created_at': datetime.now().isoformat(),
        'network': 'mainnet'
    }

    return account_info

def check_mainnet_balance(address):
    """메인넷 계정 잔액 확인"""
    api_url = f'https://mainnet-api.algonode.cloud/v2/accounts/{address}'

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get('amount', 0)
            return balance / 1000000
        else:
            return 0
    except Exception as e:
        print(f"Balance check error: {e}")
        return 0

def main():
    print("="*60)
    print("PAM-TALK 메인넷 계정 생성기")
    print("="*60)
    print()

    # 새 메인넷 계정 생성
    account_info = create_mainnet_account()

    print(f"✓ 메인넷 계정 주소: {account_info['address']}")
    print()
    print(f"✓ 니모닉 (Mnemonic):")
    print(f"  {account_info['mnemonic']}")
    print()
    print("⚠️  보안 경고: 니모닉 구문을 안전하게 보관하세요!")
    print("   이 구문으로 계정을 복구할 수 있습니다.")
    print()
    print("="*60)
    print()

    # 메인넷 ALGO 구매 안내
    print("📌 메인넷 ALGO 획득 방법:")
    print("1. 거래소에서 ALGO 구매:")
    print("   - Binance, Coinbase, Upbit 등")
    print("2. 위 주소로 ALGO 전송 (최소 0.5 ALGO 권장)")
    print("3. 토큰 발행 수수료: 약 0.001 ALGO")
    print()

    # 계정 탐색기 링크
    print("🔗 메인넷 계정 탐색기:")
    print(f"   https://algoexplorer.io/address/{account_info['address']}")
    print()

    # 현재 잔액 확인
    balance = check_mainnet_balance(account_info['address'])
    print(f"💰 현재 잔액: {balance:.6f} ALGO")
    print()

    # 계정 정보 JSON 파일 저장
    filename = f"pam_mainnet_account_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(account_info, f, indent=2)

    print(f"✓ 계정 정보 저장됨: {filename}")
    print()

    # 사용자 안내
    print("="*60)
    print("다음 단계:")
    print("1. 위 주소로 ALGO를 전송하세요 (최소 0.5 ALGO)")
    print("2. 잔액 확인 후 토큰 발행을 진행합니다")
    print("="*60)

    return account_info

if __name__ == "__main__":
    main()
