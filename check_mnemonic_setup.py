#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""니모닉 설정 확인"""

import sys
import json
from algosdk import mnemonic, account

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('pera_wallet_account.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    mn = data.get('mnemonic', '')

    if mn == "PASTE_YOUR_24_WORD_PASSPHRASE_HERE":
        print("❌ 니모닉이 아직 설정되지 않았습니다.")
        print("pera_wallet_account.json 파일을 열어서 니모닉을 붙여넣으세요.")
    else:
        # 단어 개수 확인
        words = mn.split()
        print(f"✓ 니모닉 단어 개수: {len(words)}")

        if len(words) not in [12, 24, 25]:
            print(f"❌ 오류: {len(words)}개 단어는 유효하지 않습니다.")
        else:
            # 주소 확인
            try:
                pk = mnemonic.to_private_key(mn)
                addr = account.address_from_private_key(pk)

                print(f"✓ 복원된 주소: {addr}")
                print()

                expected_addr = "37EJ5O4SUKT3SL7NWT6HJKNLXFLVEJ4N6VAMXH3K6C42EVCEPSVZB77MDQ"

                if addr == expected_addr:
                    print("✅ 페라 월렛 주소와 일치합니다!")
                    print()
                    print("🚀 준비 완료! 이제 토큰을 발행할 수 있습니다.")
                    print()
                    print("다음 명령어 실행:")
                    print("  python create_digital_coupon_token.py")
                else:
                    print("⚠️ 경고: 주소가 일치하지 않습니다.")
                    print(f"예상: {expected_addr}")
                    print(f"실제: {addr}")
                    print()
                    print("다른 계정의 니모닉을 입력하셨을 수 있습니다.")
            except Exception as e:
                print(f"❌ 니모닉이 유효하지 않습니다: {e}")

except FileNotFoundError:
    print("❌ pera_wallet_account.json 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"❌ 오류: {e}")
