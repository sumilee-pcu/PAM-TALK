#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PAM 디지털 쿠폰 API 서버 (Flask)"""

import sys
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# 상위 디렉토리의 모듈 import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from token_creation_api import AlgorandTokenAPI

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱
app = Flask(__name__)
CORS(app)

# 설정
API_BASE = "https://mainnet-api.algonode.cloud/v2"
PAM_POINT_ASSET_ID = 3330375002

# 마스터 계정 로드
account_file = os.path.join(os.path.dirname(__file__), '..', 'pam_mainnet_account_20251116_181939.json')
with open(account_file, 'r') as f:
    account_data = json.load(f)

token_api = AlgorandTokenAPI(account_data['mnemonic'])

def check_opt_in(user_address, asset_id):
    try:
        url = f"{API_BASE}/accounts/{user_address}"
        headers = {'User-Agent': 'PAM-Token-API/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False
        data = response.json()
        assets = data.get('assets', [])
        for asset in assets:
            if asset['asset-id'] == asset_id:
                return True
        return False
    except:
        return False

def validate_algorand_address(address):
    return address and len(address) == 58

@app.route('/')
def index():
    return jsonify({
        'name': 'PAM Digital Coupon API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/token-info')
def token_info():
    return jsonify({
        'asset_id': PAM_POINT_ASSET_ID,
        'asset_name': 'PAM-POINT',
        'unit_name': 'PAMP',
        'total_supply': 1000000000,
        'decimals': 2,
        'explorer_url': f'https://algoexplorer.io/asset/{PAM_POINT_ASSET_ID}'
    })

@app.route('/api/balance')
def check_balance():
    try:
        balance = token_api._check_balance()
        return jsonify({'success': True, 'balance_algo': balance})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-opt-in', methods=['POST'])
def check_user_opt_in():
    try:
        data = request.get_json()
        user_address = data.get('user_address')
        if not validate_algorand_address(user_address):
            return jsonify({'success': False, 'error': 'Invalid address'}), 400
        opted_in = check_opt_in(user_address, PAM_POINT_ASSET_ID)
        return jsonify({
            'success': True,
            'opted_in': opted_in,
            'asset_id': PAM_POINT_ASSET_ID
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/give-coupon', methods=['POST'])
def give_coupon():
    try:
        data = request.get_json()
        user_address = data.get('user_address')
        amount = data.get('amount')
        
        if not user_address or amount is None:
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
        if not validate_algorand_address(user_address):
            return jsonify({'success': False, 'error': 'Invalid address'}), 400
        
        if not isinstance(amount, int) or amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid amount'}), 400
        
        if not check_opt_in(user_address, PAM_POINT_ASSET_ID):
            return jsonify({
                'success': False,
                'error': 'NOT_OPTED_IN',
                'message': 'User must opt-in first',
                'asset_id': PAM_POINT_ASSET_ID
            }), 400
        
        logger.info(f"Giving {amount} to {user_address}")
        
        result = token_api.transfer_token(
            asset_id=PAM_POINT_ASSET_ID,
            recipient_address=user_address,
            amount=amount
        )
        
        if result['success']:
            logger.info(f"Success: {result['txid']}")
            return jsonify({
                'success': True,
                'txid': result['txid'],
                'asset_id': PAM_POINT_ASSET_ID,
                'amount': amount,
                'amount_display': f"{amount / 100:.2f}",
                'explorer_url': f"https://algoexplorer.io/tx/{result['txid']}"
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = 5000
    logger.info("PAM Digital Coupon API Server")
    logger.info(f"Asset ID: {PAM_POINT_ASSET_ID}")
    logger.info(f"Port: {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
