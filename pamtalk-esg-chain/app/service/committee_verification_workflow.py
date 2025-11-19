# -*- coding: utf-8 -*-
"""
ESG위원회 검증 승인 워크플로우
탄소 감축 활동의 검증 및 승인 프로세스 관리
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .mrv_measurement_module import MeasurementData, MeasurementStatus

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """검증 상태"""
    PENDING = "pending"  # 검증 대기
    IN_REVIEW = "in_review"  # 검토 중
    APPROVED = "approved"  # 승인됨
    REJECTED = "rejected"  # 반려됨
    RESUBMISSION_REQUIRED = "resubmission_required"  # 재제출 필요
    ESCALATED = "escalated"  # 상위 위원회로 에스컬레이션


class CommitteeRole(Enum):
    """위원회 역할"""
    REVIEWER = "reviewer"  # 검토자
    APPROVER = "approver"  # 승인자
    ADMIN = "admin"  # 관리자
    AUDITOR = "auditor"  # 감사자


@dataclass
class CommitteeMember:
    """위원회 위원"""
    member_id: str
    name: str
    role: CommitteeRole
    email: str
    wallet_address: str
    specialization: List[str]  # 전문 분야
    active: bool = True


@dataclass
class VerificationRequest:
    """검증 요청"""
    request_id: str
    measurement: MeasurementData
    submitted_by: str
    submitted_at: str

    # 검증 상태
    status: VerificationStatus = VerificationStatus.PENDING
    assigned_to: Optional[str] = None  # 담당 위원 ID
    assigned_at: Optional[str] = None

    # 검증 결과
    verification_result: Optional[Dict] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None

    # 피드백
    comments: List[Dict] = None
    rejection_reason: Optional[str] = None

    # 우선순위
    priority: int = 0  # 0: 일반, 1: 높음, 2: 긴급

    def __post_init__(self):
        if self.comments is None:
            self.comments = []


@dataclass
class VerificationResult:
    """검증 결과"""
    result_id: str
    request_id: str
    measurement_id: str

    # 검증 판정
    approved: bool
    confidence_score_verified: float
    carbon_savings_verified: float
    dc_units_verified: float

    # 검증 세부사항
    verification_method: str
    verified_by: str
    verified_at: str

    # 검증 체크리스트
    checklist_results: Dict
    evidence_verified: bool
    data_integrity_verified: bool
    calculation_verified: bool

    # 피드백
    verifier_comments: str
    recommendations: List[str] = None

    # 블록체인 기록
    blockchain_tx_id: Optional[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class CommitteeVerificationWorkflow:
    """ESG위원회 검증 워크플로우"""

    def __init__(self, db_connection=None):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
        self.committee_members = []

        # 자동 승인 기준
        self.auto_approve_threshold = {
            'confidence_score': 95,  # 95% 이상
            'evidence_count': 3,  # 증빙 3개 이상
            'carbon_savings_max': 50  # 50kg 이하
        }

    def submit_for_verification(self, measurement: MeasurementData,
                               user_id: str,
                               priority: int = 0) -> VerificationRequest:
        """
        검증 요청 제출

        Args:
            measurement: 측정 데이터
            user_id: 제출자 ID
            priority: 우선순위

        Returns:
            VerificationRequest: 검증 요청
        """
        # 요청 ID 생성
        request_id = self._generate_request_id()

        # 검증 요청 생성
        request = VerificationRequest(
            request_id=request_id,
            measurement=measurement,
            submitted_by=user_id,
            submitted_at=datetime.now().isoformat(),
            status=VerificationStatus.PENDING,
            priority=priority
        )

        # 자동 승인 가능 여부 확인
        if self._check_auto_approve_eligible(measurement):
            logger.info(f"Measurement {measurement.measurement_id} eligible for auto-approval")
            request.status = VerificationStatus.APPROVED
            request.approved_at = datetime.now().isoformat()
            request.approved_by = "system_auto"

            # 자동 승인 처리
            result = self._auto_approve(request)
            request.verification_result = result

        else:
            # 담당 위원 자동 배정
            assigned_member = self._assign_to_committee_member(measurement, request.priority)
            if assigned_member:
                request.assigned_to = assigned_member.member_id
                request.assigned_at = datetime.now().isoformat()
                request.status = VerificationStatus.IN_REVIEW

        # DB에 저장
        if self.db:
            self._save_verification_request(request)

        logger.info(f"Verification request submitted: {request_id}, Status: {request.status.value}")

        return request

    def assign_to_reviewer(self, request_id: str, member_id: str) -> bool:
        """
        검토자에게 수동 배정

        Args:
            request_id: 요청 ID
            member_id: 위원 ID

        Returns:
            성공 여부
        """
        request = self._get_verification_request(request_id)
        if not request:
            logger.error(f"Verification request not found: {request_id}")
            return False

        member = self._get_committee_member(member_id)
        if not member or not member.active:
            logger.error(f"Committee member not found or inactive: {member_id}")
            return False

        # 배정
        request.assigned_to = member_id
        request.assigned_at = datetime.now().isoformat()
        request.status = VerificationStatus.IN_REVIEW

        # DB 업데이트
        if self.db:
            self._update_verification_request(request)

        logger.info(f"Request {request_id} assigned to {member.name}")

        return True

    def review_and_verify(self, request_id: str, reviewer_id: str,
                         approved: bool,
                         comments: str = "",
                         adjustments: Dict = None) -> VerificationResult:
        """
        검증 검토 및 승인/반려

        Args:
            request_id: 요청 ID
            reviewer_id: 검토자 ID
            approved: 승인 여부
            comments: 검토 의견
            adjustments: 수정된 값 (탄소 감축량 등)

        Returns:
            VerificationResult: 검증 결과
        """
        request = self._get_verification_request(request_id)
        if not request:
            raise ValueError(f"Verification request not found: {request_id}")

        reviewer = self._get_committee_member(reviewer_id)
        if not reviewer:
            raise ValueError(f"Committee member not found: {reviewer_id}")

        # 검증 체크리스트 수행
        checklist_results = self._perform_verification_checklist(request.measurement)

        # 검증된 값 (조정 적용)
        verified_carbon = adjustments.get('carbon_savings_kg', request.measurement.carbon_savings_kg) if adjustments else request.measurement.carbon_savings_kg
        verified_dc = adjustments.get('dc_units', request.measurement.dc_units) if adjustments else request.measurement.dc_units
        verified_confidence = adjustments.get('confidence_score', request.measurement.confidence_score) if adjustments else request.measurement.confidence_score

        # 검증 결과 생성
        result_id = self._generate_result_id()
        result = VerificationResult(
            result_id=result_id,
            request_id=request_id,
            measurement_id=request.measurement.measurement_id,
            approved=approved,
            confidence_score_verified=verified_confidence,
            carbon_savings_verified=verified_carbon,
            dc_units_verified=verified_dc,
            verification_method="committee_review",
            verified_by=reviewer_id,
            verified_at=datetime.now().isoformat(),
            checklist_results=checklist_results,
            evidence_verified=checklist_results['evidence_check'],
            data_integrity_verified=checklist_results['data_integrity_check'],
            calculation_verified=checklist_results['calculation_check'],
            verifier_comments=comments
        )

        # 요청 상태 업데이트
        if approved:
            request.status = VerificationStatus.APPROVED
            request.approved_by = reviewer_id
            request.approved_at = datetime.now().isoformat()
            request.measurement.status = MeasurementStatus.VERIFIED

            # 검증된 값으로 업데이트
            request.measurement.carbon_savings_kg = verified_carbon
            request.measurement.dc_units = verified_dc
            request.measurement.confidence_score = verified_confidence

        else:
            request.status = VerificationStatus.REJECTED
            request.rejection_reason = comments

        # 코멘트 추가
        request.comments.append({
            'timestamp': datetime.now().isoformat(),
            'author': reviewer_id,
            'content': comments,
            'decision': 'approved' if approved else 'rejected'
        })

        request.verification_result = result.__dict__

        # DB 저장
        if self.db:
            self._update_verification_request(request)
            self._save_verification_result(result)

        logger.info(f"Verification completed: {request_id}, Approved: {approved}")

        return result

    def request_resubmission(self, request_id: str, reviewer_id: str,
                            feedback: str) -> bool:
        """
        재제출 요청

        Args:
            request_id: 요청 ID
            reviewer_id: 검토자 ID
            feedback: 재제출 요청 사유

        Returns:
            성공 여부
        """
        request = self._get_verification_request(request_id)
        if not request:
            return False

        request.status = VerificationStatus.RESUBMISSION_REQUIRED
        request.rejection_reason = feedback

        request.comments.append({
            'timestamp': datetime.now().isoformat(),
            'author': reviewer_id,
            'content': feedback,
            'decision': 'resubmission_required'
        })

        if self.db:
            self._update_verification_request(request)

        logger.info(f"Resubmission requested for {request_id}")

        return True

    def escalate_to_senior_committee(self, request_id: str, reason: str) -> bool:
        """
        상위 위원회로 에스컬레이션

        Args:
            request_id: 요청 ID
            reason: 에스컬레이션 사유

        Returns:
            성공 여부
        """
        request = self._get_verification_request(request_id)
        if not request:
            return False

        request.status = VerificationStatus.ESCALATED
        request.priority = 2  # 긴급으로 변경

        request.comments.append({
            'timestamp': datetime.now().isoformat(),
            'author': 'system',
            'content': f"Escalated: {reason}",
            'decision': 'escalated'
        })

        # 상위 위원(APPROVER 또는 ADMIN)에게 재배정
        senior_member = self._find_senior_committee_member()
        if senior_member:
            request.assigned_to = senior_member.member_id
            request.assigned_at = datetime.now().isoformat()

        if self.db:
            self._update_verification_request(request)

        logger.info(f"Request {request_id} escalated to senior committee")

        return True

    def get_pending_verifications(self, member_id: Optional[str] = None,
                                 priority: Optional[int] = None) -> List[VerificationRequest]:
        """
        대기 중인 검증 목록 조회

        Args:
            member_id: 특정 위원의 목록 (None이면 전체)
            priority: 우선순위 필터

        Returns:
            검증 요청 목록
        """
        # DB에서 조회
        filters = {
            'status': [VerificationStatus.PENDING, VerificationStatus.IN_REVIEW]
        }

        if member_id:
            filters['assigned_to'] = member_id

        if priority is not None:
            filters['priority'] = priority

        # 실제 구현에서는 DB 쿼리
        logger.info(f"Fetching pending verifications with filters: {filters}")

        return []  # Placeholder

    def get_verification_statistics(self, start_date: str, end_date: str) -> Dict:
        """
        검증 통계

        Args:
            start_date: 시작일
            end_date: 종료일

        Returns:
            통계 정보
        """
        # DB에서 통계 조회
        stats = {
            'total_requests': 0,
            'approved': 0,
            'rejected': 0,
            'pending': 0,
            'average_review_time_hours': 0.0,
            'auto_approved_count': 0,
            'by_reviewer': {},
            'by_priority': {}
        }

        return stats

    def _check_auto_approve_eligible(self, measurement: MeasurementData) -> bool:
        """자동 승인 가능 여부 확인"""
        conditions = [
            measurement.confidence_score >= self.auto_approve_threshold['confidence_score'],
            len(measurement.evidences) >= self.auto_approve_threshold['evidence_count'],
            measurement.carbon_savings_kg <= self.auto_approve_threshold['carbon_savings_max']
        ]

        return all(conditions)

    def _auto_approve(self, request: VerificationRequest) -> Dict:
        """자동 승인 처리"""
        result = {
            'approved': True,
            'method': 'auto',
            'confidence_verified': request.measurement.confidence_score,
            'carbon_verified': request.measurement.carbon_savings_kg,
            'dc_verified': request.measurement.dc_units,
            'approved_at': datetime.now().isoformat()
        }

        return result

    def _assign_to_committee_member(self, measurement: MeasurementData,
                                   priority: int) -> Optional[CommitteeMember]:
        """위원회 위원에게 자동 배정"""
        # 활동 유형에 맞는 전문가 찾기
        activity_type = measurement.activity.activity_type.value

        # 가용한 위원 중 워크로드가 가장 적은 사람 선택
        available_members = [m for m in self.committee_members
                           if m.active and m.role in [CommitteeRole.REVIEWER, CommitteeRole.APPROVER]]

        if not available_members:
            return None

        # 간단한 라운드 로빈 (실제로는 워크로드, 전문 분야 고려)
        return available_members[0] if available_members else None

    def _perform_verification_checklist(self, measurement: MeasurementData) -> Dict:
        """검증 체크리스트 수행"""
        checklist = {
            'evidence_check': len(measurement.evidences) >= 2,
            'data_integrity_check': measurement.data_hash != "",
            'calculation_check': measurement.carbon_savings_kg > 0,
            'confidence_check': measurement.confidence_score >= 40,
            'timestamp_check': measurement.measurement_timestamp != "",
            'activity_details_check': measurement.activity.product_name != ""
        }

        return checklist

    def _find_senior_committee_member(self) -> Optional[CommitteeMember]:
        """상위 위원 찾기"""
        senior_members = [m for m in self.committee_members
                         if m.active and m.role in [CommitteeRole.APPROVER, CommitteeRole.ADMIN]]

        return senior_members[0] if senior_members else None

    def _generate_request_id(self) -> str:
        """검증 요청 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"VRQ-{timestamp}"

    def _generate_result_id(self) -> str:
        """검증 결과 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"VRS-{timestamp}"

    def _get_verification_request(self, request_id: str) -> Optional[VerificationRequest]:
        """검증 요청 조회 (DB)"""
        # 실제 구현에서는 DB에서 조회
        return None

    def _get_committee_member(self, member_id: str) -> Optional[CommitteeMember]:
        """위원 정보 조회"""
        for member in self.committee_members:
            if member.member_id == member_id:
                return member
        return None

    def _save_verification_request(self, request: VerificationRequest):
        """검증 요청 저장 (DB)"""
        if not self.db:
            return
        # DB INSERT 쿼리 실행
        logger.info(f"Saving verification request: {request.request_id}")

    def _update_verification_request(self, request: VerificationRequest):
        """검증 요청 업데이트 (DB)"""
        if not self.db:
            return
        # DB UPDATE 쿼리 실행
        logger.info(f"Updating verification request: {request.request_id}")

    def _save_verification_result(self, result: VerificationResult):
        """검증 결과 저장 (DB)"""
        if not self.db:
            return
        # DB INSERT 쿼리 실행
        logger.info(f"Saving verification result: {result.result_id}")


# 사용 예시
if __name__ == "__main__":
    from mrv_measurement_module import MRVMeasurementModule, Evidence, EvidenceType
    from carbon_calculation_engine import CarbonActivity, ActivityType

    # 워크플로우 초기화
    workflow = CommitteeVerificationWorkflow()

    # 위원회 위원 추가
    workflow.committee_members = [
        CommitteeMember(
            member_id="committee001",
            name="김환경",
            role=CommitteeRole.REVIEWER,
            email="kim@example.com",
            wallet_address="ALGO_WALLET_ADDRESS",
            specialization=["agriculture", "local_food"]
        ),
        CommitteeMember(
            member_id="committee002",
            name="이탄소",
            role=CommitteeRole.APPROVER,
            email="lee@example.com",
            wallet_address="ALGO_WALLET_ADDRESS2",
            specialization=["renewable_energy", "waste_reduction"]
        )
    ]

    # 측정 데이터 준비
    mrv_module = MRVMeasurementModule()

    activity = CarbonActivity(
        activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
        user_id="user123",
        product_name="유기농 상추",
        quantity=3.0,
        origin_region="경기도",
        destination_region="서울시",
        farming_method="organic",
        transport_method="truck_small",
        packaging_type="paper",
        activity_date=datetime.now().isoformat()
    )

    evidences = [
        Evidence(
            evidence_type=EvidenceType.RECEIPT,
            file_path="/uploads/receipt.jpg",
            description="구매 영수증"
        )
    ]

    measurement = mrv_module.measure_activity(activity, "manual", evidences)

    # 검증 요청 제출
    request = workflow.submit_for_verification(measurement, "user123", priority=0)

    print(f"검증 요청 제출: {request.request_id}")
    print(f"상태: {request.status.value}")
    print(f"배정: {request.assigned_to or '미배정'}")
