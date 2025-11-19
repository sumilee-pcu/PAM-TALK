#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
페라 월렛 니모닉 검증 및 계정 정보 확인
"""

import sys
from algosdk import mnemonic, account

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def verify_mnemonic(mnemonic_phrase):
    """니모닉 검증 및 주소 확인"""
    try:
        # 니모닉에서 private key 복원
        private_key = mnemonic.to_private_key(mnemonic_phrase)

        # 주소 생성
        address = account.address_from_private_key(private_key)

        return {
            'valid': True,
            'address': address,
            'private_key': private_key
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def main():
    print("=" * 60)
    print("페라 월렛 니모닉 검증기")
    print("=" * 60)
    print()
    print("니모닉 구문을 입력하세요 (24 또는 25단어):")
    print("예: word1 word2 word3 ... word24")
    print()

    # 니모닉 입력 받기
    mnemonic_input = input("Mnemonic: ").strip()

    # 단어 개수 확인
    words = mnemonic_input.split()
    print(f"\n입력된 단어 개수: {len(words)}")

    if len(words) not in [12, 24, 25]:
        print(f"❌ 오류: {len(words)}개 단어는 유효하지 않습니다.")
        print("   12, 24, 또는 25 단어여야 합니다.")
        return

    # 검증
    print("\n검증 중...")
    result = verify_mnemonic(mnemonic_input)

    if result['valid']:
        print("✅ 니모닉이 유효합니다!")
        print()
        print(f"주소: {result['address']}")
        print()

        # 페라 월렛 주소와 비교
        pera_address = "37EJ5O4SUKT3SL7NWT6HJKNLXFLVEJ4N6VAMXH3K6C42EVCEPSVZB77MDQ"
        if result['address'] == pera_address:
            print("✅ 페라 월렛 주소와 일치합니다!")
            print()
            print("이제 이 니모닉으로 토큰을 발행할 수 있습니다.")
        else:
            print("⚠️  경고: 주소가 일치하지 않습니다!")
            print(f"예상 주소: {pera_address}")
            print(f"실제 주소: {result['address']}")
            print()
            print("다른 계정의 니모닉을 입력하셨을 수 있습니다.")
    else:
        print(f"❌ 니모닉이 유효하지 않습니다.")
        print(f"오류: {result['error']}")

if __name__ == "__main__":
    main()
