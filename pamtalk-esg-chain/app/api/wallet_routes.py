# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from algosdk import account, mnemonic

wallet_routes = Blueprint('wallet_routes', __name__)

@wallet_routes.route("/create", methods=["POST"])
def create_wallet():
    try:
        # 1. 새 계정 생성
        private_key, wallet_address = account.generate_account()

        # 2. 니모닉 추출 (지갑 복구용)
        wallet_mnemonic = mnemonic.from_private_key(private_key)

        print(f"지갑주소: {wallet_address}")
        print(f"니모닉: {wallet_mnemonic}")

        # 3. 결과 반환
        return jsonify({
            "success": True,
            "wallet_address": wallet_address,
            "wallet_mnemonic": wallet_mnemonic,
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
