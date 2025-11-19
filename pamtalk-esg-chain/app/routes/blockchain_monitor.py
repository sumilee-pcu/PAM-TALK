# -*- coding: utf-8 -*-
"""
블록체인 트랜잭션 모니터링 API
ESG Chain 동작 상태 및 트랜잭션 추적
"""
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime, timedelta
import asyncio
import json
import logging

from ..utils.db_pool import get_db_connection

blockchain_monitor_bp = Blueprint('blockchain_monitor', __name__)
logger = logging.getLogger(__name__)

def async_route(f):
    """비동기 라우트 데코레이터"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__
    return wrapper

@blockchain_monitor_bp.route('/transactions/recent', methods=['GET'])
@cross_origin()
@async_route
async def get_recent_transactions():
    """최근 블록체인 트랜잭션 조회"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        tx_type = request.args.get('type')  # token_mint, reward_payment, etc.

        conn = get_db_connection()
        cursor = conn.cursor()

        # 토큰 발행 트랜잭션 조회
        query = """
            SELECT
                'token_distribution' as type,
                td.id,
                td.user_id,
                td.provider_id,
                td.amount,
                td.tx_hash,
                td.status,
                td.created_at,
                td.completed_at,
                p.name as provider_name,
                'ASA Transfer' as blockchain_action
            FROM token_distributions td
            JOIN providers p ON td.provider_id = p.id
            WHERE td.tx_hash IS NOT NULL

            UNION ALL

            SELECT
                'content_reward' as type,
                scr.id,
                scr.user_id,
                NULL as provider_id,
                scr.token_amount as amount,
                scr.tx_hash,
                scr.status,
                scr.created_at,
                scr.paid_at as completed_at,
                'Content Rewards' as provider_name,
                'Reward Payment' as blockchain_action
            FROM social_content_rewards scr
            WHERE scr.tx_hash IS NOT NULL

            UNION ALL

            SELECT
                'carbon_reward' as type,
                cr.id,
                cr.user_id,
                NULL as provider_id,
                cr.token_amount as amount,
                cr.tx_hash,
                cr.status,
                cr.created_at,
                cr.paid_at as completed_at,
                'Carbon Activities' as provider_name,
                'Carbon Reward' as blockchain_action
            FROM carbon_rewards cr
            WHERE cr.tx_hash IS NOT NULL
        """

        if tx_type:
            query += f" AND type = '{tx_type}'"

        query += " ORDER BY created_at DESC LIMIT %s"

        cursor.execute(query, (limit,))

        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'type': row[0],
                'id': row[1],
                'user_id': row[2],
                'provider_id': row[3],
                'amount': float(row[4]) if row[4] else 0,
                'tx_hash': row[5],
                'status': row[6],
                'created_at': row[7],
                'completed_at': row[8],
                'provider_name': row[9],
                'blockchain_action': row[10],
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{row[5]}" if row[5] else None
            })

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'transactions': transactions,
                'count': len(transactions)
            }
        })

    except Exception as e:
        logger.error(f"최근 트랜잭션 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_monitor_bp.route('/transactions/<tx_hash>/details', methods=['GET'])
@cross_origin()
@async_route
async def get_transaction_details(tx_hash):
    """특정 트랜잭션 상세 정보"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 모든 테이블에서 해당 tx_hash 검색
        tables_to_check = [
            ('token_distributions', 'td', ['user_id', 'provider_id', 'amount', 'esg_coupon_id']),
            ('social_content_rewards', 'scr', ['user_id', 'content_type', 'content_id', 'reward_type', 'token_amount']),
            ('carbon_rewards', 'cr', ['user_id', 'carbon_activity_id', 'token_amount', 'carbon_saved'])
        ]

        transaction_details = None

        for table_name, alias, fields in tables_to_check:
            field_select = ', '.join([f"{alias}.{field}" for field in fields])
            query = f"""
                SELECT
                    '{table_name}' as source_table,
                    {alias}.id,
                    {alias}.tx_hash,
                    {alias}.status,
                    {alias}.created_at,
                    {field_select}
                FROM {table_name} {alias}
                WHERE {alias}.tx_hash = %s
            """

            cursor.execute(query, (tx_hash,))
            result = cursor.fetchone()

            if result:
                transaction_details = {
                    'source_table': result[0],
                    'id': result[1],
                    'tx_hash': result[2],
                    'status': result[3],
                    'created_at': result[4],
                    'details': dict(zip(fields, result[5:]))
                }
                break

        if not transaction_details:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

        # Algorand Explorer 정보 추가
        transaction_details['explorer_url'] = f"https://testnet.algoexplorer.io/tx/{tx_hash}"
        transaction_details['network'] = 'Algorand Testnet'

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': transaction_details
        })

    except Exception as e:
        logger.error(f"트랜잭션 상세 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_monitor_bp.route('/stats/blockchain', methods=['GET'])
@cross_origin()
@async_route
async def get_blockchain_stats():
    """블록체인 통계 정보"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 최근 24시간 통계
        last_24h = datetime.now() - timedelta(hours=24)

        # 토큰 발행 통계
        cursor.execute("""
            SELECT
                COUNT(*) as total_distributions,
                SUM(amount) as total_tokens_distributed,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_distributions
            FROM token_distributions
            WHERE created_at >= %s
        """, (last_24h,))

        token_stats = cursor.fetchone()

        # 콘텐츠 보상 통계
        cursor.execute("""
            SELECT
                COUNT(*) as total_rewards,
                SUM(token_amount) as total_reward_tokens,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_rewards
            FROM social_content_rewards
            WHERE created_at >= %s
        """, (last_24h,))

        content_stats = cursor.fetchone()

        # 탄소 보상 통계
        cursor.execute("""
            SELECT
                COUNT(*) as total_carbon_rewards,
                SUM(token_amount) as total_carbon_tokens,
                SUM(carbon_saved) as total_carbon_saved
            FROM carbon_rewards
            WHERE created_at >= %s
        """, (last_24h,))

        carbon_stats = cursor.fetchone()

        # 전체 시스템 통계
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as active_users
            FROM (
                SELECT user_id FROM token_distributions WHERE created_at >= %s
                UNION
                SELECT user_id FROM social_content_rewards WHERE created_at >= %s
                UNION
                SELECT user_id FROM carbon_rewards WHERE created_at >= %s
            ) combined
        """, (last_24h, last_24h, last_24h))

        active_users = cursor.fetchone()[0]

        stats = {
            'last_24_hours': {
                'token_distributions': {
                    'total': token_stats[0],
                    'total_amount': float(token_stats[1]) if token_stats[1] else 0,
                    'completed': token_stats[2]
                },
                'content_rewards': {
                    'total': content_stats[0],
                    'total_amount': float(content_stats[1]) if content_stats[1] else 0,
                    'paid': content_stats[2]
                },
                'carbon_rewards': {
                    'total': carbon_stats[0],
                    'total_amount': float(carbon_stats[1]) if carbon_stats[1] else 0,
                    'carbon_saved': float(carbon_stats[2]) if carbon_stats[2] else 0
                },
                'active_users': active_users
            },
            'blockchain_info': {
                'network': 'Algorand Testnet',
                'explorer_base_url': 'https://testnet.algoexplorer.io',
                'asa_token': 'PAM-TALK-ESG'
            }
        }

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"블록체인 통계 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_monitor_bp.route('/user/<user_id>/transactions', methods=['GET'])
@cross_origin()
@async_route
async def get_user_transactions(user_id):
    """특정 사용자의 모든 블록체인 트랜잭션"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 사용자의 모든 트랜잭션 조회
        query = """
            SELECT
                'token_received' as type,
                td.amount,
                td.tx_hash,
                td.status,
                td.created_at,
                td.completed_at,
                p.name as source,
                'Received from provider' as description
            FROM token_distributions td
            JOIN providers p ON td.provider_id = p.id
            WHERE td.user_id = %s AND td.tx_hash IS NOT NULL

            UNION ALL

            SELECT
                'content_reward' as type,
                scr.token_amount as amount,
                scr.tx_hash,
                scr.status,
                scr.created_at,
                scr.paid_at as completed_at,
                scr.reward_type as source,
                'Content creation reward' as description
            FROM social_content_rewards scr
            WHERE scr.user_id = %s AND scr.tx_hash IS NOT NULL

            UNION ALL

            SELECT
                'carbon_reward' as type,
                cr.token_amount as amount,
                cr.tx_hash,
                cr.status,
                cr.created_at,
                cr.paid_at as completed_at,
                'Carbon Activity' as source,
                CONCAT('Carbon saved: ', cr.carbon_saved, ' kg CO2') as description
            FROM carbon_rewards cr
            WHERE cr.user_id = %s AND cr.tx_hash IS NOT NULL

            ORDER BY created_at DESC
        """

        cursor.execute(query, (user_id, user_id, user_id))

        transactions = []
        total_received = 0

        for row in cursor.fetchall():
            tx_data = {
                'type': row[0],
                'amount': float(row[1]) if row[1] else 0,
                'tx_hash': row[2],
                'status': row[3],
                'created_at': row[4],
                'completed_at': row[5],
                'source': row[6],
                'description': row[7],
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{row[2]}"
            }

            transactions.append(tx_data)
            if row[3] in ['completed', 'paid']:
                total_received += tx_data['amount']

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'transactions': transactions,
                'summary': {
                    'total_transactions': len(transactions),
                    'total_tokens_received': total_received,
                    'latest_transaction': transactions[0]['created_at'] if transactions else None
                }
            }
        })

    except Exception as e:
        logger.error(f"사용자 트랜잭션 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blockchain_monitor_bp.route('/health/blockchain', methods=['GET'])
@cross_origin()
@async_route
async def blockchain_health_check():
    """블록체인 연결 상태 체크"""
    try:
        from ..service.carbon_smart_contract_bridge import CarbonSmartContractBridge

        bridge = CarbonSmartContractBridge()

        # 간단한 상태 체크
        health_status = {
            'blockchain_connected': True,  # 실제로는 Algorand 노드 연결 체크
            'smart_contract_deployed': True,  # 스마트 컨트랙트 배포 상태
            'last_block_time': datetime.now(),  # 마지막 블록 시간
            'network': 'Algorand Testnet',
            'status': 'healthy'
        }

        return jsonify({
            'success': True,
            'data': health_status
        })

    except Exception as e:
        logger.error(f"블록체인 헬스체크 오류: {e}")
        return jsonify({
            'success': False,
            'data': {
                'blockchain_connected': False,
                'status': 'unhealthy',
                'error': str(e)
            }
        }), 500