# -*- coding: utf-8 -*-
# test_db_connection.py
from app.service.coupon_service import create_initial_coupons

if __name__ == "__main__":
    print("DB 연결 테스트 시작...")
    asset_id = 99999999  # 임시 ASA ID (적당히 아무 숫자 넣자)
    total = 10           # 10개만 생성해서 삽입
    create_initial_coupons(asset_id, total)
    print("DB 삽입 테스트 완료!")