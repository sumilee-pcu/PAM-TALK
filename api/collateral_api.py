# -*- coding: utf-8 -*-
"""
Collateral & DC Minting API
ALGO 담보 예치 및 DC 토큰 발급 시스템 REST API
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import logging
import os
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, PaymentTxn, wait_for_confirmation
import requests

logger = logging.getLogger(__name__)

# Blueprint 생성
collateral_bp = Blueprint('collateral', __name__, url_prefix='/api/collateral')

# Algorand 설정
ALGOD_ADDRESS = os.getenv('ALGORAND_SERVER', 'https://testnet-api.algonode.cloud')
ALGOD_TOKEN = ''
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# 시스템 설정
ESG_GOLD_ASSET_ID = int(os.getenv('ESG_GOLD_ASSET_ID', '0'))
COLLATERAL_POOL_ADDRESS = os.getenv('COLLATERAL_POOL_ADDRESS', '')
RESERVE_MNEMONIC = os.getenv('RESERVE_MNEMONIC', '')
COLLATERAL_RATIO = 1000  # 1 ALGO = 1000 DC
MIN_COLLATERAL_AMOUNT = 10  # 최소 10 ALGO

# Supabase 설정 (실제로는 환경변수에서 로드)
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')


def get_supabase_headers():
    """Supabase API 헤더"""
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }


def verify_transaction(tx_id: str) -> Optional[Dict]:
    """
    알고랜드 트랜잭션 검증

    Args:
        tx_id: 트랜잭션 ID

    Returns:
        트랜잭션 정보 또는 None
    """
    try:
        tx_info = algod_client.pending_transaction_info(tx_id)
        if tx_info.get('confirmed-round', 0) > 0:
            return tx_info

        # 대기 중이면 확인 대기
        wait_for_confirmation(algod_client, tx_id, 4)
        return algod_client.pending_transaction_info(tx_id)
    except Exception as e:
        logger.error(f"Transaction verification failed: {e}")
        return None


def get_algo_price_usd() -> float:
    """
    ALGO 가격 조회 (USD)
    실제로는 가격 오라클에서 가져와야 함
    """
    try:
        # CoinGecko API 사용 예시
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'algorand', 'vs_currencies': 'usd'},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('algorand', {}).get('usd', 0.0)
    except Exception as e:
        logger.warning(f"Failed to fetch ALGO price: {e}")

    # 기본값 (fallback)
    return 0.20  # $0.20


# ============================================================================
# 1. 담보 예치 (Deposit Collateral)
# ============================================================================

@collateral_bp.route('/deposit', methods=['POST'])
def deposit_collateral():
    """
    담보 예치 기록

    Request Body:
        {
            'user_id': str (UUID),
            'user_address': str,
            'algo_amount': float,
            'deposit_tx_id': str
        }

    Returns:
        {
            'success': bool,
            'collateral_id': str,
            'dc_capacity': float,
            'algo_amount': float,
            'usd_value': float
        }
    """
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        user_address = data.get('user_address')
        algo_amount = float(data.get('algo_amount', 0))
        deposit_tx_id = data.get('deposit_tx_id')

        # 입력 검증
        if not all([user_id, user_address, algo_amount, deposit_tx_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        if algo_amount < MIN_COLLATERAL_AMOUNT:
            return jsonify({
                'success': False,
                'error': f'Minimum collateral is {MIN_COLLATERAL_AMOUNT} ALGO'
            }), 400

        # 트랜잭션 검증
        tx_info = verify_transaction(deposit_tx_id)
        if not tx_info:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or not confirmed'
            }), 400

        # ALGO 가격 조회
        algo_price = get_algo_price_usd()
        usd_value = algo_amount * algo_price
        dc_capacity = algo_amount * COLLATERAL_RATIO

        # Supabase에 저장
        deposit_data = {
            'user_id': user_id,
            'algo_amount': algo_amount,
            'usd_value': usd_value,
            'algo_price_at_deposit': algo_price,
            'dc_minting_capacity': dc_capacity,
            'dc_minted': 0,
            'collateral_ratio': COLLATERAL_RATIO,
            'status': 'active',
            'deposit_tx_id': deposit_tx_id,
            'deposit_block_round': tx_info.get('confirmed-round'),
            'deposited_at': datetime.utcnow().isoformat()
        }

        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            json=deposit_data
        )

        if response.status_code not in [200, 201]:
            logger.error(f"Database insert failed: {response.text}")
            return jsonify({
                'success': False,
                'error': 'Failed to record deposit'
            }), 500

        result = response.json()
        collateral_id = result[0]['id'] if isinstance(result, list) else result['id']

        logger.info(f"Collateral deposit recorded: {collateral_id}, {algo_amount} ALGO")

        return jsonify({
            'success': True,
            'collateral_id': collateral_id,
            'dc_capacity': dc_capacity,
            'algo_amount': algo_amount,
            'usd_value': usd_value,
            'collateral_ratio': COLLATERAL_RATIO
        }), 200

    except Exception as e:
        logger.error(f"Deposit collateral error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 2. DC 토큰 발급 (Mint DC)
# ============================================================================

@collateral_bp.route('/mint-dc', methods=['POST'])
def mint_dc():
    """
    DC 토큰 발급 (RESERVE 계정에서 사용자로 전송)

    Request Body:
        {
            'userAddress': str,
            'collateralId': str (UUID),
            'dcAmount': float
        }

    Returns:
        {
            'success': bool,
            'minting_tx_id': str,
            'dc_minted': float,
            'fee_amount': float,
            'net_dc_amount': float
        }
    """
    try:
        data = request.get_json()

        user_address = data.get('userAddress')
        collateral_id = data.get('collateralId')
        dc_amount = float(data.get('dcAmount', 0))

        # 입력 검증
        if not all([user_address, collateral_id, dc_amount]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        if dc_amount <= 0:
            return jsonify({
                'success': False,
                'error': 'DC amount must be positive'
            }), 400

        # 담보 정보 조회
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            params={'id': f'eq.{collateral_id}', 'select': '*'}
        )

        if response.status_code != 200 or not response.json():
            return jsonify({
                'success': False,
                'error': 'Collateral not found'
            }), 404

        collateral = response.json()[0]

        # 담보 용량 확인
        dc_available = float(collateral['dc_minting_capacity']) - float(collateral['dc_minted'])
        if dc_amount > dc_available:
            return jsonify({
                'success': False,
                'error': f'Insufficient DC capacity. Available: {dc_available} DC'
            }), 400

        # 수수료 계산 (0.1%)
        fee_amount = dc_amount * 0.001
        net_dc_amount = dc_amount - fee_amount

        # RESERVE 계정에서 DC 전송
        if not RESERVE_MNEMONIC:
            return jsonify({
                'success': False,
                'error': 'RESERVE account not configured'
            }), 500

        reserve_account = mnemonic.mnemonicToSecretKey(RESERVE_MNEMONIC)
        params = algod_client.suggested_params()

        # DC 토큰 전송 트랜잭션
        txn = AssetTransferTxn(
            sender=reserve_account.addr,
            sp=params,
            receiver=user_address,
            amt=int(net_dc_amount * 1_000_000),  # microDC
            index=ESG_GOLD_ASSET_ID,
            note=f"DC minting: {collateral_id}".encode()
        )

        signed_txn = txn.sign(reserve_account.sk)
        tx_id = algod_client.send_transaction(signed_txn)

        # 트랜잭션 확인 대기
        wait_for_confirmation(algod_client, tx_id, 4)
        tx_info = algod_client.pending_transaction_info(tx_id)

        # 데이터베이스 업데이트
        # 1. collateral_deposits 업데이트
        new_dc_minted = float(collateral['dc_minted']) + dc_amount
        update_response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            params={'id': f'eq.{collateral_id}'},
            json={
                'dc_minted': new_dc_minted,
                'last_minted_at': datetime.utcnow().isoformat()
            }
        )

        if update_response.status_code not in [200, 204]:
            logger.error(f"Failed to update collateral: {update_response.text}")

        # 2. dc_minting_records 생성
        minting_record = {
            'user_id': collateral['user_id'],
            'collateral_id': collateral_id,
            'dc_amount': dc_amount,
            'fee_amount': fee_amount,
            'net_dc_amount': net_dc_amount,
            'algo_collateral_used': dc_amount / COLLATERAL_RATIO,
            'minting_tx_id': tx_id,
            'minting_block_round': tx_info.get('confirmed-round'),
            'status': 'completed',
            'minted_at': datetime.utcnow().isoformat()
        }

        requests.post(
            f'{SUPABASE_URL}/rest/v1/dc_minting_records',
            headers=get_supabase_headers(),
            json=minting_record
        )

        logger.info(f"DC minted: {net_dc_amount} DC to {user_address}")

        return jsonify({
            'success': True,
            'minting_tx_id': tx_id,
            'dc_minted': dc_amount,
            'fee_amount': fee_amount,
            'net_dc_amount': net_dc_amount,
            'explorer_url': f'https://testnet.algoexplorer.io/tx/{tx_id}'
        }), 200

    except Exception as e:
        logger.error(f"Mint DC error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 3. 담보 상환 (Redeem Collateral)
# ============================================================================

@collateral_bp.route('/redeem', methods=['POST'])
def redeem_collateral():
    """
    담보 상환 (DC 소각 후 ALGO 반환)

    Request Body:
        {
            'userAddress': str,
            'collateralId': str (UUID),
            'dcAmount': float,
            'burnTxId': str
        }

    Returns:
        {
            'success': bool,
            'returnTxId': str,
            'algoReturned': float,
            'feeAmount': float,
            'netAlgoReturned': float
        }
    """
    try:
        data = request.get_json()

        user_address = data.get('userAddress')
        collateral_id = data.get('collateralId')
        dc_amount = float(data.get('dcAmount', 0))
        burn_tx_id = data.get('burnTxId')

        # 입력 검증
        if not all([user_address, collateral_id, dc_amount, burn_tx_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # DC 소각 트랜잭션 검증
        tx_info = verify_transaction(burn_tx_id)
        if not tx_info:
            return jsonify({
                'success': False,
                'error': 'Burn transaction not confirmed'
            }), 400

        # 담보 정보 조회
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            params={'id': f'eq.{collateral_id}', 'select': '*'}
        )

        if response.status_code != 200 or not response.json():
            return jsonify({
                'success': False,
                'error': 'Collateral not found'
            }), 404

        collateral = response.json()[0]

        # DC 소각 가능 여부 확인
        if dc_amount > float(collateral['dc_minted']):
            return jsonify({
                'success': False,
                'error': 'Cannot burn more DC than minted'
            }), 400

        # 반환할 ALGO 계산
        algo_to_return = dc_amount / COLLATERAL_RATIO
        fee_amount = algo_to_return * 0.005  # 0.5% 수수료
        net_algo_returned = algo_to_return - fee_amount

        # COLLATERAL_POOL에서 사용자에게 ALGO 반환
        if not RESERVE_MNEMONIC:
            return jsonify({
                'success': False,
                'error': 'RESERVE account not configured'
            }), 500

        reserve_account = mnemonic.mnemonicToSecretKey(RESERVE_MNEMONIC)
        params = algod_client.suggested_params()

        # ALGO 반환 트랜잭션
        txn = PaymentTxn(
            sender=reserve_account.addr,
            sp=params,
            receiver=user_address,
            amt=int(net_algo_returned * 1_000_000),  # microALGO
            note=f"Collateral redemption: {collateral_id}".encode()
        )

        signed_txn = txn.sign(reserve_account.sk)
        return_tx_id = algod_client.send_transaction(signed_txn)

        # 트랜잭션 확인 대기
        wait_for_confirmation(algod_client, return_tx_id, 4)
        return_tx_info = algod_client.pending_transaction_info(return_tx_id)

        # 데이터베이스 업데이트
        # 1. collateral_deposits 업데이트
        new_dc_minted = float(collateral['dc_minted']) - dc_amount
        new_status = 'fully_redeemed' if new_dc_minted == 0 else 'partial_redeemed'

        update_response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            params={'id': f'eq.{collateral_id}'},
            json={
                'dc_minted': new_dc_minted,
                'status': new_status,
                'redeemed_at': datetime.utcnow().isoformat() if new_dc_minted == 0 else None
            }
        )

        if update_response.status_code not in [200, 204]:
            logger.error(f"Failed to update collateral: {update_response.text}")

        # 2. collateral_redemptions 생성
        redemption_record = {
            'user_id': collateral['user_id'],
            'collateral_id': collateral_id,
            'dc_burned': dc_amount,
            'algo_returned': algo_to_return,
            'fee_amount': fee_amount,
            'net_algo_returned': net_algo_returned,
            'burn_tx_id': burn_tx_id,
            'return_tx_id': return_tx_id,
            'burn_block_round': tx_info.get('confirmed-round'),
            'return_block_round': return_tx_info.get('confirmed-round'),
            'status': 'completed',
            'redeemed_at': datetime.utcnow().isoformat()
        }

        requests.post(
            f'{SUPABASE_URL}/rest/v1/collateral_redemptions',
            headers=get_supabase_headers(),
            json=redemption_record
        )

        logger.info(f"Collateral redeemed: {net_algo_returned} ALGO to {user_address}")

        return jsonify({
            'success': True,
            'returnTxId': return_tx_id,
            'algoReturned': algo_to_return,
            'feeAmount': fee_amount,
            'netAlgoReturned': net_algo_returned,
            'explorer_url': f'https://testnet.algoexplorer.io/tx/{return_tx_id}'
        }), 200

    except Exception as e:
        logger.error(f"Redeem collateral error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 4. 담보 상태 조회 (Get Collateral Status)
# ============================================================================

@collateral_bp.route('/status/<user_address>', methods=['GET'])
def get_collateral_status(user_address: str):
    """
    사용자의 담보 상태 조회

    Returns:
        {
            'success': bool,
            'collaterals': [{
                'id': str,
                'algo_amount': float,
                'dc_capacity': float,
                'dc_minted': float,
                'dc_available': float,
                'status': str,
                'deposited_at': str
            }]
        }
    """
    try:
        # 사용자 ID로 user_id 조회 (실제로는 주소로 조회 가능하도록 수정 필요)
        # 여기서는 간단히 주소를 user_id로 사용
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/collateral_deposits',
            headers=get_supabase_headers(),
            params={
                'select': '*',
                'order': 'deposited_at.desc'
            }
        )

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch collateral status'
            }), 500

        collaterals = response.json()

        # 결과 포맷팅
        result = []
        for c in collaterals:
            result.append({
                'id': c['id'],
                'algo_amount': float(c['algo_amount']),
                'dc_capacity': float(c['dc_minting_capacity']),
                'dc_minted': float(c['dc_minted']),
                'dc_available': float(c['dc_minting_capacity']) - float(c['dc_minted']),
                'status': c['status'],
                'deposited_at': c['deposited_at'],
                'collateral_ratio': c['collateral_ratio']
            })

        return jsonify({
            'success': True,
            'collaterals': result
        }), 200

    except Exception as e:
        logger.error(f"Get collateral status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 5. Health Check
# ============================================================================

@collateral_bp.route('/health', methods=['GET'])
def health_check():
    """
    API 상태 확인

    Returns:
        {
            'status': str,
            'service': str,
            'esg_gold_asset_id': int,
            'collateral_pool_configured': bool
        }
    """
    return jsonify({
        'status': 'ok',
        'service': 'collateral-api',
        'timestamp': datetime.utcnow().isoformat(),
        'esg_gold_asset_id': ESG_GOLD_ASSET_ID,
        'collateral_pool_configured': bool(COLLATERAL_POOL_ADDRESS),
        'reserve_configured': bool(RESERVE_MNEMONIC)
    }), 200


# ============================================================================
# Flask App (standalone mode)
# ============================================================================

if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(collateral_bp)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Collateral & DC Minting API Server")
    logger.info(f"ESG-GOLD Asset ID: {ESG_GOLD_ASSET_ID}")
    logger.info(f"Collateral Pool: {COLLATERAL_POOL_ADDRESS}")

    app.run(debug=True, host='0.0.0.0', port=5001)
