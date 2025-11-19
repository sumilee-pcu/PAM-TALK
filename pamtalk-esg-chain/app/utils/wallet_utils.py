# -*- coding: utf-8 -*-
# app/utils/wallet_utils.py

import psycopg2
from algosdk import mnemonic, account
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def get_wallet_keys(mnemonic_phrase):
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    return address, private_key


def get_wallet_keys_from_address(receiver_address, table_name):
    """
    receiver_address를 사용하여 특정 테이블에서 지갑 키를 조회한다.

    :param receiver_address: 지갑 주소
    :param table_name: 'committees' 또는 'providers' 테이블 이름
    :return: 지갑 주소와 개인키
    """
    print(f"[지갑 키 조회] 주소: {receiver_address}")
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        with conn.cursor() as cur:
            # 테이블 이름을 동적으로 처리하기 위해 SQL 문에 변수 삽입
            query = f"SELECT wallet_mnemonic FROM {table_name} WHERE wallet_address = %s"
            cur.execute(query, (receiver_address,))
            result = cur.fetchone()
            if result is None:
                raise Exception(f"[오류] 수신자 주소에 대한 mnemonic이 {table_name} 테이블에 없음: {receiver_address}")

            wallet_mnemonic = result[0]
            private_key = mnemonic.to_private_key(wallet_mnemonic)
            address = account.address_from_private_key(private_key)

            print(f"[지갑 키 반환] 주소: {address}")
            return address, private_key
    finally:
        conn.close()