# -*- coding: utf-8 -*-
"""
MRV (Measurement, Reporting, Verification) 측정 모듈
탄소 감축 활동의 정확한 측정 및 데이터 수집
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import hashlib
from enum import Enum

from .carbon_calculation_engine import (
    CarbonCalculationEngine,
    CarbonActivity,
    ActivityType
)

logger = logging.getLogger(__name__)


class MeasurementStatus(Enum):
    """측정 상태"""
    PENDING = "pending"  # 측정 대기
    MEASURED = "measured"  # 측정 완료
    VERIFIED = "verified"  # 검증 완료
    REJECTED = "rejected"  # 반려됨


class EvidenceType(Enum):
    """증빙 자료 유형"""
    RECEIPT = "receipt"  # 영수증
    PHOTO = "photo"  # 사진
    GPS = "gps"  # GPS 위치
    SENSOR_DATA = "sensor_data"  # 센서 데이터
    INVOICE = "invoice"  # 거래명세서
    CERTIFICATE = "certificate"  # 인증서
    METER_READING = "meter_reading"  # 계량기 수치


@dataclass
class Evidence:
    """증빙 자료"""
    evidence_type: EvidenceType
    file_path: Optional[str] = None
    data: Optional[Dict] = None
    description: str = ""
    timestamp: str = ""
    hash: str = ""  # 위조 방지 해시


@dataclass
class MeasurementData:
    """측정 데이터"""
    measurement_id: str
    user_id: str
    activity: CarbonActivity

    # 측정 결과
    carbon_savings_kg: float
    dc_units: float
    esg_gold_amount: float

    # 측정 세부사항
    measurement_method: str  # manual, automated, sensor
    measurement_timestamp: str
    measurement_location: Optional[Dict] = None  # GPS 좌표

    # 증빙 자료
    evidences: List[Evidence] = None

    # 상태
    status: MeasurementStatus = MeasurementStatus.PENDING
    confidence_score: float = 0.0  # 0-100, 측정 신뢰도

    # 메타데이터
    data_hash: str = ""  # 데이터 무결성 해시
    metadata: Dict = None

    def __post_init__(self):
        if self.evidences is None:
            self.evidences = []
        if self.metadata is None:
            self.metadata = {}


class MRVMeasurementModule:
    """MRV 측정 모듈"""

    def __init__(self, carbon_engine: CarbonCalculationEngine = None):
        """
        Args:
            carbon_engine: 탄소 계산 엔진
        """
        self.carbon_engine = carbon_engine or CarbonCalculationEngine()

        # 측정 방법별 신뢰도 가중치
        self.confidence_weights = {
            'sensor': 0.95,  # 센서 자동 측정
            'automated': 0.85,  # 자동화된 측정
            'manual_verified': 0.75,  # 검증된 수동 측정
            'manual': 0.60,  # 일반 수동 측정
            'self_reported': 0.40  # 자가 보고
        }

    def measure_activity(self, activity: CarbonActivity,
                        measurement_method: str = "manual",
                        evidences: List[Evidence] = None,
                        location: Dict = None) -> MeasurementData:
        """
        탄소 감축 활동 측정

        Args:
            activity: 탄소 감축 활동
            measurement_method: 측정 방법
            evidences: 증빙 자료 목록
            location: GPS 위치 정보

        Returns:
            MeasurementData: 측정 데이터
        """
        try:
            # 1. 탄소 발자국 계산
            carbon_result = self.carbon_engine.calculate_carbon_footprint(activity)

            # 2. 측정 ID 생성
            measurement_id = self._generate_measurement_id(activity.user_id)

            # 3. 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(
                measurement_method=measurement_method,
                evidences=evidences or [],
                activity=activity
            )

            # 4. 측정 데이터 생성
            measurement = MeasurementData(
                measurement_id=measurement_id,
                user_id=activity.user_id,
                activity=activity,
                carbon_savings_kg=carbon_result.carbon_savings,
                dc_units=carbon_result.digital_carbon_units,
                esg_gold_amount=carbon_result.esg_gold_actual,
                measurement_method=measurement_method,
                measurement_timestamp=datetime.now().isoformat(),
                measurement_location=location,
                evidences=evidences or [],
                status=MeasurementStatus.MEASURED,
                confidence_score=confidence_score
            )

            # 5. 데이터 해시 생성 (무결성 보장)
            measurement.data_hash = self._generate_data_hash(measurement)

            # 6. 메타데이터 추가
            measurement.metadata = {
                'carbon_breakdown': {
                    'transport': carbon_result.transport_emissions,
                    'production': carbon_result.production_emissions,
                    'packaging': carbon_result.packaging_emissions,
                    'total': carbon_result.total_emissions,
                    'baseline': carbon_result.baseline_emissions
                },
                'reduction_percentage': carbon_result.reduction_percentage,
                'pam_tokens': carbon_result.reward_amount,
                'measurement_version': '1.0'
            }

            logger.info(f"Activity measured: {measurement_id}, "
                       f"Carbon savings: {carbon_result.carbon_savings} kg, "
                       f"Confidence: {confidence_score}%")

            return measurement

        except Exception as e:
            logger.error(f"Failed to measure activity: {e}")
            raise

    def validate_measurement(self, measurement: MeasurementData) -> Tuple[bool, List[str]]:
        """
        측정 데이터 검증

        Args:
            measurement: 측정 데이터

        Returns:
            (유효성, 검증 메시지 목록)
        """
        issues = []

        # 1. 필수 필드 확인
        if not measurement.measurement_id:
            issues.append("측정 ID가 없습니다")
        if not measurement.user_id:
            issues.append("사용자 ID가 없습니다")
        if measurement.carbon_savings_kg <= 0:
            issues.append("탄소 절약량이 0 이하입니다")

        # 2. 신뢰도 점수 확인
        if measurement.confidence_score < 40:
            issues.append(f"신뢰도 점수가 너무 낮습니다: {measurement.confidence_score}%")

        # 3. 증빙 자료 확인
        if not measurement.evidences or len(measurement.evidences) == 0:
            issues.append("증빙 자료가 없습니다")

        # 4. 데이터 해시 검증
        expected_hash = self._generate_data_hash(measurement)
        if measurement.data_hash != expected_hash:
            issues.append("데이터 무결성 검증 실패")

        # 5. 활동 데이터 합리성 확인
        if measurement.activity.quantity <= 0:
            issues.append("활동 수량이 0 이하입니다")

        if measurement.activity.quantity > 10000:  # 비정상적으로 큰 값
            issues.append(f"활동 수량이 비정상적으로 큽니다: {measurement.activity.quantity}")

        # 6. 날짜 검증
        try:
            activity_date = datetime.fromisoformat(measurement.activity.activity_date)
            measurement_date = datetime.fromisoformat(measurement.measurement_timestamp)

            # 미래 날짜 확인
            if activity_date > datetime.now():
                issues.append("활동 날짜가 미래입니다")

            # 측정이 활동보다 이전인지 확인
            if measurement_date < activity_date:
                issues.append("측정 시간이 활동 시간보다 이전입니다")

            # 너무 오래된 활동
            if (datetime.now() - activity_date).days > 30:
                issues.append("활동 날짜가 30일 이상 지났습니다")

        except Exception as e:
            issues.append(f"날짜 형식 오류: {e}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def add_evidence(self, measurement: MeasurementData,
                    evidence_type: EvidenceType,
                    file_path: str = None,
                    data: Dict = None,
                    description: str = "") -> Evidence:
        """
        측정 데이터에 증빙 자료 추가

        Args:
            measurement: 측정 데이터
            evidence_type: 증빙 유형
            file_path: 파일 경로 (이미지, PDF 등)
            data: 구조화된 데이터 (JSON)
            description: 설명

        Returns:
            Evidence: 추가된 증빙 자료
        """
        # 증빙 자료 생성
        evidence = Evidence(
            evidence_type=evidence_type,
            file_path=file_path,
            data=data,
            description=description,
            timestamp=datetime.now().isoformat()
        )

        # 해시 생성
        evidence.hash = self._generate_evidence_hash(evidence)

        # 측정 데이터에 추가
        measurement.evidences.append(evidence)

        # 신뢰도 점수 재계산
        measurement.confidence_score = self._calculate_confidence_score(
            measurement_method=measurement.measurement_method,
            evidences=measurement.evidences,
            activity=measurement.activity
        )

        # 데이터 해시 업데이트
        measurement.data_hash = self._generate_data_hash(measurement)

        logger.info(f"Evidence added to measurement {measurement.measurement_id}: "
                   f"{evidence_type.value}")

        return evidence

    def batch_measure_activities(self, activities: List[Tuple[CarbonActivity, str, List[Evidence]]]) -> List[MeasurementData]:
        """
        여러 활동을 일괄 측정

        Args:
            activities: [(CarbonActivity, measurement_method, evidences), ...]

        Returns:
            List[MeasurementData]: 측정 데이터 목록
        """
        measurements = []

        for activity, method, evidences in activities:
            try:
                measurement = self.measure_activity(
                    activity=activity,
                    measurement_method=method,
                    evidences=evidences
                )
                measurements.append(measurement)
            except Exception as e:
                logger.error(f"Failed to measure activity for user {activity.user_id}: {e}")

        return measurements

    def get_measurement_statistics(self, measurements: List[MeasurementData]) -> Dict:
        """
        측정 데이터 통계

        Args:
            measurements: 측정 데이터 목록

        Returns:
            통계 정보
        """
        if not measurements:
            return {}

        total_carbon = sum(m.carbon_savings_kg for m in measurements)
        total_dc = sum(m.dc_units for m in measurements)
        avg_confidence = sum(m.confidence_score for m in measurements) / len(measurements)

        # 측정 방법별 통계
        method_stats = {}
        for m in measurements:
            method = m.measurement_method
            if method not in method_stats:
                method_stats[method] = {'count': 0, 'total_carbon': 0.0}
            method_stats[method]['count'] += 1
            method_stats[method]['total_carbon'] += m.carbon_savings_kg

        # 상태별 통계
        status_stats = {}
        for m in measurements:
            status = m.status.value
            status_stats[status] = status_stats.get(status, 0) + 1

        return {
            'total_measurements': len(measurements),
            'total_carbon_savings_kg': round(total_carbon, 2),
            'total_dc_units': round(total_dc, 2),
            'average_confidence_score': round(avg_confidence, 2),
            'by_method': method_stats,
            'by_status': status_stats,
            'high_confidence_count': sum(1 for m in measurements if m.confidence_score >= 80),
            'low_confidence_count': sum(1 for m in measurements if m.confidence_score < 60)
        }

    def _calculate_confidence_score(self, measurement_method: str,
                                    evidences: List[Evidence],
                                    activity: CarbonActivity) -> float:
        """
        신뢰도 점수 계산

        Args:
            measurement_method: 측정 방법
            evidences: 증빙 자료 목록
            activity: 활동 정보

        Returns:
            신뢰도 점수 (0-100)
        """
        # 기본 점수 (측정 방법별)
        base_score = self.confidence_weights.get(measurement_method, 0.5) * 100

        # 증빙 자료 보너스
        evidence_bonus = 0
        if len(evidences) >= 1:
            evidence_bonus += 5
        if len(evidences) >= 2:
            evidence_bonus += 5
        if len(evidences) >= 3:
            evidence_bonus += 10

        # 증빙 유형별 추가 보너스
        evidence_types = {e.evidence_type for e in evidences}
        if EvidenceType.RECEIPT in evidence_types:
            evidence_bonus += 5
        if EvidenceType.GPS in evidence_types:
            evidence_bonus += 5
        if EvidenceType.SENSOR_DATA in evidence_types:
            evidence_bonus += 10
        if EvidenceType.CERTIFICATE in evidence_types:
            evidence_bonus += 10

        # 활동 유형별 보정
        activity_modifier = 1.0
        if activity.farming_method == "organic":
            activity_modifier += 0.05
        if activity.packaging_type in ["reusable", "biodegradable"]:
            activity_modifier += 0.03

        final_score = min(100, (base_score + evidence_bonus) * activity_modifier)
        return round(final_score, 2)

    def _generate_measurement_id(self, user_id: str) -> str:
        """측정 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"MRV-{user_id[:8]}-{timestamp}"

    def _generate_data_hash(self, measurement: MeasurementData) -> str:
        """
        측정 데이터 해시 생성 (무결성 보장)

        Args:
            measurement: 측정 데이터

        Returns:
            SHA256 해시
        """
        # 해시 계산에 포함할 핵심 데이터
        hash_data = {
            'measurement_id': measurement.measurement_id,
            'user_id': measurement.user_id,
            'activity_type': measurement.activity.activity_type.value,
            'carbon_savings_kg': measurement.carbon_savings_kg,
            'dc_units': measurement.dc_units,
            'measurement_timestamp': measurement.measurement_timestamp,
            'product_name': measurement.activity.product_name,
            'quantity': measurement.activity.quantity,
            'origin': measurement.activity.origin_region,
            'destination': measurement.activity.destination_region
        }

        # JSON 직렬화 후 해시
        json_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _generate_evidence_hash(self, evidence: Evidence) -> str:
        """
        증빙 자료 해시 생성

        Args:
            evidence: 증빙 자료

        Returns:
            SHA256 해시
        """
        hash_data = {
            'evidence_type': evidence.evidence_type.value,
            'file_path': evidence.file_path or '',
            'data': evidence.data or {},
            'timestamp': evidence.timestamp
        }

        json_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def export_measurement_report(self, measurement: MeasurementData) -> Dict:
        """
        측정 리포트 생성 (JSON)

        Args:
            measurement: 측정 데이터

        Returns:
            리포트 데이터
        """
        return {
            'report_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'measurement_id': measurement.measurement_id,
            'user_id': measurement.user_id,

            'measurement_summary': {
                'carbon_savings_kg': measurement.carbon_savings_kg,
                'dc_units': measurement.dc_units,
                'esg_gold_amount': measurement.esg_gold_amount,
                'confidence_score': measurement.confidence_score,
                'status': measurement.status.value
            },

            'activity_details': {
                'type': measurement.activity.activity_type.value,
                'product': measurement.activity.product_name,
                'quantity': measurement.activity.quantity,
                'origin': measurement.activity.origin_region,
                'destination': measurement.activity.destination_region,
                'farming_method': measurement.activity.farming_method,
                'transport_method': measurement.activity.transport_method,
                'packaging_type': measurement.activity.packaging_type,
                'activity_date': measurement.activity.activity_date
            },

            'measurement_info': {
                'method': measurement.measurement_method,
                'timestamp': measurement.measurement_timestamp,
                'location': measurement.measurement_location
            },

            'evidences': [
                {
                    'type': e.evidence_type.value,
                    'description': e.description,
                    'timestamp': e.timestamp,
                    'hash': e.hash
                } for e in measurement.evidences
            ],

            'metadata': measurement.metadata,
            'data_hash': measurement.data_hash
        }


# 사용 예시
if __name__ == "__main__":
    from carbon_calculation_engine import CarbonActivity, ActivityType

    # MRV 모듈 초기화
    mrv_module = MRVMeasurementModule()

    # 활동 데이터
    activity = CarbonActivity(
        activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
        user_id="user123",
        product_name="유기농 토마토",
        quantity=5.0,
        origin_region="경기도",
        destination_region="서울시",
        farming_method="organic",
        transport_method="truck_small",
        packaging_type="paper",
        activity_date=datetime.now().isoformat()
    )

    # 증빙 자료
    evidences = [
        Evidence(
            evidence_type=EvidenceType.RECEIPT,
            file_path="/uploads/receipt_20240115.jpg",
            description="구매 영수증",
            timestamp=datetime.now().isoformat()
        ),
        Evidence(
            evidence_type=EvidenceType.GPS,
            data={'lat': 37.5665, 'lng': 126.9780},
            description="거래 위치",
            timestamp=datetime.now().isoformat()
        )
    ]

    # 측정
    measurement = mrv_module.measure_activity(
        activity=activity,
        measurement_method="manual_verified",
        evidences=evidences,
        location={'lat': 37.5665, 'lng': 126.9780}
    )

    print("=== MRV 측정 결과 ===")
    print(f"측정 ID: {measurement.measurement_id}")
    print(f"탄소 절약: {measurement.carbon_savings_kg} kg CO₂")
    print(f"DC 획득: {measurement.dc_units} DC")
    print(f"신뢰도 점수: {measurement.confidence_score}%")
    print(f"데이터 해시: {measurement.data_hash[:16]}...")

    # 검증
    is_valid, issues = mrv_module.validate_measurement(measurement)
    print(f"\n검증 결과: {'통과' if is_valid else '실패'}")
    if issues:
        print("문제점:")
        for issue in issues:
            print(f"  - {issue}")

    # 리포트 생성
    report = mrv_module.export_measurement_report(measurement)
    print(f"\n리포트 생성 완료: {report['report_version']}")
