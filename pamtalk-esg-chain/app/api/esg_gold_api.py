# -*- coding: utf-8 -*-
"""
ESG-Gold API Endpoints
ESG-GOLD 디지털 쿠폰 시스템 REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Optional
from datetime import datetime
import json

from ..service.esg_gold_service import ESGGoldService
from ..service.esg_gold_conversion_module import ESGGoldConversionModule
from ..service.carbon_calculation_engine import (
    CarbonCalculationEngine,
    CarbonActivity,
    ActivityType
)

logger = logging.getLogger(__name__)

# Flask 앱 생성 (또는 기존 앱에 Blueprint 추가)
app = Flask(__name__)
CORS(app)

# 서비스 초기화 (실제로는 앱 설정에서 초기화)
esg_gold_service = None
conversion_module = None
carbon_engine = None


def init_esg_gold_api(esg_service: ESGGoldService,
                     conv_module: ESGGoldConversionModule,
                     c_engine: CarbonCalculationEngine):
    """API 초기화"""
    global esg_gold_service, conversion_module, carbon_engine
    esg_gold_service = esg_service
    conversion_module = conv_module
    carbon_engine = c_engine


# ============================================================================
# 1. 토큰 정보 및 잔액 조회
# ============================================================================

@app.route('/api/esg-gold/info', methods=['GET'])
def get_esg_gold_info():
    """
    ESG-GOLD 토큰 정보 조회

    Returns:
        {
            'asset_id': int,
            'name': str,
            'total_supply_dc': float,
            'creator': str,
            ...
        }
    """
    try:
        asset_info = esg_gold_service.get_asset_info()
        return jsonify({
            'success': True,
            'data': asset_info
        }), 200

    except Exception as e:
        logger.error(f"Failed to get ESG-GOLD info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/esg-gold/balance/<wallet_address>', methods=['GET'])
def get_balance(wallet_address: str):
    """
    지갑 주소의 ESG-GOLD 잔액 조회

    Args:
        wallet_address: Algorand 지갑 주소

    Returns:
        {
            'wallet_address': str,
            'balance_dc': float,
            'balance_micro': int,
            'opted_in': bool,
            'carbon_offset': {...}
        }
    """
    try:
        balance = esg_gold_service.get_balance(wallet_address)
        opted_in = esg_gold_service.has_opted_in(wallet_address)
        carbon_offset = esg_gold_service.calculate_carbon_offset(balance)

        return jsonify({
            'success': True,
            'data': {
                'wallet_address': wallet_address,
                'balance_dc': balance,
                'balance_micro': int(balance * 1_000_000),
                'opted_in': opted_in,
                'carbon_offset': carbon_offset
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get balance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 2. Opt-in 및 계정 관리
# ============================================================================

@app.route('/api/esg-gold/opt-in', methods=['POST'])
def opt_in():
    """
    ESG-GOLD 토큰 Opt-in

    Request Body:
        {
            'account_address': str,
            'account_private_key': str
        }

    Returns:
        {
            'success': bool,
            'tx_id': str,
            'block': int
        }
    """
    try:
        data = request.get_json()
        account_address = data.get('account_address')
        account_private_key = data.get('account_private_key')

        if not account_address or not account_private_key:
            return jsonify({
                'success': False,
                'error': 'account_address and account_private_key required'
            }), 400

        result = esg_gold_service.opt_in_esg_gold(
            account_address=account_address,
            account_private_key=account_private_key
        )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Opt-in failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 3. 탄소 감축 활동 및 ESG-GOLD 변환
# ============================================================================

@app.route('/api/esg-gold/activity/preview', methods=['POST'])
def preview_carbon_activity():
    """
    탄소 감축 활동 보상 미리보기

    Request Body:
        {
            'activity_type': str,
            'product_name': str,
            'quantity': float,
            'origin_region': str,
            'destination_region': str,
            'farming_method': str,
            'transport_method': str,
            'packaging_type': str
        }

    Returns:
        {
            'carbon_savings_kg': float,
            'dc_units': float,
            'esg_gold_amount': float,
            'pam_tokens': int,
            'breakdown': {...}
        }
    """
    try:
        data = request.get_json()

        # CarbonActivity 생성
        activity = CarbonActivity(
            activity_type=ActivityType(data['activity_type']),
            user_id='preview',
            product_name=data['product_name'],
            quantity=data['quantity'],
            origin_region=data['origin_region'],
            destination_region=data['destination_region'],
            farming_method=data['farming_method'],
            transport_method=data['transport_method'],
            packaging_type=data['packaging_type'],
            activity_date=datetime.now().isoformat()
        )

        # 보상 미리보기
        preview = conversion_module.calculate_reward_preview(activity)

        return jsonify({
            'success': True,
            'data': preview
        }), 200

    except Exception as e:
        logger.error(f"Preview failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/esg-gold/activity/submit', methods=['POST'])
def submit_carbon_activity():
    """
    탄소 감축 활동 제출 및 ESG-GOLD 자동 발행

    Request Body:
        {
            'user_id': str,
            'wallet_address': str,
            'activity_type': str,
            'product_name': str,
            'quantity': float,
            'origin_region': str,
            'destination_region': str,
            'farming_method': str,
            'transport_method': str,
            'packaging_type': str
        }

    Returns:
        {
            'success': bool,
            'carbon_savings_kg': float,
            'dc_units': float,
            'esg_gold_minted': float,
            'transaction_id': str
        }
    """
    try:
        data = request.get_json()

        # CarbonActivity 생성
        activity = CarbonActivity(
            activity_type=ActivityType(data['activity_type']),
            user_id=data['user_id'],
            product_name=data['product_name'],
            quantity=data['quantity'],
            origin_region=data['origin_region'],
            destination_region=data['destination_region'],
            farming_method=data['farming_method'],
            transport_method=data['transport_method'],
            packaging_type=data['packaging_type'],
            activity_date=datetime.now().isoformat()
        )

        # 활동 처리 및 ESG-GOLD 발행
        result = conversion_module.process_carbon_activity(
            activity=activity,
            user_wallet_address=data['wallet_address']
        )

        return jsonify({
            'success': result.success,
            'data': {
                'carbon_savings_kg': result.carbon_savings_kg,
                'dc_units': result.dc_units,
                'esg_gold_minted': result.esg_gold_minted,
                'pam_tokens_awarded': result.pam_tokens_awarded,
                'transaction_id': result.transaction_id,
                'timestamp': result.timestamp
            },
            'error': result.error
        }), 200 if result.success else 400

    except Exception as e:
        logger.error(f"Activity submission failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 4. ESG-GOLD 전송
# ============================================================================

@app.route('/api/esg-gold/transfer', methods=['POST'])
def transfer_esg_gold():
    """
    ESG-GOLD 전송

    Request Body:
        {
            'sender_address': str,
            'sender_private_key': str,
            'recipient_address': str,
            'amount_dc': float,
            'note': str (optional)
        }

    Returns:
        {
            'success': bool,
            'tx_id': str,
            'amount_dc': float
        }
    """
    try:
        data = request.get_json()

        result = esg_gold_service.transfer_esg_gold(
            sender_address=data['sender_address'],
            sender_private_key=data['sender_private_key'],
            recipient_address=data['recipient_address'],
            amount_dc=data['amount_dc'],
            note=data.get('note', '')
        )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 5. 마켓플레이스 할인 적용
# ============================================================================

@app.route('/api/esg-gold/marketplace/apply-discount', methods=['POST'])
def apply_marketplace_discount():
    """
    마켓플레이스에서 ESG-GOLD 할인 적용

    Request Body:
        {
            'user_wallet': str,
            'user_private_key': str,
            'esg_gold_amount': float,
            'purchase_amount': float,
            'order_id': str (optional)
        }

    Returns:
        {
            'success': bool,
            'discount_rate': float,
            'discount_amount': float,
            'final_amount': float,
            'esg_gold_burned': float,
            'burn_tx_id': str
        }
    """
    try:
        data = request.get_json()

        result = conversion_module.apply_marketplace_discount(
            user_wallet=data['user_wallet'],
            user_private_key=data['user_private_key'],
            esg_gold_amount=data['esg_gold_amount'],
            purchase_amount=data['purchase_amount']
        )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Discount application failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 6. 사용자 통계 및 내역
# ============================================================================

@app.route('/api/esg-gold/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id: str):
    """
    사용자 ESG-GOLD 통계 조회

    Query Parameters:
        days: int (default: 30) - 조회 기간

    Returns:
        {
            'total_conversions': int,
            'total_carbon_saved_kg': float,
            'total_dc_earned': float,
            'total_esg_gold': float,
            'total_pam_tokens': int
        }
    """
    try:
        days = request.args.get('days', 30, type=int)

        stats = conversion_module.get_user_conversion_stats(user_id, days)

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/esg-gold/user/<wallet_address>/transactions', methods=['GET'])
def get_user_transactions(wallet_address: str):
    """
    사용자 거래 내역 조회

    Query Parameters:
        limit: int (default: 100)

    Returns:
        {
            'transactions': [...]
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)

        transactions = esg_gold_service.get_transaction_history(
            account_address=wallet_address,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': {
                'wallet_address': wallet_address,
                'transactions': transactions,
                'count': len(transactions)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 7. ESG-GOLD 소각 (Burn)
# ============================================================================

@app.route('/api/esg-gold/burn', methods=['POST'])
def burn_esg_gold():
    """
    ESG-GOLD 영구 소각 (탄소 상쇄 증명)

    Request Body:
        {
            'owner_address': str,
            'owner_private_key': str,
            'amount_dc': float,
            'reason': str ('offset_retirement', 'marketplace_discount', etc.)
        }

    Returns:
        {
            'success': bool,
            'burned_dc': float,
            'carbon_offset_kg': float,
            'burn_tx_id': str
        }
    """
    try:
        data = request.get_json()

        result = esg_gold_service.burn_esg_gold(
            amount_dc=data['amount_dc'],
            owner_address=data['owner_address'],
            owner_private_key=data['owner_private_key'],
            reason=data.get('reason', 'offset_retirement')
        )

        if result['success']:
            # 탄소 상쇄 계산
            carbon_offset = esg_gold_service.calculate_carbon_offset(result['burned_dc'])
            result['carbon_offset'] = carbon_offset

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Burn failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 8. 시스템 통계
# ============================================================================

@app.route('/api/esg-gold/stats/global', methods=['GET'])
def get_global_stats():
    """
    전체 시스템 통계 조회

    Returns:
        {
            'total_users': int,
            'total_dc_minted': float,
            'total_dc_burned': float,
            'total_carbon_offset_kg': float,
            'circulating_supply': float
        }
    """
    try:
        # DB에서 통계 조회 (실제 구현 필요)
        # 여기서는 예시
        stats = {
            'total_users': 0,
            'total_dc_minted': 0.0,
            'total_dc_burned': 0.0,
            'total_carbon_offset_kg': 0.0,
            'circulating_supply': 0.0,
            'last_updated': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        logger.error(f"Failed to get global stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 9. Health Check
# ============================================================================

@app.route('/api/esg-gold/health', methods=['GET'])
def health_check():
    """
    API 상태 확인

    Returns:
        {
            'status': 'ok',
            'service': 'esg-gold-api',
            'timestamp': str
        }
    """
    return jsonify({
        'status': 'ok',
        'service': 'esg-gold-api',
        'timestamp': datetime.now().isoformat(),
        'esg_gold_service': esg_gold_service is not None,
        'conversion_module': conversion_module is not None
    }), 200


# ============================================================================
# 에러 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # 개발 모드로 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
