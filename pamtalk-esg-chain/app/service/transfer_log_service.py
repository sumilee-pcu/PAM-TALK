# -*- coding: utf-8 -*-
# app/service/log_token_distribution.py

from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def log_token_distribution(committee_id, amount, tx_hash):
    try:
        # DB 연결
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port="5432"
        )
        cursor = conn.cursor()

        # 현재 시각
        now = datetime.now()

        # 배분 이력 저장
        cursor.execute("""
            INSERT INTO token_distributions (
                committee_id,
                amount,
                tx_hash,
                created_at
            ) VALUES (%s, %s, %s, %s)
        """, (
            committee_id,
            amount,
            tx_hash,
            now
        ))

        conn.commit()
        print(f"[토큰 배분 기록 완료] 위원회 ID: {committee_id}, tx: {tx_hash}")

    except Exception as e:
        print(f"[토큰 배분 기록 실패] 에러: {str(e)}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
