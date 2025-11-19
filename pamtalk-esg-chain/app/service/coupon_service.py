# -*- coding: utf-8 -*-
from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv

# Base62 인코딩 유틸
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
def encode_base62(num):
    if num == 0:
        return BASE62_ALPHABET[0]
    arr = []
    while num:
        num, rem = divmod(num, 62)
        arr.append(BASE62_ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

# 환경 변수 로딩
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 쿠폰 생성 함수
def create_initial_coupons(amount: int, description: str, issued_by: str,
                           asset_id: int, asset_name: str, unit_name: str):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )
    cursor = conn.cursor()
    now = datetime.now()

    # 1. 발행 이력 저장 (unit_name 포함)
    cursor.execute("""
        INSERT INTO token_mint_history (amount, unit_name, description, issued_by, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (amount, unit_name, description, issued_by, now))
    mint_history_id = cursor.fetchone()[0]

    # 2. 기존 쿠폰 수량 확인 → 중복 방지용 시리얼 시작점 설정
    cursor.execute("""
        SELECT COUNT(*) FROM esg_coupons WHERE coupon_code LIKE %s
    """, (f"{unit_name}-%",))
    existing_count = cursor.fetchone()[0]
    start_serial = existing_count + 1

    # 3. 쿠폰 일괄 생성 및 저장
    BATCH_SIZE = 1000
    for batch_start in range(0, amount, BATCH_SIZE):
        batch = []
        for i in range(0, min(BATCH_SIZE, amount - batch_start)):
            serial_number = start_serial + batch_start + i
            base62_serial = encode_base62(serial_number)
            coupon_code = f"{unit_name}-{base62_serial}"

            batch.append((
                coupon_code, asset_id, asset_name, mint_history_id,
                None, None, None, 'ISSUED',
                None, None, None, None, None, None, None,
                now, now
            ))

        try:
            args_str = ','.join(cursor.mogrify(
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                x
            ).decode('utf-8') for x in batch)

            cursor.execute("""
                INSERT INTO esg_coupons
                (coupon_code, asset_id, asset_name, mint_history_id,
                 committee_id, provider_id, consumer_id,
                 status, committee_assigned_at, provider_assigned_at, consumer_assigned_at,
                 used_at, redeemed_at, expired_at, tx_hash,
                 created_at, updated_at)
                VALUES """ + args_str)
        except Exception as e:
            print("[ERROR] Batch insert 오류:", e)
            raise

        conn.commit()
        print(f"[INFO] Inserted {batch_start + len(batch)} / {amount}")

    cursor.close()
    conn.close()
    print("[SUCCESS] 쿠폰 발행 완료")
