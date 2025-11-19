# -*- coding: utf-8 -*-
"""
지자체 홈페이지 API
지자체별 탄소감축 현황, 생산자 등록, ESG 프로그램, 인센티브 정책, 충전소 관리
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
import json

logger = logging.getLogger(__name__)

# Blueprint 생성
local_gov_bp = Blueprint('local_government', __name__, url_prefix='/api/local-government')

# ============================================================================
# 지자체 대시보드 API
# ============================================================================

@local_gov_bp.route('/governments', methods=['GET'])
def get_local_governments():
    """지자체 목록 조회"""
    try:
        government_type = request.args.get('type')
        is_active = request.args.get('is_active', 'true').lower() == 'true'

        # Mock data - 실제로는 DB 조회
        governments = [
            {
                'government_id': 'GOV-SEOUL-001',
                'government_name': '서울특별시',
                'government_type': 'city',
                'region_code': 'KR-11',
                'population': 9700000,
                'contact_email': 'carbon@seoul.go.kr',
                'website_url': 'https://seoul.go.kr',
                'is_active': True
            },
            {
                'government_id': 'GOV-BUSAN-001',
                'government_name': '부산광역시',
                'government_type': 'city',
                'region_code': 'KR-26',
                'population': 3400000,
                'contact_email': 'esg@busan.go.kr',
                'website_url': 'https://busan.go.kr',
                'is_active': True
            }
        ]

        return jsonify({
            'success': True,
            'data': {'governments': governments, 'total': len(governments)}
        }), 200

    except Exception as e:
        logger.error(f"Failed to get governments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/governments/<government_id>/dashboard', methods=['GET'])
def get_government_dashboard(government_id: str):
    """지자체 대시보드 데이터 조회"""
    try:
        # Mock dashboard data
        dashboard_data = {
            'government_info': {
                'government_id': government_id,
                'government_name': '서울특별시',
                'government_type': 'city',
                'population': 9700000,
                'region_code': 'KR-11'
            },
            'carbon_stats': {
                'total_carbon_reduction': 125000,
                'reduction_percentage': 12.5,
                'baseline_emissions': 1000000,
                'current_emissions': 875000,
                'national_rank': 1,
                'regional_rank': 1,
                'active_residents': 8500,
                'active_businesses': 1200,
                'esg_gold_issued': 125000000000,
                'breakdown': {
                    'ev_usage_reduction': 45000,
                    'renewable_energy_reduction': 30000,
                    'recycling_reduction': 25000,
                    'tree_planting_reduction': 15000,
                    'green_products_reduction': 10000
                }
            },
            'targets': {
                'target_year': 2024,
                'target_reduction_kg': 500000,
                'current_reduction_kg': 125000,
                'achievement_percentage': 25.0,
                'status': 'in_progress'
            },
            'programs': {
                'active_programs': 12,
                'total_participants': 15430,
                'expected_carbon_reduction': 200000
            },
            'producers': {
                'total_producers': 245,
                'verified_producers': 198,
                'pending_verification': 47,
                'total_products': 1280
            },
            'charging_stations': {
                'operational_stations': 38,
                'total_chargers': 156,
                'available_chargers': 128,
                'total_sessions_today': 342,
                'total_energy_delivered_kwh': 8450
            },
            'incentives': {
                'active_policies': 8,
                'total_budget': 15000000000,
                'remaining_budget': 12500000000,
                'applications_processed': 1245,
                'total_disbursed': 2500000000
            }
        }

        return jsonify({
            'success': True,
            'data': dashboard_data
        }), 200

    except Exception as e:
        logger.error(f"Failed to get dashboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 탄소 감축 통계 API
# ============================================================================

@local_gov_bp.route('/governments/<government_id>/carbon-stats', methods=['GET'])
def get_carbon_stats(government_id: str):
    """지자체 탄소 감축 통계 조회"""
    try:
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Mock time series data
        stats = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            stats.append({
                'date': date,
                'total_carbon_reduction': 120000 + (i * 1000),
                'ev_usage_reduction': 40000 + (i * 300),
                'renewable_energy_reduction': 30000 + (i * 250),
                'recycling_reduction': 25000 + (i * 200),
                'active_residents': 8000 + (i * 50),
                'active_businesses': 1100 + (i * 10)
            })

        return jsonify({
            'success': True,
            'data': {
                'stats': stats,
                'period': period,
                'government_id': government_id
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get carbon stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/governments/<government_id>/rankings', methods=['GET'])
def get_government_rankings(government_id: str):
    """전국 지자체 탄소감축 랭킹 조회"""
    try:
        category = request.args.get('category', 'total_reduction')

        rankings = [
            {
                'rank': 1,
                'government_id': 'GOV-SEOUL-001',
                'government_name': '서울특별시',
                'total_carbon_reduction': 125000,
                'reduction_percentage': 12.5,
                'active_residents': 8500
            },
            {
                'rank': 2,
                'government_id': 'GOV-BUSAN-001',
                'government_name': '부산광역시',
                'total_carbon_reduction': 67000,
                'reduction_percentage': 11.2,
                'active_residents': 4200
            },
            {
                'rank': 3,
                'government_id': 'GOV-INCHEON-001',
                'government_name': '인천광역시',
                'total_carbon_reduction': 52000,
                'reduction_percentage': 10.8,
                'active_residents': 3500
            }
        ]

        return jsonify({
            'success': True,
            'data': {'rankings': rankings}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 지역 ESG 프로그램 API
# ============================================================================

@local_gov_bp.route('/governments/<government_id>/programs', methods=['GET'])
def get_esg_programs(government_id: str):
    """지역 ESG 프로그램 목록"""
    try:
        program_type = request.args.get('type')
        status = request.args.get('status')

        programs = [
            {
                'program_id': 'PROG-SEOUL-001',
                'government_id': government_id,
                'program_name': '서울시 탄소중립 챌린지',
                'program_type': 'carbon_reduction',
                'description': '시민 참여형 탄소감축 캠페인으로 일상생활에서 탄소를 줄이고 보상을 받을 수 있습니다.',
                'target_group': 'all',
                'budget_amount': 500000000,
                'support_type': 'mixed',
                'start_date': '2024-03-01',
                'end_date': '2024-12-31',
                'application_deadline': '2024-11-30',
                'max_participants': 100000,
                'current_participants': 15430,
                'status': 'recruiting',
                'expected_carbon_reduction': 200000,
                'manager_name': '김환경',
                'manager_email': 'carbon@seoul.go.kr',
                'manager_phone': '02-1234-5678'
            },
            {
                'program_id': 'PROG-SEOUL-002',
                'government_id': government_id,
                'program_name': '태양광 패널 설치 지원',
                'program_type': 'renewable_energy',
                'description': '주택 및 건물 태양광 패널 설치 비용의 50%를 지원합니다.',
                'target_group': 'residents',
                'budget_amount': 2000000000,
                'support_type': 'financial',
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'max_participants': 5000,
                'current_participants': 1245,
                'status': 'ongoing',
                'manager_name': '이태양'
            }
        ]

        return jsonify({
            'success': True,
            'data': {'programs': programs}
        }), 200

    except Exception as e:
        logger.error(f"Failed to get programs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/programs/<program_id>', methods=['GET'])
def get_program_detail(program_id: str):
    """ESG 프로그램 상세 조회"""
    try:
        program = {
            'program_id': program_id,
            'program_name': '서울시 탄소중립 챌린지',
            'program_type': 'carbon_reduction',
            'description': '시민 참여형 탄소감축 캠페인으로 일상생활에서 탄소를 줄이고 보상을 받을 수 있습니다.',
            'objectives': '2024년까지 시민 참여를 통해 20만 kg의 탄소를 감축합니다.',
            'target_group': 'all',
            'budget_amount': 500000000,
            'eligibility_criteria': '서울시 거주자 또는 서울시 소재 사업장 근무자',
            'required_documents': ['신분증', '거주지 증명서류'],
            'application_process': [
                '1. 온라인 신청서 작성',
                '2. 서류 제출',
                '3. 승인 대기 (3-5일)',
                '4. 활동 시작'
            ],
            'benefits': [
                'ESG-Gold 토큰 적립',
                '우수 참여자 시상',
                '탄소감축 인증서 발급'
            ],
            'max_participants': 100000,
            'current_participants': 15430,
            'participation_rate': 15.43,
            'status': 'recruiting'
        }

        return jsonify({
            'success': True,
            'data': program
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 지역 생산자 등록 API
# ============================================================================

@local_gov_bp.route('/governments/<government_id>/producers', methods=['GET'])
def get_producers(government_id: str):
    """지역 생산자 목록 조회"""
    try:
        producer_type = request.args.get('type')
        verification_status = request.args.get('verification_status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        producers = [
            {
                'producer_id': 'PROD-SEOUL-001',
                'government_id': government_id,
                'producer_name': '행복농장',
                'producer_type': 'farmer',
                'contact_person': '김농부',
                'contact_phone': '010-1234-5678',
                'farm_address': '서울시 강동구 상일동',
                'farm_area_sqm': 15000,
                'organic_certified': True,
                'gap_certified': True,
                'verification_status': 'verified',
                'verified_at': '2024-01-15T10:00:00',
                'carbon_footprint_kg': 1250,
                'available_products': 8,
                'rating': 4.8
            },
            {
                'producer_id': 'PROD-SEOUL-002',
                'government_id': government_id,
                'producer_name': '청정수산',
                'producer_type': 'fisherman',
                'contact_person': '박어부',
                'contact_phone': '010-2345-6789',
                'farm_address': '서울시 마포구 상암동',
                'haccp_certified': True,
                'verification_status': 'verified',
                'available_products': 5
            }
        ]

        return jsonify({
            'success': True,
            'data': {
                'producers': producers,
                'page': page,
                'per_page': per_page,
                'total': len(producers)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get producers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/producers/register', methods=['POST'])
def register_producer():
    """생산자 등록"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required = ['government_id', 'producer_name', 'producer_type', 'contact_person', 'contact_phone', 'farm_address']
        if not all(k in data for k in required):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # producer_id 생성
        producer_id = f"PROD-{data['government_id'].split('-')[1]}-{secrets.token_hex(4)}"

        # DB 저장 (실제 구현 시)
        # ...

        logger.info(f"New producer registered: {producer_id}")

        return jsonify({
            'success': True,
            'data': {
                'producer_id': producer_id,
                'message': '생산자 등록이 완료되었습니다. 관리자 검증 후 승인됩니다.',
                'verification_status': 'pending'
            }
        }), 201

    except Exception as e:
        logger.error(f"Failed to register producer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/producers/<producer_id>', methods=['GET'])
def get_producer_detail(producer_id: str):
    """생산자 상세 정보"""
    try:
        producer = {
            'producer_id': producer_id,
            'government_id': 'GOV-SEOUL-001',
            'government_name': '서울특별시',
            'producer_name': '행복농장',
            'producer_type': 'farmer',
            'business_registration_number': '123-45-67890',
            'contact_person': '김농부',
            'contact_phone': '010-1234-5678',
            'contact_email': 'happy@farm.com',
            'farm_address': '서울시 강동구 상일동 123',
            'farm_latitude': 37.5565,
            'farm_longitude': 127.1690,
            'farm_area_sqm': 15000,
            'organic_certified': True,
            'gap_certified': True,
            'haccp_certified': False,
            'other_certifications': ['친환경농산물인증', 'GAP인증'],
            'carbon_footprint_kg': 1250,
            'water_usage_liters': 125000,
            'renewable_energy_ratio': 0.35,
            'waste_recycling_ratio': 0.85,
            'verification_status': 'verified',
            'verified_by': 'admin001',
            'verified_at': '2024-01-15T10:00:00',
            'registration_date': '2024-01-10',
            'products': [
                {
                    'product_id': 'PRDCT-001',
                    'product_name': '유기농 토마토',
                    'product_type': 'vegetable',
                    'unit_price': 15000,
                    'unit_type': 'kg',
                    'is_available': True
                }
            ]
        }

        return jsonify({
            'success': True,
            'data': producer
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/producers/<producer_id>/verify', methods=['POST'])
def verify_producer(producer_id: str):
    """생산자 검증 승인/반려 (관리자 전용)"""
    try:
        data = request.get_json()

        verification_status = data.get('verification_status')  # 'verified' or 'rejected'
        verification_notes = data.get('verification_notes')

        if verification_status not in ['verified', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid verification status'}), 400

        # DB 업데이트
        # ...

        return jsonify({
            'success': True,
            'data': {
                'producer_id': producer_id,
                'verification_status': verification_status,
                'verified_at': datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to verify producer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 인센티브 정책 API
# ============================================================================

@local_gov_bp.route('/governments/<government_id>/incentives', methods=['GET'])
def get_incentive_policies(government_id: str):
    """지자체 인센티브 정책 목록"""
    try:
        policy_type = request.args.get('type')
        status = request.args.get('status', 'active')

        policies = [
            {
                'policy_id': 'POL-SEOUL-001',
                'government_id': government_id,
                'policy_name': '전기차 충전 지원금',
                'policy_type': 'subsidy',
                'description': '전기차 이용자에게 충전비의 50%를 지원합니다.',
                'target_group': '서울시 거주 전기차 소유자',
                'benefit_amount': 100000,
                'benefit_unit': 'KRW/월',
                'total_budget': 5000000000,
                'remaining_budget': 4800000000,
                'application_start_date': '2024-01-01',
                'application_end_date': '2024-12-31',
                'status': 'active',
                'contact_department': '환경정책과',
                'contact_phone': '02-1234-5678'
            },
            {
                'policy_id': 'POL-SEOUL-002',
                'government_id': government_id,
                'policy_name': 'ESG-Gold 보너스 프로그램',
                'policy_type': 'esg_gold_bonus',
                'description': '탄소감축 활동 시 ESG-Gold 20% 추가 지급',
                'target_group': '서울시민 전체',
                'esg_gold_bonus_percentage': 20,
                'total_budget': 1000000000,
                'remaining_budget': 850000000,
                'application_start_date': '2024-03-01',
                'status': 'active'
            }
        ]

        return jsonify({
            'success': True,
            'data': {'policies': policies}
        }), 200

    except Exception as e:
        logger.error(f"Failed to get incentive policies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/incentives/<policy_id>/apply', methods=['POST'])
def apply_for_incentive(policy_id: str):
    """인센티브 신청"""
    try:
        data = request.get_json()

        application_id = f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"

        # DB 저장
        # ...

        return jsonify({
            'success': True,
            'data': {
                'application_id': application_id,
                'policy_id': policy_id,
                'message': '인센티브 신청이 완료되었습니다. 검토 후 결과를 알려드립니다.',
                'status': 'submitted',
                'estimated_review_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            }
        }), 201

    except Exception as e:
        logger.error(f"Failed to apply for incentive: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/incentives/applications/<application_id>', methods=['GET'])
def get_application_status(application_id: str):
    """인센티브 신청 현황 조회"""
    try:
        application = {
            'application_id': application_id,
            'policy_id': 'POL-SEOUL-001',
            'policy_name': '전기차 충전 지원금',
            'applicant_name': '홍길동',
            'application_date': '2024-01-20',
            'requested_amount': 100000,
            'status': 'approved',
            'approved_amount': 100000,
            'approval_date': '2024-01-27',
            'payment_date': '2024-02-01',
            'review_notes': '승인되었습니다.'
        }

        return jsonify({
            'success': True,
            'data': application
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 충전소 위치 맵 API
# ============================================================================

@local_gov_bp.route('/charging-stations', methods=['GET'])
def get_charging_stations():
    """충전소 목록 조회 (맵용)"""
    try:
        government_id = request.args.get('government_id')
        station_type = request.args.get('type')
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius_km = request.args.get('radius_km', 10, type=float)
        accepts_esg_gold = request.args.get('accepts_esg_gold')

        stations = [
            {
                'station_id': 'CS-SEOUL-001',
                'government_id': 'GOV-SEOUL-001',
                'government_name': '서울특별시',
                'station_name': '강남역 급속충전소',
                'station_type': 'fast',
                'operator_name': '한국전력',
                'address': '서울시 강남구 강남대로 396',
                'latitude': 37.4979,
                'longitude': 127.0276,
                'total_chargers': 8,
                'available_chargers': 6,
                'charger_types': ['AC 3kW', 'DC 50kW', 'DC 100kW'],
                'max_power_kw': 100,
                'price_per_kwh': 350,
                'parking_fee_per_hour': 2000,
                'accepts_esg_gold': True,
                'esg_gold_discount_percentage': 15,
                'is_24_hours': True,
                'operational_status': 'operational',
                'average_rating': 4.6,
                'total_charging_sessions': 1542,
                'total_carbon_reduction_kg': 23456,
                'has_wifi': True,
                'has_cafe': True,
                'wheelchair_accessible': True
            },
            {
                'station_id': 'CS-SEOUL-002',
                'government_id': 'GOV-SEOUL-001',
                'station_name': '여의도 충전센터',
                'station_type': 'super_fast',
                'operator_name': 'SK네트웍스',
                'address': '서울시 영등포구 여의도동 23',
                'latitude': 37.5219,
                'longitude': 126.9245,
                'total_chargers': 12,
                'available_chargers': 10,
                'charger_types': ['DC 100kW', 'DC 350kW'],
                'max_power_kw': 350,
                'price_per_kwh': 450,
                'accepts_esg_gold': True,
                'esg_gold_discount_percentage': 20,
                'is_24_hours': True,
                'operational_status': 'operational',
                'average_rating': 4.8
            }
        ]

        return jsonify({
            'success': True,
            'data': {
                'stations': stations,
                'total': len(stations)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get charging stations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/charging-stations/<station_id>', methods=['GET'])
def get_charging_station_detail(station_id: str):
    """충전소 상세 정보"""
    try:
        station = {
            'station_id': station_id,
            'government_id': 'GOV-SEOUL-001',
            'government_name': '서울특별시',
            'station_name': '강남역 급속충전소',
            'station_type': 'fast',
            'operator_name': '한국전력',
            'operator_contact': '1588-1234',
            'address': '서울시 강남구 강남대로 396',
            'latitude': 37.4979,
            'longitude': 127.0276,
            'total_chargers': 8,
            'available_chargers': 6,
            'charger_types': ['AC 3kW', 'DC 50kW', 'DC 100kW'],
            'charger_details': [
                {'charger_number': 1, 'type': 'DC 100kW', 'status': 'available'},
                {'charger_number': 2, 'type': 'DC 100kW', 'status': 'charging'},
                {'charger_number': 3, 'type': 'DC 50kW', 'status': 'available'}
            ],
            'max_power_kw': 100,
            'price_per_kwh': 350,
            'parking_fee_per_hour': 2000,
            'accepts_esg_gold': True,
            'accepts_pam_token': True,
            'esg_gold_discount_percentage': 15,
            'operating_hours': {
                'monday': '00:00-24:00',
                'tuesday': '00:00-24:00',
                'wednesday': '00:00-24:00',
                'thursday': '00:00-24:00',
                'friday': '00:00-24:00',
                'saturday': '00:00-24:00',
                'sunday': '00:00-24:00'
            },
            'is_24_hours': True,
            'amenities': {
                'wifi': True,
                'restroom': True,
                'cafe': True,
                'convenience_store': False,
                'parking': True,
                'wheelchair_accessible': True
            },
            'operational_status': 'operational',
            'average_rating': 4.6,
            'review_count': 234,
            'total_charging_sessions': 1542,
            'total_energy_delivered_kwh': 45678,
            'total_carbon_reduction_kg': 23456,
            'installation_date': '2023-06-15',
            'last_maintenance_date': '2024-01-05',
            'reviews': [
                {
                    'rating': 5,
                    'review_text': '충전 속도가 빠르고 주차도 편리합니다.',
                    'created_at': '2024-01-20T15:30:00'
                }
            ]
        }

        return jsonify({
            'success': True,
            'data': station
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/charging-stations/<station_id>/start-charging', methods=['POST'])
def start_charging_session(station_id: str):
    """충전 세션 시작"""
    try:
        data = request.get_json()

        user_algorand_address = data.get('user_algorand_address')
        charger_number = data.get('charger_number')
        payment_method = data.get('payment_method')

        if not all([user_algorand_address, charger_number, payment_method]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        usage_id = f"CHG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"

        # DB에 세션 저장
        # 충전기 상태 업데이트
        # ...

        return jsonify({
            'success': True,
            'data': {
                'usage_id': usage_id,
                'station_id': station_id,
                'charger_number': charger_number,
                'start_time': datetime.now().isoformat(),
                'status': 'in_progress',
                'message': '충전이 시작되었습니다.'
            }
        }), 201

    except Exception as e:
        logger.error(f"Failed to start charging: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@local_gov_bp.route('/charging-sessions/<usage_id>/stop', methods=['POST'])
def stop_charging_session(usage_id: str):
    """충전 세션 종료"""
    try:
        # 세션 정보 조회
        # 충전량 계산
        # 결제 처리
        # 탄소 감축량 계산
        # ESG-Gold 발급

        session_result = {
            'usage_id': usage_id,
            'station_id': 'CS-SEOUL-001',
            'start_time': '2024-01-20T10:00:00',
            'end_time': datetime.now().isoformat(),
            'duration_minutes': 45,
            'energy_delivered_kwh': 25.5,
            'carbon_reduction_kg': 13.1,
            'total_cost': 8925,
            'payment_method': 'esg_gold',
            'esg_gold_amount': 8925000000,
            'discount_applied': 1339,
            'esg_gold_earned': 13100000,
            'status': 'completed'
        }

        return jsonify({
            'success': True,
            'data': session_result
        }), 200

    except Exception as e:
        logger.error(f"Failed to stop charging: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 지역 공지사항 API
# ============================================================================

@local_gov_bp.route('/governments/<government_id>/announcements', methods=['GET'])
def get_announcements(government_id: str):
    """지역 공지사항 목록"""
    try:
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        announcements = [
            {
                'announcement_id': 'ANN-SEOUL-001',
                'government_id': government_id,
                'title': '서울시 탄소중립 챌린지 참여자 모집',
                'summary': '2024년 상반기 탄소중립 챌린지에 참여할 시민을 모집합니다.',
                'category': 'program',
                'priority': 2,
                'is_pinned': True,
                'author_name': '환경정책과',
                'published_at': '2024-01-15T10:00:00',
                'view_count': 2345
            },
            {
                'announcement_id': 'ANN-SEOUL-002',
                'government_id': government_id,
                'title': '전기차 충전소 10개소 추가 설치',
                'summary': '시민 편의를 위해 주요 거점에 충전소를 추가 설치합니다.',
                'category': 'notice',
                'priority': 1,
                'published_at': '2024-01-10T14:00:00',
                'view_count': 1234
            }
        ]

        return jsonify({
            'success': True,
            'data': {
                'announcements': announcements,
                'page': page,
                'per_page': per_page,
                'total': len(announcements)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get announcements: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@local_gov_bp.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        'status': 'ok',
        'service': 'local-government-api',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(local_gov_bp)
    app.run(debug=True, host='0.0.0.0', port=5003)
