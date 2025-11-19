# -*- coding: utf-8 -*-
"""
MRV 및 ESG위원회 관리 API
측정, 검증, 위원회 관리를 위한 REST API 엔드포인트
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import logging
from typing import Dict, Optional
from datetime import datetime
import json

from ..service.mrv_measurement_module import (
    MRVMeasurementModule,
    MeasurementData,
    Evidence,
    EvidenceType
)
from ..service.mrv_reporting_service import MRVReportingService, ReportType
from ..service.committee_verification_workflow import (
    CommitteeVerificationWorkflow,
    VerificationRequest,
    CommitteeMember,
    CommitteeRole
)
from ..service.blockchain_verification_service import BlockchainVerificationService
from ..service.carbon_calculation_engine import CarbonActivity, ActivityType

logger = logging.getLogger(__name__)

# Blueprint 생성
mrv_bp = Blueprint('mrv', __name__, url_prefix='/api/mrv')
committee_bp = Blueprint('committee', __name__, url_prefix='/api/committee')

# 서비스 초기화 (앱 설정에서 주입)
mrv_module = None
reporting_service = None
verification_workflow = None
blockchain_service = None


def init_mrv_committee_api(mrv_mod, report_svc, verify_workflow, blockchain_svc):
    """API 초기화"""
    global mrv_module, reporting_service, verification_workflow, blockchain_service
    mrv_module = mrv_mod
    reporting_service = report_svc
    verification_workflow = verify_workflow
    blockchain_service = blockchain_svc


# ============================================================================
# MRV 측정 API
# ============================================================================

@mrv_bp.route('/measurement/submit', methods=['POST'])
def submit_measurement():
    """
    측정 데이터 제출

    Request Body:
        {
            'user_id': str,
            'activity': {...},
            'measurement_method': str,
            'evidences': [...],
            'location': {'lat': float, 'lng': float}
        }
    """
    try:
        data = request.get_json()

        # CarbonActivity 생성
        activity_data = data['activity']
        activity = CarbonActivity(
            activity_type=ActivityType(activity_data['activity_type']),
            user_id=data['user_id'],
            product_name=activity_data['product_name'],
            quantity=activity_data['quantity'],
            origin_region=activity_data['origin_region'],
            destination_region=activity_data['destination_region'],
            farming_method=activity_data['farming_method'],
            transport_method=activity_data['transport_method'],
            packaging_type=activity_data['packaging_type'],
            activity_date=activity_data.get('activity_date', datetime.now().isoformat())
        )

        # Evidence 생성
        evidences = []
        for ev in data.get('evidences', []):
            evidence = Evidence(
                evidence_type=EvidenceType(ev['evidence_type']),
                file_path=ev.get('file_path'),
                data=ev.get('data'),
                description=ev.get('description', ''),
                timestamp=datetime.now().isoformat()
            )
            evidences.append(evidence)

        # 측정
        measurement = mrv_module.measure_activity(
            activity=activity,
            measurement_method=data.get('measurement_method', 'manual'),
            evidences=evidences,
            location=data.get('location')
        )

        # 검증
        is_valid, issues = mrv_module.validate_measurement(measurement)

        return jsonify({
            'success': True,
            'data': {
                'measurement_id': measurement.measurement_id,
                'carbon_savings_kg': measurement.carbon_savings_kg,
                'dc_units': measurement.dc_units,
                'esg_gold_amount': measurement.esg_gold_amount,
                'confidence_score': measurement.confidence_score,
                'status': measurement.status.value,
                'data_hash': measurement.data_hash,
                'is_valid': is_valid,
                'issues': issues
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to submit measurement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mrv_bp.route('/measurement/<measurement_id>', methods=['GET'])
def get_measurement(measurement_id: str):
    """측정 데이터 조회"""
    try:
        # DB에서 조회
        # measurement = ...

        return jsonify({
            'success': True,
            'data': {
                'measurement_id': measurement_id,
                # ... 측정 데이터
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mrv_bp.route('/measurement/<measurement_id>/evidence', methods=['POST'])
def add_evidence(measurement_id: str):
    """증빙 자료 추가"""
    try:
        data = request.get_json()

        evidence = Evidence(
            evidence_type=EvidenceType(data['evidence_type']),
            file_path=data.get('file_path'),
            data=data.get('data'),
            description=data.get('description', ''),
            timestamp=datetime.now().isoformat()
        )

        # measurement 조회 후 증빙 추가
        # measurement = get_measurement_from_db(measurement_id)
        # mrv_module.add_evidence(measurement, evidence)

        return jsonify({
            'success': True,
            'message': 'Evidence added successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mrv_bp.route('/report/generate', methods=['POST'])
def generate_report():
    """리포트 생성"""
    try:
        data = request.get_json()
        report_type = ReportType(data['report_type'])

        if report_type == ReportType.DAILY:
            report = reporting_service.generate_daily_report(
                date=data['date'],
                user_id=data.get('user_id')
            )
        elif report_type == ReportType.MONTHLY:
            report = reporting_service.generate_monthly_report(
                year=data['year'],
                month=data['month'],
                user_id=data.get('user_id')
            )
        else:
            # Custom report
            # measurements = fetch_from_db(...)
            # report = reporting_service.generate_measurement_report(measurements)
            pass

        # 리포트 내보내기
        report_data = reporting_service.export_report(report)

        return jsonify({
            'success': True,
            'data': {
                'report_id': report.report_id,
                'report_type': report.report_type.value,
                'summary': report.summary,
                'generated_at': report.generated_at
            },
            'report_data': report_data
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mrv_bp.route('/statistics', methods=['GET'])
def get_mrv_statistics():
    """MRV 통계"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # DB에서 통계 조회
        stats = {
            'total_measurements': 0,
            'total_carbon_saved': 0.0,
            'total_dc_issued': 0.0,
            'average_confidence': 0.0
        }

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 위원회 검증 API
# ============================================================================

@committee_bp.route('/verification/submit', methods=['POST'])
def submit_verification_request():
    """검증 요청 제출"""
    try:
        data = request.get_json()

        # measurement 조회
        # measurement = get_measurement_from_db(data['measurement_id'])

        # 검증 요청 제출
        # request = verification_workflow.submit_for_verification(
        #     measurement=measurement,
        #     user_id=data['user_id'],
        #     priority=data.get('priority', 0)
        # )

        return jsonify({
            'success': True,
            'data': {
                'request_id': 'VRQ-123',  # request.request_id
                'status': 'pending',
                'assigned_to': None
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/verification/pending', methods=['GET'])
def get_pending_verifications():
    """대기 중인 검증 목록"""
    try:
        member_id = request.args.get('member_id')
        priority = request.args.get('priority', type=int)

        requests = verification_workflow.get_pending_verifications(
            member_id=member_id,
            priority=priority
        )

        return jsonify({
            'success': True,
            'data': {
                'pending_count': len(requests),
                'requests': [
                    {
                        'request_id': req.request_id,
                        'measurement_id': req.measurement.measurement_id,
                        'carbon_savings': req.measurement.carbon_savings_kg,
                        'confidence_score': req.measurement.confidence_score,
                        'submitted_at': req.submitted_at,
                        'priority': req.priority,
                        'status': req.status.value
                    } for req in requests
                ]
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/verification/<request_id>/review', methods=['POST'])
def review_verification():
    """검증 검토 및 승인/반려"""
    try:
        request_id = request_id
        data = request.get_json()

        result = verification_workflow.review_and_verify(
            request_id=request_id,
            reviewer_id=data['reviewer_id'],
            approved=data['approved'],
            comments=data.get('comments', ''),
            adjustments=data.get('adjustments')
        )

        # 승인된 경우 블록체인에 기록
        if result.approved and data.get('store_on_blockchain', True):
            blockchain_result = blockchain_service.store_verification_on_chain(
                verification_result=result,
                verifier_private_key=data['verifier_private_key']
            )
            result.blockchain_tx_id = blockchain_result.get('tx_id')

        return jsonify({
            'success': True,
            'data': {
                'result_id': result.result_id,
                'approved': result.approved,
                'carbon_verified': result.carbon_savings_verified,
                'dc_verified': result.dc_units_verified,
                'blockchain_tx_id': result.blockchain_tx_id
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/verification/<request_id>/assign', methods=['POST'])
def assign_verification():
    """검증 배정"""
    try:
        request_id = request_id
        data = request.get_json()

        success = verification_workflow.assign_to_reviewer(
            request_id=request_id,
            member_id=data['member_id']
        )

        return jsonify({
            'success': success,
            'message': 'Verification assigned successfully' if success else 'Assignment failed'
        }), 200 if success else 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/verification/<request_id>/resubmit', methods=['POST'])
def request_resubmission():
    """재제출 요청"""
    try:
        request_id = request_id
        data = request.get_json()

        success = verification_workflow.request_resubmission(
            request_id=request_id,
            reviewer_id=data['reviewer_id'],
            feedback=data['feedback']
        )

        return jsonify({'success': success}), 200 if success else 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/members', methods=['GET'])
def get_committee_members():
    """위원회 위원 목록"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        role = request.args.get('role')

        members = verification_workflow.committee_members

        if active_only:
            members = [m for m in members if m.active]

        if role:
            members = [m for m in members if m.role.value == role]

        return jsonify({
            'success': True,
            'data': {
                'members': [
                    {
                        'member_id': m.member_id,
                        'name': m.name,
                        'role': m.role.value,
                        'email': m.email,
                        'specialization': m.specialization,
                        'active': m.active
                    } for m in members
                ]
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/members/<member_id>/performance', methods=['GET'])
def get_member_performance():
    """위원 성과 조회"""
    try:
        member_id = member_id

        # DB에서 성과 조회 (v_committee_performance view)
        performance = {
            'member_id': member_id,
            'total_assigned': 0,
            'total_approved': 0,
            'total_rejected': 0,
            'approval_rate': 0.0,
            'avg_review_time_hours': 0.0
        }

        return jsonify({
            'success': True,
            'data': performance
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/statistics', methods=['GET'])
def get_committee_statistics():
    """위원회 통계"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        stats = verification_workflow.get_verification_statistics(
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 블록체인 검증 API
# ============================================================================

@committee_bp.route('/blockchain/verify/<tx_id>', methods=['GET'])
def verify_blockchain_record():
    """블록체인 기록 검증"""
    try:
        tx_id = tx_id

        # 블록체인에서 데이터 조회
        verification_data = blockchain_service.retrieve_verification_from_chain(tx_id)

        if not verification_data:
            return jsonify({
                'success': False,
                'error': 'Verification record not found on blockchain'
            }), 404

        # 무결성 검증
        is_valid, message = blockchain_service.verify_data_integrity(verification_data)

        return jsonify({
            'success': True,
            'data': {
                'tx_id': tx_id,
                'verification_data': verification_data,
                'integrity_verified': is_valid,
                'message': message,
                'explorer_url': f"https://testnet.algoexplorer.io/tx/{tx_id}"
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/blockchain/proof/<result_id>', methods=['GET'])
def get_verification_proof():
    """검증 증명서 조회"""
    try:
        result_id = result_id

        # DB에서 검증 결과 조회
        # verification_result = get_verification_result_from_db(result_id)

        # 증명서 생성
        # proof = blockchain_service.generate_proof_of_verification(verification_result)

        proof = {}  # Placeholder

        return jsonify({
            'success': True,
            'data': proof
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@committee_bp.route('/blockchain/certificate/nft', methods=['POST'])
def create_verification_nft():
    """검증 인증서 NFT 생성"""
    try:
        data = request.get_json()

        # verification_result = get_verification_result_from_db(data['result_id'])

        # nft_result = blockchain_service.create_verification_certificate_nft(
        #     verification_result=verification_result,
        #     creator_private_key=data['creator_private_key']
        # )

        nft_result = {}  # Placeholder

        return jsonify({
            'success': True,
            'data': nft_result
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@mrv_bp.route('/health', methods=['GET'])
@committee_bp.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        'status': 'ok',
        'service': 'mrv-committee-api',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'mrv_measurement': mrv_module is not None,
            'reporting': reporting_service is not None,
            'verification_workflow': verification_workflow is not None,
            'blockchain': blockchain_service is not None
        }
    }), 200


# 에러 핸들러
@mrv_bp.errorhandler(404)
@committee_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@mrv_bp.errorhandler(500)
@committee_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # 개발 모드 테스트
    app = Flask(__name__)
    CORS(app)

    # Blueprint 등록
    app.register_blueprint(mrv_bp)
    app.register_blueprint(committee_bp)

    # 서비스 초기화
    from carbon_calculation_engine import CarbonCalculationEngine
    carbon_engine = CarbonCalculationEngine()
    mrv_mod = MRVMeasurementModule(carbon_engine)
    report_svc = MRVReportingService()
    verify_workflow = CommitteeVerificationWorkflow()
    blockchain_svc = BlockchainVerificationService()

    init_mrv_committee_api(mrv_mod, report_svc, verify_workflow, blockchain_svc)

    app.run(debug=True, host='0.0.0.0', port=5001)
