# -*- coding: utf-8 -*-
from algosdk import account, mnemonic

def create_hcf_wallet():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)

    print("HCF 관리자 지갑 생성 완료")
    print(f"지갑 주소: {address}")
    print(f"니모닉 (반드시 .env에 저장):\n{mnemonic_phrase}")

    # https://bank.testnet.algorand.network/ -> 주소로 충전하기

if __name__ == "__main__":
    create_hcf_wallet()