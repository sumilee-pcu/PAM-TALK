# -*- coding: utf-8 -*-
"""
블록체인 초기 설정 및 배포 API
ASA 생성, 지갑 관리, 실제 블록체인 연동
"""
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import os
import json
import logging

from ..service.algorand_client import AlgorandClient
from ..utils.db_pool import get_db_connection

blockchain_setup_bp = Blueprint('blockchain_setup', __name__)
logger = logging.getLogger(__name__)

def async_route(f):
    """비동기 라우트 데코레이터"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__
    return wrapper

@blockchain_setup_bp.route('/setup/check-status', methods=['GET'])
@cross_origin()
def check_blockchain_status():
    """현재 블록체인 연동 상태 확인"""
    try:
        client = AlgorandClient()
        status = client.get_network_status()

        # PAM 토큰 정보 확인
        pam_token_info = client.check_pam_token_info()

        return jsonify({
            'success': True,
            'data': {
                'network_status': status,
                'pam_token_deployed': pam_token_info is not None,
                'pam_token_info': pam_token_info,
                'setup_required': not status['connected'] or not pam_token_info
            }
        })

    except Exception as e:
        logger.error(f"블록체인 상태 확인 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'network_status': {'connected': False},
                'pam_token_deployed': False,
                'setup_required': True
            }
        }), 500

@blockchain_setup_bp.route('/setup/create-admin-account', methods=['POST'])
@cross_origin()
def create_admin_account():
    """관리자 계정 생성 (최초 설정)"""
    try:
        client = AlgorandClient()

        # 새 계정 생성
        wallet_info = client.create_user_wallet()

        if not wallet_info:
            return jsonify({
                'success': False,
                'error': '계정 생성 실패'
            }), 500

        # 생성된 정보 반환 (실제 환경에서는 보안 고려 필요)
        return jsonify({
            'success': True,
            'data': {
                'address': wallet_info['address'],
                'mnemonic': wallet_info['mnemonic'],
                'instructions': [
                    f"1. 주소 {wallet_info['address']}를 복사하세요",
                    "2. https://testnet.algoexplorer.io/dispenser 에서 테스트넷 ALGO를 받으세요",
                    "3. 개인키를 환경변수 CREATOR_PRIVATE_KEY에 설정하세요",
                    "4. PAM 토큰 생성을 진행하세요"
                ]
            }
        })

    except Exception as e:
        logger.error(f"관리자 계정 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_setup_bp.route('/setup/create-pam-token', methods=['POST'])
@cross_origin()
def create_pam_token():
    """PAM-TALK ESG 토큰 생성 (ASA)"""
    try:
        client = AlgorandClient()

        # PAM 토큰 생성
        success, tx_hash, asset_id = client.create_pam_esg_token()

        if not success:
            return jsonify({
                'success': False,
                'error': tx_hash  # 오류 메시지
            }), 500

        # 성공적으로 생성된 경우
        response_data = {
            'success': True,
            'data': {
                'transaction_hash': tx_hash,
                'asset_id': asset_id,
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{tx_hash}",
                'asset_url': f"https://testnet.algoexplorer.io/asset/{asset_id}",
                'next_steps': [
                    f"ASA ID {asset_id}를 환경변수 PAM_TOKEN_ASA_ID에 설정하세요",
                    "이제 사용자들이 토큰을 받을 수 있습니다",
                    "테스트 토큰 전송을 해보세요"
                ]
            }
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"PAM 토큰 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_setup_bp.route('/setup/create-user-wallet', methods=['POST'])
@cross_origin()
def create_user_wallet():
    """새 사용자 지갑 생성"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        client = AlgorandClient()
        wallet_info = client.create_user_wallet()

        if not wallet_info:
            return jsonify({'success': False, 'error': '지갑 생성 실패'}), 500

        # 데이터베이스에 지갑 정보 저장
        conn = get_db_connection()
        cursor = conn.cursor()

        # 지갑 정보 저장 (개인키는 암호화 저장 권장)
        cursor.execute("""
            INSERT INTO user_wallets (user_id, wallet_address, encrypted_private_key, network)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                wallet_address = %s, updated_at = CURRENT_TIMESTAMP
        """, (
            user_id, wallet_info['address'], wallet_info['private_key'], 'testnet',
            wallet_info['address']
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # PAM 토큰 opt-in 수행
        if client.pam_token_id:
            opt_in_success, opt_in_tx = client.opt_in_to_asset(
                wallet_info['private_key'],
                int(client.pam_token_id)
            )

            if opt_in_success:
                logger.info(f"사용자 {user_id} PAM 토큰 opt-in 완료: {opt_in_tx}")

        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'wallet_address': wallet_info['address'],
                'mnemonic': wallet_info['mnemonic'],  # 실제로는 사용자에게만 1회 제공
                'opt_in_completed': opt_in_success if client.pam_token_id else False,
                'explorer_url': f"https://testnet.algoexplorer.io/address/{wallet_info['address']}"
            }
        })

    except Exception as e:
        logger.error(f"사용자 지갑 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_setup_bp.route('/setup/send-test-tokens', methods=['POST'])
@cross_origin()
def send_test_tokens():
    """테스트 토큰 전송"""
    try:
        data = request.get_json()
        recipient_address = data.get('recipient_address')
        amount = float(data.get('amount', 10.0))  # 기본 10 PAM
        note = data.get('note', 'Test token distribution')

        if not recipient_address:
            return jsonify({'success': False, 'error': 'recipient_address is required'}), 400

        client = AlgorandClient()

        # 토큰 전송 (소수점 3자리 변환: 10.0 PAM = 10000)
        amount_with_decimals = int(amount * 1000)
        success, tx_hash = client.transfer_tokens(
            recipient_address,
            amount_with_decimals,
            note
        )

        if not success:
            return jsonify({
                'success': False,
                'error': tx_hash  # 오류 메시지
            }), 500

        return jsonify({
            'success': True,
            'data': {
                'transaction_hash': tx_hash,
                'recipient': recipient_address,
                'amount_sent': amount,
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{tx_hash}",
                'recipient_explorer': f"https://testnet.algoexplorer.io/address/{recipient_address}"
            }
        })

    except Exception as e:
        logger.error(f"테스트 토큰 전송 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_setup_bp.route('/setup/verify-wallet/<wallet_address>', methods=['GET'])
@cross_origin()
def verify_wallet_balance(wallet_address):
    """지갑 잔액 및 상태 확인"""
    try:
        client = AlgorandClient()

        # 계정 정보 조회
        account_info = client.get_account_info(wallet_address)
        if not account_info:
            return jsonify({'success': False, 'error': '계정을 찾을 수 없음'}), 404

        # ALGO 잔액
        algo_balance = account_info['amount'] / 1000000  # microAlgos를 ALGO로 변환

        # PAM 토큰 잔액
        pam_balance = 0
        if client.pam_token_id:
            pam_balance = client.get_asset_balance(wallet_address, int(client.pam_token_id)) / 1000

        return jsonify({
            'success': True,
            'data': {
                'wallet_address': wallet_address,
                'algo_balance': algo_balance,
                'pam_balance': pam_balance,
                'assets_count': len(account_info.get('assets', [])),
                'explorer_url': f"https://testnet.algoexplorer.io/address/{wallet_address}",
                'status': 'active' if algo_balance > 0 else 'inactive'
            }
        })

    except Exception as e:
        logger.error(f"지갑 확인 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_setup_bp.route('/setup/integration-guide', methods=['GET'])
@cross_origin()
def get_integration_guide():
    """블록체인 연동 가이드"""
    return jsonify({
        'success': True,
        'data': {
            'title': 'PAM-TALK ESG Chain 블록체인 연동 가이드',
            'steps': [
                {
                    'step': 1,
                    'title': '관리자 계정 생성',
                    'endpoint': 'POST /api/blockchain-setup/setup/create-admin-account',
                    'description': '블록체인 관리용 계정을 생성합니다'
                },
                {
                    'step': 2,
                    'title': '테스트넷 ALGO 받기',
                    'url': 'https://testnet.algoexplorer.io/dispenser',
                    'description': '생성된 주소로 무료 테스트 ALGO를 받습니다'
                },
                {
                    'step': 3,
                    'title': 'PAM 토큰 생성',
                    'endpoint': 'POST /api/blockchain-setup/setup/create-pam-token',
                    'description': 'PAM-TALK ESG 토큰(ASA)을 블록체인에 생성합니다'
                },
                {
                    'step': 4,
                    'title': '환경변수 설정',
                    'variables': [
                        'CREATOR_PRIVATE_KEY=관리자계정개인키',
                        'PAM_TOKEN_ASA_ID=생성된ASA번호'
                    ],
                    'description': '생성된 정보를 환경변수에 설정합니다'
                },
                {
                    'step': 5,
                    'title': '사용자 지갑 생성 테스트',
                    'endpoint': 'POST /api/blockchain-setup/setup/create-user-wallet',
                    'description': '일반 사용자 지갑을 생성하고 opt-in합니다'
                },
                {
                    'step': 6,
                    'title': '토큰 전송 테스트',
                    'endpoint': 'POST /api/blockchain-setup/setup/send-test-tokens',
                    'description': '생성한 지갑으로 테스트 토큰을 전송합니다'
                }
            ],
            'required_packages': [
                'pip install py-algorand-sdk==2.6.0',
                'pip install algosdk'
            ],
            'testnet_resources': [
                'Algorand 테스트넷 Explorer: https://testnet.algoexplorer.io',
                'ALGO 무료 받기: https://testnet.algoexplorer.io/dispenser',
                'Algorand 지갑: https://wallet.myalgo.com'
            ]
        }
    })

# 테이블 생성 SQL (필요시)
CREATE_USER_WALLETS_TABLE = """
CREATE TABLE IF NOT EXISTS user_wallets (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL UNIQUE,
    wallet_address VARCHAR(58) NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    network VARCHAR(20) DEFAULT 'testnet',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_wallets_user_id ON user_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_user_wallets_address ON user_wallets(wallet_address);
"""