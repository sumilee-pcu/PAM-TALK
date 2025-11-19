# -*- coding: utf-8 -*-
# app/service/token_routes.py

from flask import Blueprint, request, jsonify, current_app
from app.service.coupon_service import create_initial_coupons
from app.service.token_service import transfer_committee_token
from app.service.token_service import transfer_provider_token
from app.service.token_service import transfer_consumer_token
import os
from dotenv import load_dotenv

# .env 파일 로드
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

ASA_ID = int(os.getenv("ASA_ID"))
ASSET_NAME = os.getenv("ASA_NAME", "Pamtalk ESG Asset")  # 기본 자산 이름

# Flask Blueprint 설정
token_routes = Blueprint("token_routes", __name__)

# 토큰 발행 엔드포인트
@token_routes.route("/mint", methods=["POST"])
def mint_token_route():
    try:
        # JSON 요청 파싱
        body = request.get_json()
        print("[INFO] 요청 body:", body)

        amount = int(body.get("amount", 0))
        description = body.get("description", "").strip()
        unit_name = body.get("unit_name", "").strip().upper()

        # 발행자 정보 (로그인된 사용자로 대체 가능)
        issued_by = "admin@hcf.com"

        # 수량 유효성 검사
        if amount <= 0:
            return jsonify({
                "success": False,
                "message": "수량은 1 이상이어야 합니다."
            }), 400

        # 쿠폰 생성 함수 호출
        create_initial_coupons(
            amount=amount,
            description=description or f"{unit_name} 쿠폰 발행",
            issued_by=issued_by,
            asset_id=ASA_ID,
            asset_name=ASSET_NAME,
            unit_name=unit_name  # 단지 접두어로만 사용됨
        )

        return jsonify({
            "success": True,
            "message": f"{amount}개의 쿠폰({unit_name})을 발행했습니다.",
            "unit_name": unit_name,
            "asset_id": ASA_ID,
            "asset_name": ASSET_NAME,
            "amount": amount
        }), 200

    except Exception as e:
        print("[ERROR] 쿠폰 발행 중 오류:", e)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@token_routes.route('/transfer-committee', methods=['POST'])
def token_transfer_committee():
    data = request.get_json()
    committee_id = data.get('committee_id')
    amount = data.get('amount')

    if not committee_id or not amount:
        return jsonify({'error': 'Missing committee_id or amount'}), 400

    try:
        print(f"[요청 수신] committee_id: {committee_id}, amount: {amount}")
        tx_id = transfer_committee_token(committee_id, int(amount))
        return jsonify({'txId': tx_id}), 200
    except Exception as e:
        current_app.logger.exception("토큰 전송 중 오류 발생")
        return jsonify({'error': f'[토큰 전송 실패] 에러: {str(e)}'}), 500

@token_routes.route('/transfer-provider', methods=['POST'])
def token_transfer_provider():
    data = request.get_json()
    provider_id = data.get('provider_id')
    amount = data.get('amount')

    if not provider_id or not amount:
        return jsonify({'error': 'Missing provider_id or amount'}), 400

    try:
        print(f"[요청 수신] provider_id: {provider_id}, amount: {amount}")
        tx_id = transfer_provider_token(provider_id, int(amount))
        return jsonify({'txId': tx_id}), 200
    except Exception as e:
        current_app.logger.exception("토큰 전송 중 오류 발생")
        return jsonify({'error': f'[토큰 전송 실패] 에러: {str(e)}'}), 500

@token_routes.route('/transfer-consumer', methods=['POST'])
def token_transfer_consumer():
    data = request.get_json()
    consumer_id = data.get('consumer_id')
    amount = data.get('amount')

    if not consumer_id or not amount:
        return jsonify({'error': 'Missing provider_id or amount'}), 400

    try:
        print(f"[요청 수신] consumer_id: {consumer_id}, amount: {amount}")
        tx_id = transfer_consumer_token(consumer_id, int(amount))
        return jsonify({'txId': tx_id}), 200
    except Exception as e:
        current_app.logger.exception("토큰 전송 중 오류 발생")
        return jsonify({'error': f'[토큰 전송 실패] 에러: {str(e)}'}), 500