# -*- coding: utf-8 -*-
"""
탄소 추적 및 보상 API 라우트
탄소 활동 기록, 통계 조회, 챌린지 관리 등을 위한 REST API
"""

import json
from flask import Blueprint, request, jsonify
from datetime import datetime, date

from app.service.carbon_tracking_service import carbon_tracking_service
from app.service.carbon_reward_trigger import carbon_reward_trigger

# Flask Blueprint 설정
carbon_routes = Blueprint("carbon_routes", __name__)


@carbon_routes.route("/profile", methods=["POST"])
def create_carbon_profile():
    """탄소 프로필 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['user_id', 'email', 'name', 'region']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"필수 필드가 누락되었습니다: {field}"
                }), 400

        # 프로필 생성
        profile_id = carbon_tracking_service.create_carbon_profile(
            user_id=data['user_id'],
            email=data['email'],
            name=data['name'],
            region=data['region'],
            household_size=data.get('household_size', 1),
            lifestyle_type=data.get('lifestyle_type', 'standard'),
            preferred_transport=data.get('preferred_transport', 'mixed'),
            carbon_reduction_goal=data.get('carbon_reduction_goal', 10.0),
            monthly_token_goal=data.get('monthly_token_goal', 100)
        )

        return jsonify({
            "success": True,
            "message": "탄소 프로필이 생성되었습니다.",
            "profile_id": profile_id,
            "user_id": data['user_id']
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"프로필 생성 실패: {str(e)}"
        }), 500


@carbon_routes.route("/profile/<user_id>", methods=["GET"])
def get_carbon_profile(user_id):
    """탄소 프로필 조회 API"""
    try:
        profile = carbon_tracking_service.get_user_carbon_profile(user_id)

        if not profile:
            return jsonify({
                "success": False,
                "message": "사용자 프로필을 찾을 수 없습니다."
            }), 404

        return jsonify({
            "success": True,
            "profile": profile
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"프로필 조회 실패: {str(e)}"
        }), 500


@carbon_routes.route("/activity", methods=["POST"])
def record_carbon_activity():
    """탄소 활동 기록 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['user_id', 'activity_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"필수 필드가 누락되었습니다: {field}"
                }), 400

        # 활동 기록
        activity_id = carbon_tracking_service.record_carbon_activity(
            user_id=data['user_id'],
            activity_data=data
        )

        return jsonify({
            "success": True,
            "message": "탄소 활동이 기록되었습니다.",
            "activity_id": activity_id,
            "user_id": data['user_id']
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"활동 기록 실패: {str(e)}"
        }), 500


@carbon_routes.route("/activities/<user_id>", methods=["GET"])
def get_user_activities(user_id):
    """사용자 활동 기록 조회 API"""
    try:
        # 쿼리 파라미터 파싱
        limit = int(request.args.get('limit', 50))
        activity_type = request.args.get('activity_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 활동 기록 조회
        activities = carbon_tracking_service.get_user_activities(
            user_id=user_id,
            limit=limit,
            activity_type=activity_type,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            "success": True,
            "activities": activities,
            "count": len(activities)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"활동 조회 실패: {str(e)}"
        }), 500


@carbon_routes.route("/statistics/<user_id>", methods=["GET"])
def get_carbon_statistics(user_id):
    """사용자 탄소 통계 조회 API"""
    try:
        # 쿼리 파라미터
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        # 통계 조회
        statistics = carbon_tracking_service.get_user_carbon_statistics(
            user_id=user_id,
            year=year,
            month=month
        )

        return jsonify({
            "success": True,
            "statistics": statistics
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"통계 조회 실패: {str(e)}"
        }), 500


@carbon_routes.route("/challenges", methods=["GET"])
def get_active_challenges():
    """활성 챌린지 목록 조회 API"""
    try:
        limit = int(request.args.get('limit', 10))

        challenges = carbon_tracking_service.get_active_challenges(limit)

        return jsonify({
            "success": True,
            "challenges": challenges,
            "count": len(challenges)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"챌린지 조회 실패: {str(e)}"
        }), 500


@carbon_routes.route("/challenges", methods=["POST"])
def create_carbon_challenge():
    """탄소 챌린지 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['challenge_name', 'challenge_type', 'reward_tokens',
                          'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"필수 필드가 누락되었습니다: {field}"
                }), 400

        # 챌린지 생성
        challenge_id = carbon_tracking_service.create_carbon_challenge(data)

        return jsonify({
            "success": True,
            "message": "탄소 챌린지가 생성되었습니다.",
            "challenge_id": challenge_id
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"챌린지 생성 실패: {str(e)}"
        }), 500


@carbon_routes.route("/challenges/<int:challenge_id>/join", methods=["POST"])
def join_challenge(challenge_id):
    """챌린지 참여 API"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({
                "success": False,
                "message": "사용자 ID가 필요합니다."
            }), 400

        # 챌린지 참여
        success = carbon_tracking_service.join_challenge(user_id, challenge_id)

        if success:
            return jsonify({
                "success": True,
                "message": "챌린지에 참여했습니다.",
                "challenge_id": challenge_id,
                "user_id": user_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "챌린지 참여에 실패했습니다."
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"챌린지 참여 실패: {str(e)}"
        }), 500


@carbon_routes.route("/challenges/<user_id>/my", methods=["GET"])
def get_user_challenges(user_id):
    """사용자 참여 챌린지 조회 API"""
    try:
        challenges = carbon_tracking_service.get_user_challenges(user_id)

        return jsonify({
            "success": True,
            "challenges": challenges,
            "count": len(challenges)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"사용자 챌린지 조회 실패: {str(e)}"
        }), 500


@carbon_routes.route("/rewards/<user_id>/process", methods=["POST"])
def process_user_rewards(user_id):
    """사용자 보상 처리 API"""
    try:
        result = carbon_tracking_service.process_pending_rewards(user_id)

        return jsonify({
            "success": result['success'],
            "message": result.get('message', ''),
            "result": result
        }), 200 if result['success'] else 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"보상 처리 실패: {str(e)}"
        }), 500


@carbon_routes.route("/calculate", methods=["POST"])
def calculate_carbon_footprint():
    """탄소 발자국 계산 API (시뮬레이션)"""
    try:
        data = request.get_json()

        # 임시 활동 객체 생성하여 계산만 수행 (저장하지 않음)
        from app.service.carbon_calculation_engine import (
            CarbonCalculationEngine, CarbonActivity, ActivityType
        )

        engine = CarbonCalculationEngine()

        activity = CarbonActivity(
            activity_type=ActivityType(data.get('activity_type', 'local_food_purchase')),
            user_id=data.get('user_id', 'simulation'),
            product_name=data.get('product_name', ''),
            quantity=float(data.get('quantity', 1.0)),
            origin_region=data.get('origin_region', '경기도'),
            destination_region=data.get('destination_region', '서울시'),
            farming_method=data.get('farming_method', 'conventional'),
            transport_method=data.get('transport_method', 'truck_medium'),
            packaging_type=data.get('packaging_type', 'plastic'),
            activity_date=data.get('activity_date', date.today().isoformat())
        )

        result = engine.calculate_carbon_footprint(activity)

        return jsonify({
            "success": True,
            "calculation_result": {
                "total_emissions": result.total_emissions,
                "transport_emissions": result.transport_emissions,
                "production_emissions": result.production_emissions,
                "packaging_emissions": result.packaging_emissions,
                "carbon_savings": result.carbon_savings,
                "baseline_emissions": result.baseline_emissions,
                "reduction_percentage": result.reduction_percentage,
                "token_reward_eligible": result.token_reward_eligible,
                "reward_amount": result.reward_amount
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"탄소 발자국 계산 실패: {str(e)}"
        }), 500


@carbon_routes.route("/trigger/start", methods=["POST"])
def start_reward_trigger():
    """보상 트리거 시작 API (관리자 전용)"""
    try:
        # 실제로는 백그라운드 태스크로 실행해야 함
        # 여기서는 단순히 수동 트리거만 실행

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 한 번만 처리 실행
        loop.run_until_complete(carbon_reward_trigger.process_pending_rewards())
        loop.close()

        return jsonify({
            "success": True,
            "message": "보상 처리가 실행되었습니다."
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"보상 트리거 실행 실패: {str(e)}"
        }), 500


@carbon_routes.route("/leaderboard", methods=["GET"])
def get_carbon_leaderboard():
    """탄소 절약 리더보드 API"""
    try:
        period = request.args.get('period', 'monthly')  # monthly, weekly, daily
        limit = int(request.args.get('limit', 10))

        # 기간별 리더보드 쿼리
        if period == 'monthly':
            query = """
                SELECT
                    cp.name,
                    cp.region,
                    cms.total_carbon_savings,
                    cms.total_tokens_earned,
                    cms.total_activities
                FROM carbon_monthly_stats cms
                JOIN carbon_profiles cp ON cms.user_id = cp.user_id
                WHERE cms.year = EXTRACT(YEAR FROM CURRENT_DATE)
                AND cms.month = EXTRACT(MONTH FROM CURRENT_DATE)
                ORDER BY cms.total_carbon_savings DESC
                LIMIT %s
            """
        else:
            # 일일/주간은 활동 테이블에서 집계
            days = 7 if period == 'weekly' else 1
            query = f"""
                SELECT
                    cp.name,
                    cp.region,
                    SUM(ca.carbon_savings) as total_carbon_savings,
                    SUM(ca.token_reward_amount) as total_tokens_earned,
                    COUNT(*) as total_activities
                FROM carbon_activities ca
                JOIN carbon_profiles cp ON ca.user_id = cp.user_id
                WHERE ca.activity_date >= CURRENT_DATE - INTERVAL '{days} days'
                AND ca.verified = TRUE
                GROUP BY cp.user_id, cp.name, cp.region
                ORDER BY total_carbon_savings DESC
                LIMIT %s
            """

        leaderboard = carbon_tracking_service.db.pool.execute_query(query, (limit,))

        return jsonify({
            "success": True,
            "leaderboard": [dict(record) for record in leaderboard],
            "period": period,
            "count": len(leaderboard)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"리더보드 조회 실패: {str(e)}"
        }), 500